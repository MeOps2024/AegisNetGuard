"""
Configuration de production pour AEGISLAN
"""

import os
import json
from pathlib import Path

class ProductionConfig:
    """Configuration pour environnement de production"""
    
    def __init__(self, config_file="config/production.json"):
        self.config_file = config_file
        self.load_config()
    
    def load_config(self):
        """Charger la configuration depuis le fichier"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
        except FileNotFoundError:
            config = self.get_default_config()
            self.save_config(config)
        
        # Configuration réseau
        self.NETWORK_RANGE = config.get('network_range', '192.168.1.0/24')
        self.SCAN_INTERVAL = config.get('scan_interval', 300)  # 5 minutes
        self.CONTINUOUS_MONITORING = config.get('continuous_monitoring', True)
        
        # Configuration base de données
        self.DATABASE_PATH = config.get('database_path', 'data/aegislan_production.db')
        self.DB_BACKUP_INTERVAL = config.get('db_backup_interval', 3600)  # 1 heure
        self.DATA_RETENTION_DAYS = config.get('data_retention_days', 30)
        
        # Configuration IA
        self.AI_MODEL_PATH = config.get('ai_model_path', 'models/')
        self.CONTAMINATION_RATE = config.get('contamination_rate', 0.1)
        self.RETRAIN_INTERVAL = config.get('retrain_interval', 86400)  # 24 heures
        self.MIN_TRAINING_SAMPLES = config.get('min_training_samples', 1000)
        
        # Configuration web
        self.WEB_PORT = config.get('web_port', 8501)
        self.WEB_HOST = config.get('web_host', '0.0.0.0')
        self.SSL_ENABLED = config.get('ssl_enabled', False)
        self.SSL_CERT_PATH = config.get('ssl_cert_path', '')
        self.SSL_KEY_PATH = config.get('ssl_key_path', '')
        
        # Configuration sécurité
        self.ENABLE_AUTHENTICATION = config.get('enable_authentication', True)
        self.SESSION_TIMEOUT = config.get('session_timeout', 3600)  # 1 heure
        self.MAX_LOGIN_ATTEMPTS = config.get('max_login_attempts', 3)
        
        # Configuration alertes
        self.ALERT_EMAIL_ENABLED = config.get('alert_email_enabled', False)
        self.ALERT_EMAIL_SMTP = config.get('alert_email_smtp', '')
        self.ALERT_EMAIL_FROM = config.get('alert_email_from', '')
        self.ALERT_EMAIL_TO = config.get('alert_email_to', [])
        
        # Configuration logging
        self.LOG_LEVEL = config.get('log_level', 'INFO')
        self.LOG_FILE = config.get('log_file', 'logs/aegislan.log')
        self.LOG_MAX_SIZE = config.get('log_max_size', 10485760)  # 10MB
        self.LOG_BACKUP_COUNT = config.get('log_backup_count', 5)
        
        # Configuration collecte de données
        self.ENABLE_NMAP = config.get('enable_nmap', True)
        self.ENABLE_SNMP = config.get('enable_snmp', False)
        self.ENABLE_LOG_PARSING = config.get('enable_log_parsing', False)
        self.ROUTER_LOGS_PATH = config.get('router_logs_path', '')
        
        # Configuration performance
        self.MAX_CONCURRENT_SCANS = config.get('max_concurrent_scans', 3)
        self.SCAN_TIMEOUT = config.get('scan_timeout', 300)  # 5 minutes
        self.MEMORY_LIMIT_MB = config.get('memory_limit_mb', 1024)
    
    def get_default_config(self):
        """Configuration par défaut"""
        return {
            "network_range": "192.168.1.0/24",
            "scan_interval": 300,
            "continuous_monitoring": True,
            "database_path": "data/aegislan_production.db",
            "db_backup_interval": 3600,
            "data_retention_days": 30,
            "ai_model_path": "models/",
            "contamination_rate": 0.1,
            "retrain_interval": 86400,
            "min_training_samples": 1000,
            "web_port": 8501,
            "web_host": "0.0.0.0",
            "ssl_enabled": False,
            "ssl_cert_path": "",
            "ssl_key_path": "",
            "enable_authentication": True,
            "session_timeout": 3600,
            "max_login_attempts": 3,
            "alert_email_enabled": False,
            "alert_email_smtp": "",
            "alert_email_from": "",
            "alert_email_to": [],
            "log_level": "INFO",
            "log_file": "logs/aegislan.log",
            "log_max_size": 10485760,
            "log_backup_count": 5,
            "enable_nmap": True,
            "enable_snmp": False,
            "enable_log_parsing": False,
            "router_logs_path": "",
            "max_concurrent_scans": 3,
            "scan_timeout": 300,
            "memory_limit_mb": 1024
        }
    
    def save_config(self, config):
        """Sauvegarder la configuration"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def update_config(self, updates):
        """Mettre à jour la configuration"""
        with open(self.config_file, 'r') as f:
            config = json.load(f)
        
        config.update(updates)
        self.save_config(config)
        self.load_config()
    
    def get_network_config(self):
        """Configuration réseau"""
        return {
            'network_range': self.NETWORK_RANGE,
            'scan_interval': self.SCAN_INTERVAL,
            'continuous_monitoring': self.CONTINUOUS_MONITORING,
            'enable_nmap': self.ENABLE_NMAP,
            'enable_snmp': self.ENABLE_SNMP,
            'enable_log_parsing': self.ENABLE_LOG_PARSING,
            'router_logs_path': self.ROUTER_LOGS_PATH,
            'max_concurrent_scans': self.MAX_CONCURRENT_SCANS,
            'scan_timeout': self.SCAN_TIMEOUT
        }
    
    def get_database_config(self):
        """Configuration base de données"""
        return {
            'database_path': self.DATABASE_PATH,
            'backup_interval': self.DB_BACKUP_INTERVAL,
            'retention_days': self.DATA_RETENTION_DAYS
        }
    
    def get_ai_config(self):
        """Configuration IA"""
        return {
            'model_path': self.AI_MODEL_PATH,
            'contamination_rate': self.CONTAMINATION_RATE,
            'retrain_interval': self.RETRAIN_INTERVAL,
            'min_training_samples': self.MIN_TRAINING_SAMPLES
        }
    
    def get_web_config(self):
        """Configuration web"""
        return {
            'port': self.WEB_PORT,
            'host': self.WEB_HOST,
            'ssl_enabled': self.SSL_ENABLED,
            'ssl_cert_path': self.SSL_CERT_PATH,
            'ssl_key_path': self.SSL_KEY_PATH
        }
    
    def get_security_config(self):
        """Configuration sécurité"""
        return {
            'enable_authentication': self.ENABLE_AUTHENTICATION,
            'session_timeout': self.SESSION_TIMEOUT,
            'max_login_attempts': self.MAX_LOGIN_ATTEMPTS
        }
    
    def get_logging_config(self):
        """Configuration logging"""
        return {
            'level': self.LOG_LEVEL,
            'file': self.LOG_FILE,
            'max_size': self.LOG_MAX_SIZE,
            'backup_count': self.LOG_BACKUP_COUNT
        }
    
    def validate_config(self):
        """Valider la configuration"""
        errors = []
        
        # Vérifier les chemins
        if not os.path.exists(os.path.dirname(self.DATABASE_PATH)):
            errors.append(f"Database directory does not exist: {os.path.dirname(self.DATABASE_PATH)}")
        
        if not os.path.exists(os.path.dirname(self.LOG_FILE)):
            errors.append(f"Log directory does not exist: {os.path.dirname(self.LOG_FILE)}")
        
        # Vérifier les valeurs
        if self.SCAN_INTERVAL < 60:
            errors.append("Scan interval must be at least 60 seconds")
        
        if self.WEB_PORT < 1024 or self.WEB_PORT > 65535:
            errors.append("Web port must be between 1024 and 65535")
        
        if self.CONTAMINATION_RATE < 0.01 or self.CONTAMINATION_RATE > 0.5:
            errors.append("Contamination rate must be between 0.01 and 0.5")
        
        # Vérifier SSL
        if self.SSL_ENABLED:
            if not os.path.exists(self.SSL_CERT_PATH):
                errors.append(f"SSL certificate file not found: {self.SSL_CERT_PATH}")
            if not os.path.exists(self.SSL_KEY_PATH):
                errors.append(f"SSL key file not found: {self.SSL_KEY_PATH}")
        
        return errors

# Configuration globale
config = ProductionConfig()