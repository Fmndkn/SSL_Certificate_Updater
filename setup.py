#!/usr/bin/env python3
"""
Setup script for SSL Certificate Updater
"""

import os
import sys
from setuptools import setup

def read_requirements():
    """Read requirements from requirements.txt"""
    try:
        with open('requirements.txt', 'r') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        return ["paramiko>=2.7.2", "cryptography>=3.3"]

def read_version():
    """Read version from version file or use default"""
    try:
        with open('VERSION', 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return "1.0.0"

def read_readme():
    """Read README file"""
    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "SSL Certificate Updater - Automated SSL certificate updater via SSH"

# Check if user has write permissions to install directory
def check_install_permissions():
    """Check if user has permissions to install to system directory"""
    if os.geteuid() == 0:  # root user
        return True
    
    # Check if user can write to Python site-packages
    try:
        import site
        packages_dir = site.getusersitepackages()
        test_file = os.path.join(packages_dir, '.write_test')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        return True
    except:
        return False

def main():
    # Check permissions and warn if needed
    if not check_install_permissions():
        print("⚠️  Warning: You don't have permission to install to system directories.")
        print("📝 Recommended installation methods:")
        print("   1. Use virtual environment (recommended):")
        print("      python3 -m venv venv")
        print("      source venv/bin/activate")
        print("      pip install .")
        print("")
        print("   2. Install for current user only:")
        print("      pip install --user .")
        print("")
        print("   3. Use sudo (not recommended for security):")
        print("      sudo pip install .")
        print("")
        
        response = input("Do you want to continue with --user installation? (y/n): ")
        if response.lower() in ['y', 'yes']:
            # Install for current user
            os.system(f"{sys.executable} -m pip install --user .")
            return
        else:
            print("Installation cancelled.")
            sys.exit(1)
    
    # Proceed with normal installation
    setup(
        name="ssl-certificate-updater",
        version=read_version(),
        description="Automated SSL certificate updater via SSH",
        long_description=read_readme(),
        long_description_content_type="text/markdown",
        author="SSL Certificate Updater",
        author_email="none",
        url="https://github.com/yourusername/ssl-certificate-updater",
        py_modules=["cert_updater"],
        install_requires=read_requirements(),
        entry_points={
            'console_scripts': [
                'cert-updater=cert_updater:main',
            ],
        },
        classifiers=[
            "Development Status :: 4 - Beta",
            "Intended Audience :: System Administrators",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Topic :: Security :: Cryptography",
            "Topic :: System :: Systems Administration",
        ],
        python_requires=">=3.6",
        keywords="ssl, certificate, ssh, automation, security",
    )

if __name__ == "__main__":
    main()