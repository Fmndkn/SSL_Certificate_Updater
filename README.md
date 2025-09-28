# SSL Certificate Updater

Automated SSL certificate updater that copies certificates from remote server via SSH. Designed for easy automation and reliable certificate management.

![Python](https://img.shields.io/badge/python-3.6%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macOS%20%7C%20windows-lightgrey)

## Features

- 🔐 **Secure SSH connections** with key-based authentication
- 🔄 **Smart certificate comparison** - only updates changed certificates
- ⚙️ **Flexible configuration** - support for multiple domains and server paths
- 📊 **Detailed logging** - comprehensive operation logs and statistics
- 🕐 **Scheduling ready** - easy integration with cron and task schedulers
- 🐍 **Python 3.6+** - cross-platform compatibility

## Quick Start

### 1. Installation

``` bash
# Clone or download the repository
git clone https://github.com/fmndkn/ssl-certificate-updater.git
cd ssl-certificate-updater

# Install dependencies
pip install -r requirements.txt
```

### 2. Basic Configuration
   Edit **_config.ini_**:

``` ini
[SSH]
host = your-server.com
username = root
private_key = ~/.ssh/id_rsa

[PATHS]
remote_cert_path = /www/server/panel/vhost/letsencrypt #example path in aaPanel

[LOCAL]
base_path = ~/ssl-certs

[DOMAINS]
example.com =
www.example.com = www
```
### 3. Run
``` bash
   python cert_updater.py
```

***

## Table of Contents
+ [Installation](#Installation)
+ [Configuration](#Configuration)
+ [Usage](#Usage)
+ [Automation](#Automation)
+ [Troubleshooting](#Troubleshooting)
+ [Examples](#Examples)
+ [Contributing](#Contributing)
+ [License](#License)

## <a id="Installation">Installation</a>

### Prerequisites
+ Python 3.6 or higher
+ SSH access to remote server with key-based authentication
+ Read access to SSL certificates on remote server

### Method 1: Direct Installation
``` bash
# Install dependencies
pip install -r requirements.txt

# Or install specific packages
pip install paramiko cryptography
```

### Method 2: Using Install Scripts
#### Linux/macOS:
``` bash
chmod +x install_dependencies.sh
./install_dependencies.sh
```

#### Windows:
``` cmd
install_dependencies.bat
```

### Method 3: Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## <a id="Configuration">Configuration</a>

### Configuration File Structure
Create or edit **_config.ini_**:

``` ini
[SSH]
host = your-server.com          ; Server hostname or IP
port = 22                       ; SSH port (default: 22)
username = root                 ; SSH username
private_key = ~/.ssh/id_rsa     ; Path to private key
use_ssh_agent = false           ; Use SSH agent (true/false)
; key_password =                ; Key password (not recommended)

[PATHS]
remote_cert_path = /www/server/panel/vhost/letsencrypt
name_cert = fullchain.pem       ; Certificate filename on server
name_privkey = privkey.pem      ; Private key filename on server

[LOCAL]
base_path = ~/ssl-certs         ; Local storage directory
name_cert = fullchain.pem       ; Local certificate filename
name_privkey = privkey.pem      ; Local private key filename
name_dir = true                 ; Create subdirectories for domains

[DOMAINS]
; Format: domain = prefix
example.com =                   ; No prefix
www.example.com = www           ; www prefix
api.example.com = api           ; api prefix
shop.com = *                    ; Wildcard prefix

[LOGGING]
log_file = ~/logs/cert_updater.log
```

### SSH Key Setup
1. Generate SSH key (if you don't have one):

``` bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/ssl_updater_key
```
2. Copy public key to server:

```bash
ssh-copy-id -i ~/.ssh/ssl_updater_key.pub user@server.com
```

3. Test connection:

``` bash
ssh -i ~/.ssh/ssl_updater_key user@server.com
```

### Domain Configuration Examples
#### Basic domain:

``` ini
example.com =
```

Server path: **_/remote/path/example.com/fullchain.pem_**

Local path: **_~/ssl-certs/example.com/fullchain.pem_**

#### Subdomain with prefix:

``` ini
www.example.com = www
```

Server path: **_/remote/path/www.example.com/fullchain.pem_**

Local path: **_~/ssl-certs/www.example.com/fullchain.pem_**

#### Wildcard domain:

``` ini
example.com = *
```
Server path: **_/remote/path/*.example.com/fullchain.pem_**

Local path: **_~/ssl-certs/example.com/fullchain.pem_**

## <a id="Usage">Usage</a>

### Basic Commands

```bash
# Basic run with default config.ini
python cert_updater.py

# Specify custom config file
python cert_updater.py -c /path/to/config.ini

# Enable debug mode
python cert_updater.py -d

# Combine options
python cert_updater.py -c config.ini -d
```

### Command Line Options
|      Option      | Description                                    |
|:----------------:|:-----------------------------------------------|
| **-c, --config** | Path to configuration file (default: config.ini)|
| **-d, --debug**  | Enable debug output and detailed logging       |
|    **--help**    | Show help message                              |

### Output Example
``` text
Starting SSL Certificate Updater with config: config.ini
Processing 3 domains

Update Summary:
Total domains processed: 3
Successfully updated: 2
Skipped (up-to-date): 1
Not found on server: 0
Errors: 0

Script completed successfully
```

### Log File Structure
``` text
2024-01-15 10:30:45 - INFO - ====== Start Update ======
2024-01-15 10:30:45 - INFO - Using configuration file: /path/to/config.ini
2024-01-15 10:30:46 - INFO - Processing 3 domains
2024-01-15 10:30:47 - INFO - [example.com] Certificates are up-to-date
2024-01-15 10:30:48 - INFO - [www.example.com] Certificates updated successfully
2024-01-15 10:30:49 - INFO - ===== Update Summary =====
2024-01-15 10:30:49 - INFO - Total domains processed: 3
2024-01-15 10:30:49 - INFO - Successfully updated: 2
2024-01-15 10:30:49 - INFO - Skipped (up-to-date): 1
2024-01-15 10:30:49 - INFO - ==========================
2024-01-15 10:30:49 - INFO - ======= End Update =======
```

## <a id="Automation">Automation</a>

### Linux/macOS (cron)
1. Open crontab:

``` bash
crontab -e
```

2. Add weekly job:

``` bash
# Run every Sunday at 3:00 AM
0 3 * * 0 /usr/bin/python3 /path/to/cert_updater.py -c /path/to/config.ini

# With logging
0 3 * * 0 /usr/bin/python3 /path/to/cert_updater.py -c /path/to/config.ini >> /var/log/cert_updater.log 2>&1
```

3. Using wrapper script:

``` bash
# Create run_cert_updater.sh
#!/bin/bash
cd /path/to/script/directory
python3 cert_updater.py -c config.ini

# Add to crontab
0 3 * * 0 /path/to/run_cert_updater.sh
```

### Windows (Task Scheduler)
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger to Weekly
4. Action: Start a program
   + Program: **python.exe**
   + Arguments: **C:\path\to\cert_updater.py -c C:\path\to\config.ini**

### Using Systemd (Linux)
Create **/etc/systemd/system/ssl-cert-updater.service:**

```ini
[Unit]
Description=SSL Certificate Updater
After=network.target

[Service]
Type=oneshot
User=your-user
WorkingDirectory=/path/to/script
ExecStart=/usr/bin/python3 cert_updater.py -c config.ini

[Install]
WantedBy=multi-user.target
```

Create **/etc/systemd/system/ssl-cert-updater.timer:**

```ini
[Unit]
Description=Weekly SSL Certificate Update
Requires=ssl-cert-updater.service

[Timer]
OnCalendar=Sun 03:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable and start:

```bash
sudo systemctl enable ssl-cert-updater.timer
sudo systemctl start ssl-cert-updater.timer
```
## <a id="Troubleshooting">Troubleshooting</a>

### Common Issues

**SSH Connection Failed:**

```text
ERROR: Connection failed: Authentication failed
```

+ Verify SSH key path in config
+ Check key permissions: chmod 600 ~/.ssh/your_key
+ Test SSH connection manually

**Certificate Not Found:**

```text
ERROR: [domain.com] Certificate not found at server path
```

+ Verify domain spelling and prefixes
+ Check remote certificate path on server
+ Ensure certificates exist on server

**Permission Denied:**

``` text
ERROR: Permission denied: '/path/to/file'
```

+ Check write permissions for local directory
+ Verify file ownership
+ Run with correct user privileges

### Debug Mode
Enable detailed logging with debug mode:

``` bash
python cert_updater.py -d
```

### Testing Components
**Test SSH connection:**

```bash
ssh -i ~/.ssh/your_key -p port user@server "ls /remote/cert/path"
```

**Test Python dependencies:**

```bash
python -c "import paramiko; print('Paramiko OK')"
python -c "import cryptography; print('Cryptography OK')"
```

**Verify configuration:**

```bash
python cert_updater.py -c config.ini --help
```

### Log Files

+ **Application logs:** *~/logs/cert_updater.log* (configurable)
+ **Cron logs:** */var/log/syslog* or *journalctl -u cron*
+ **System logs:** */var/log/messages* or */var/log/syslog*

## <a id="Examples">Examples</a>

### Example 1: Basic Web Server
```ini
[SSH]
host = web-server.com
username = admin
private_key = ~/.ssh/web_key

[PATHS]
remote_cert_path = /etc/letsencrypt/live

[LOCAL]
base_path = /var/ssl-certs

[DOMAINS]
mywebsite.com =
www.mywebsite.com = www
api.mywebsite.com = api

[LOGGING]
log_file = /var/log/ssl_updater.log
```

### Example 2: Multiple Wildcard Domains

```ini
[SSH]
host = ssl-host.com
username = ssluser
private_key = ~/.ssh/ssl_key
use_ssh_agent = true

[PATHS]
remote_cert_path = /www/ssl-certs

[LOCAL]
base_path = /backup/ssl
name_dir = true

[DOMAINS]
company.com = *
app.company.com = app
*.dev.company.com = *.dev

[LOGGING]
log_file = /backup/logs/ssl_update.log
```

### Example 3: Flat File Structure

```ini
[SSH]
host = backup-server.com
username = backup
private_key = ~/.ssh/backup_key

[PATHS]
remote_cert_path = /etc/ssl

[LOCAL]
base_path = /backup/ssl
name_dir = false
name_cert = certificate.pem
name_privkey = private.key

[DOMAINS]
primary-domain.com =

[LOGGING]
log_file = /backup/logs/ssl.log
```

### Project Structure

```text
ssl-certificate-updater/
├── cert_updater.py           # Main script
├── config.ini               # Configuration template
├── requirements.txt         # Python dependencies
├── install_dependencies.sh  # Linux/macOS installer
├── install_dependencies.bat # Windows installer
├── setup.py                # Package installation
└── README.md               # This file
```

## <a id="Contributing">Contributing</a>

We welcome contributions! Please feel free to submit pull requests, open issues, or suggest improvements.

## Development Setup

+ Fork the repository
+ Create a feature branch
+ Make your changes
+ Add tests if applicable
+ Submit a pull request

## Reporting Issues
When reporting issues, please include:
+ Configuration file (without sensitive information)
+ Log files
+ Steps to reproduce
+ Environment details

## <a id="License">License</a>
This project is licensed under the MIT License.

## Support
If you encounter any problems or have questions:
+ Check the [troubleshooting](#troubleshooting) section
+ Search existing [issues](#issues)
+ Create a new issue with detailed information

## Security
For security concerns or vulnerability reports, please contact us directly rather than opening a public issue.
***
Note: Always test configurations in a safe environment before deploying to production. Regular backups of certificates and configuration files are recommended.
