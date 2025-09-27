import os
import paramiko
import configparser
import logging
import socket
import sys
import hashlib
import argparse
import datetime
from stat import S_ISREG

def setup_logging(log_file, debug=False):
    """Настройка системы логирования с опциональным debug-режимом"""
    try:
        log_file = os.path.expanduser(log_file)
        log_file = os.path.abspath(log_file)
        log_dir = os.path.dirname(log_file)
        
        if log_dir and log_dir != "." and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        level = logging.DEBUG if debug else logging.INFO
        
        logger = logging.getLogger()
        logger.setLevel(level)
        
        # Форматтер для логов
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        
        # Обработчик для файла
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Обработчик для консоли
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        logger.addHandler(console_handler)
        
        logging.info(f"Logging initialized to: {log_file}")
        if debug:
            logging.debug("DEBUG MODE ENABLED")
        return True
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to setup logging: {str(e)}")
        return False

def compare_files(local_path, sftp, remote_path):
    """Сравнивает содержимое локального и удаленного файла"""
    try:
        # Сравниваем размеры файлов
        local_size = os.path.getsize(local_path)
        remote_attr = sftp.stat(remote_path)
        if local_size != remote_attr.st_size:
            return False
        
        # Сравниваем хеши содержимого
        with open(local_path, 'rb') as f:
            local_hash = hashlib.sha256(f.read()).hexdigest()
        
        with sftp.open(remote_path, 'rb') as f:
            remote_hash = hashlib.sha256(f.read()).hexdigest()
            
        return local_hash == remote_hash
    except Exception as e:
        logging.error(f"Error comparing files: {str(e)}")
        return False

def is_cert_update_needed(local_cert_file, local_privkey_file, sftp, remote_cert_file, remote_privkey_file):
    """Определяет, нужно ли обновлять сертификаты"""
    # Если локальные файлы отсутствуют - обновление обязательно
    if not os.path.exists(local_cert_file) or not os.path.exists(local_privkey_file):
        return True
    
    # Проверяем, изменились ли файлы
    cert_changed = not compare_files(local_cert_file, sftp, remote_cert_file)
    privkey_changed = not compare_files(local_privkey_file, sftp, remote_privkey_file)
    
    return cert_changed or privkey_changed

def resolve_hostname(hostname):
    """Разрешение DNS имени в IP-адрес"""
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        return "unresolved"

def clean_config_value(value):
    """Очистка значений конфига от комментариев и лишних пробелов"""
    if ';' in value:
        value = value.split(';')[0]
    if '#' in value:
        value = value.split('#')[0]
    return value.strip()

def load_ssh_key(ssh_key, use_ssh_agent, key_password=None):
    """Загрузка SSH-ключа с поддержкой защищенных ключей и SSH-агента"""
    if use_ssh_agent:
        try:
            logging.debug("Trying to use SSH agent for authentication")
            agent = paramiko.Agent()
            agent_keys = agent.get_keys()
            
            if not agent_keys:
                logging.warning("SSH agent is enabled but no keys available")
                return None
                
            logging.debug(f"Using first available key from SSH agent: {agent_keys[0].get_name()}")
            return agent_keys[0]
        except Exception as e:
            logging.error(f"SSH agent error: {str(e)}")
            return None

    if not os.path.exists(ssh_key):
        raise FileNotFoundError(f"SSH key not found: {ssh_key}")
    
    # Пробуем разные типы ключей
    key_types = [
        ('RSA', paramiko.RSAKey),
        ('ECDSA', paramiko.ECDSAKey),
        ('Ed25519', paramiko.Ed25519Key)
    ]
    
    last_error = None
    for key_name, key_class in key_types:
        try:
            if key_password:
                logging.warning("Using key password from config - SECURITY WARNING")
                return key_class.from_private_key_file(ssh_key, password=key_password)
            return key_class.from_private_key_file(ssh_key)
        except (paramiko.ssh_exception.PasswordRequiredException, 
                paramiko.ssh_exception.SSHException) as e:
            last_error = e
            logging.debug(f"Failed to load as {key_name} key: {str(e)}")
    
    # Если все попытки не удались
    raise last_error or Exception("Failed to load SSH key")

def main():
    """Основная функция скрипта"""
    # Парсинг аргументов командной строки
    parser = argparse.ArgumentParser(description='SSL Certificate Updater')
    parser.add_argument('-c', '--config', default='config.ini', 
                       help='Path to configuration file (default: config.ini)')
    parser.add_argument('-d', '--debug', action='store_true', 
                       help='Enable debug output and detailed logging')
    args = parser.parse_args()
    
    config_file = args.config
    print(f"Starting SSL Certificate Updater with config: {config_file}")
    
    if not os.path.exists(config_file):
        print(f"ERROR: Configuration file not found: {config_file}")
        return
    
    config = configparser.ConfigParser()
    try:
        config.read(config_file)
    except Exception as e:
        print(f"ERROR: Failed to read config file: {str(e)}")
        return
    
    # Настройка логирования
    raw_log_file = config.get('LOGGING', 'log_file', fallback='cert_updater.log')
    log_file = os.path.expanduser(raw_log_file)
    if not setup_logging(log_file, args.debug):
        print("CRITICAL: Logging setup failed. Exiting.")
        return
    
    # Запись о начале обновления
    logging.info("====== Start Update ======")
    logging.info(f"Using configuration file: {os.path.abspath(config_file)}")
    
    # Параметры SSH
    ssh_host = config.get('SSH', 'host', fallback='localhost')
    ssh_port = config.getint('SSH', 'port', fallback=22)
    ssh_user = config.get('SSH', 'username', fallback='root')
    
    raw_ssh_key = config.get('SSH', 'private_key', fallback='~/.ssh/id_rsa')
    ssh_key = os.path.expanduser(raw_ssh_key)
    
    # Обработка булевых значений
    raw_use_ssh_agent = config.get('SSH', 'use_ssh_agent', fallback='false')
    clean_use_ssh_agent = clean_config_value(raw_use_ssh_agent).lower()
    use_ssh_agent = clean_use_ssh_agent in ('yes', 'true', '1', 'on')
    
    raw_key_password = config.get('SSH', 'key_password', fallback='')
    key_password = clean_config_value(raw_key_password) or None
    
    # Домены и пути
    remote_base = config.get('PATHS', 'remote_cert_path', fallback='/www/server/panel/vhost/letsencrypt')
    
    # Имена файлов на сервере
    remote_name_cert = config.get('PATHS', 'name_cert', fallback='fullchain.pem')
    remote_name_privkey = config.get('PATHS', 'name_privkey', fallback='privkey.pem')
    
    # Локальные настройки
    raw_local_base = config.get('LOCAL', 'base_path', fallback='./ssl')
    local_base = os.path.expanduser(raw_local_base)
    
    # Имена файлов локально
    local_name_cert = config.get('LOCAL', 'name_cert', fallback='fullchain.pem')
    local_name_privkey = config.get('LOCAL', 'name_privkey', fallback='privkey.pem')
    
    # Обработка параметра name_dir (по умолчанию True)
    raw_name_dir = config.get('LOCAL', 'name_dir', fallback='true')
    clean_name_dir = clean_config_value(raw_name_dir).lower()
    name_dir = clean_name_dir in ('true', 'yes', '1', 'on')
    
    logging.info(f"Local storage settings: name_dir={name_dir}, cert_file={local_name_cert}, privkey_file={local_name_privkey}")
    logging.info(f"Remote file names: cert_file={remote_name_cert}, privkey_file={remote_name_privkey}")
    
    # Сбор доменов
    domains = []
    if config.has_section('DOMAINS'):
        for key in config['DOMAINS']:
            if key == 'domains':
                continue
            
            domain = key.strip()
            raw_prefix = config['DOMAINS'][key]
            prefix = clean_config_value(raw_prefix)
            domains.append((domain, prefix))
    
    if not domains:
        domains_str = config.get('DOMAINS', 'domains', fallback='') if config.has_section('DOMAINS') else ''
        if domains_str:
            for domain in domains_str.split(','):
                domain = domain.strip()
                if domain:
                    domains.append((domain, ''))
    
    if not domains:
        logging.warning("No domains configured for processing")
        logging.info("======= End Update =======")
        return
    
    # Обработка name_dir=false
    if not name_dir:
        if len(domains) > 1:
            logging.warning(f"Only first domain will be processed. Total domains: {len(domains)}")
            logging.warning("To process all domains, set NAME_DIR to TRUE in [LOCAL] section")
            domains = [domains[0]]  # Оставляем только первый домен
    
    logging.info(f"Processing {len(domains)} domains")
    
    # Статистика выполнения
    stats = {'total': 0, 'updated': 0, 'skipped': 0, 'errors': 0, 'not_found': 0}
    
    try:
        logging.info(f"Connecting to {ssh_user}@{ssh_host}:{ssh_port}")
        
        # Загрузка SSH-ключа
        private_key = load_ssh_key(ssh_key, use_ssh_agent, key_password)
        if not private_key:
            raise Exception("Failed to load SSH credentials")
        
        # Создание подключения
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((ssh_host, ssh_port))
        
        transport = paramiko.Transport(sock)
        transport.banner_timeout = 10
        transport.handshake_timeout = 10
        transport.connect(username=ssh_user, pkey=private_key)
        sftp = paramiko.SFTPClient.from_transport(transport)
        
        logging.info(f"Successfully connected to {ssh_user}@{ssh_host}:{ssh_port}")
        
        # Обработка доменов
        for domain, prefix in domains:
            stats['total'] += 1
            server_folder = f"{prefix}.{domain}" if prefix else domain
            remote_path = os.path.join(remote_base, server_folder)
            
            # Формирование путей на сервере
            remote_cert_file = os.path.join(remote_path, remote_name_cert)
            remote_privkey_file = os.path.join(remote_path, remote_name_privkey)
            
            # Формирование локальных путей
            if name_dir:
                # Создаем подпапку для домена
                local_path = os.path.expanduser(os.path.join(local_base, domain))
                local_cert_file = os.path.join(local_path, local_name_cert)
                local_privkey_file = os.path.join(local_path, local_name_privkey)
            else:
                # Сохраняем файлы напрямую в base_path
                local_path = os.path.expanduser(local_base)
                local_cert_file = os.path.join(local_path, local_name_cert)
                local_privkey_file = os.path.join(local_path, local_name_privkey)
            
            logging.debug(f"Domain: {domain}")
            logging.debug(f"Remote cert: {remote_cert_file}")
            logging.debug(f"Remote privkey: {remote_privkey_file}")
            logging.debug(f"Local cert: {local_cert_file}")
            logging.debug(f"Local privkey: {local_privkey_file}")
            
            try:
                # Проверка существования удаленного пути
                try:
                    sftp.stat(remote_path)
                except FileNotFoundError:
                    logging.error(f"[{domain}] Server path not found: {remote_path}")
                    stats['not_found'] += 1
                    continue
                
                # Проверка необходимости обновления
                if os.path.exists(local_cert_file) and os.path.exists(local_privkey_file):
                    if is_cert_update_needed(local_cert_file, local_privkey_file, sftp, remote_cert_file, remote_privkey_file):
                        logging.info(f"[{domain}] Certificates need update")
                    else:
                        logging.info(f"[{domain}] Certificates are up-to-date")
                        stats['skipped'] += 1
                        continue
                else:
                    logging.info(f"[{domain}] New certificate, will download")
                
                # Создание локальной директории
                if local_path and not os.path.exists(local_path):
                    os.makedirs(local_path, exist_ok=True)
                
                # Загрузка сертификатов
                for remote_file, local_file in [
                    (remote_cert_file, local_cert_file),
                    (remote_privkey_file, local_privkey_file)
                ]:
                    try:
                        sftp.get(remote_file, local_file)
                        # Установка правильных прав доступа
                        os.chmod(local_file, 0o600)
                        logging.debug(f"[{domain}] Downloaded: {os.path.basename(local_file)}")
                    except Exception as e:
                        logging.error(f"[{domain}] Error downloading {os.path.basename(local_file)}: {str(e)}")
                        raise
                
                logging.info(f"[{domain}] Certificates updated successfully")
                stats['updated'] += 1
                
            except Exception as e:
                logging.error(f"[{domain}] Error: {str(e)}")
                stats['errors'] += 1
                
    except Exception as e:
        logging.error(f"Connection failed: {str(e)}")
        stats['errors'] += len(domains)
    finally:
        if 'sftp' in locals():
            sftp.close()
        if 'transport' in locals():
            transport.close()
        if 'sock' in locals():
            sock.close()
    
    # Вывод статистики с правильным форматированием
    logging.info("===== Update Summary =====")
    logging.info(f"Total domains processed: {stats['total']}")
    logging.info(f"Successfully updated: {stats['updated']}")
    logging.info(f"Skipped (up-to-date): {stats['skipped']}")
    logging.info(f"Not found on server: {stats['not_found']}")
    logging.info(f"Errors: {stats['errors']}")
    logging.info("==========================")
    
    # Запись о завершении обновления
    logging.info("======= End Update =======")
    
    # Вывод статистики в консоль
    print("\nUpdate Summary:")
    print(f"Total domains processed: {stats['total']}")
    print(f"Successfully updated: {stats['updated']}")
    print(f"Skipped (up-to-date): {stats['skipped']}")
    print(f"Not found on server: {stats['not_found']}")
    print(f"Errors: {stats['errors']}")

if __name__ == "__main__":
    try:
        main()
        print("Script completed successfully")
    except Exception as e:
        print(f"\nCRITICAL ERROR: {str(e)}")
        sys.exit(1)