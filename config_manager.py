"""
Gestionnaire de Configuration AEGISLAN
Gère le basculement SQLite ↔ PostgreSQL et toute la configuration production
"""

import os
import json
from typing import Dict, Any, Optional
from datetime import datetime

class ConfigManager:
    """Gestionnaire centralisé de configuration AEGISLAN"""
    
    def __init__(self, config_file: str = "config/aegislan_config.json"):
        self.config_file = config_file
        self.config = {}
        self.load_config()
    
    def load_config(self):
        """Charge la configuration depuis le fichier ou crée une configuration par défaut"""
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
                print(f"✅ Configuration chargée depuis {self.config_file}")
            except Exception as e:
                print(f"⚠️ Erreur lecture config: {e}, utilisation config par défaut")
                self.config = self.get_default_config()
        else:
            self.config = self.get_default_config()
            self.save_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Configuration par défaut AEGISLAN"""
        
        return {
            "database": {
                "type": "sqlite",  # sqlite ou postgresql
                "sqlite": {
                    "path": "data/aegislan.db"
                },
                "postgresql": {
                    "host": os.getenv("PGHOST", "localhost"),
                    "port": int(os.getenv("PGPORT", "5432")),
                    "database": os.getenv("PGDATABASE", "aegislan"),
                    "user": os.getenv("PGUSER", "postgres"),
                    "password": os.getenv("PGPASSWORD", ""),
                    "ssl_mode": "prefer",
                    "connection_string": os.getenv("DATABASE_URL")
                },
                "retention_days": 90,
                "cleanup_enabled": True,
                "backup_enabled": True
            },
            
            "network": {
                "monitoring": {
                    "enabled": True,
                    "scan_range": "192.168.1.0/24",
                    "monitoring_interval": 300,  # 5 minutes
                    "discovery_interval": 3600,  # 1 heure
                    "deep_scan_interval": 86400  # 24 heures
                },
                "nmap": {
                    "enabled": True,
                    "port_range": "1-1000",
                    "scan_technique": "SYN",
                    "timing": "T3",
                    "os_detection": True,
                    "service_detection": True
                },
                "snmp": {
                    "enabled": False,
                    "community": "public",
                    "version": "2c",
                    "timeout": 10,
                    "retries": 3
                }
            },
            
            "ai": {
                "model": {
                    "algorithm": "IsolationForest",
                    "contamination": 0.1,
                    "n_estimators": 100,
                    "max_samples": "auto",
                    "random_state": 42
                },
                "training": {
                    "retrain_interval": "weekly",
                    "min_training_samples": 1000,
                    "feature_selection": "auto",
                    "validation_split": 0.2
                },
                "detection": {
                    "threshold_critical": 0.8,
                    "threshold_high": 0.6,
                    "threshold_medium": 0.4,
                    "threshold_low": 0.2,
                    "batch_size": 1000
                }
            },
            
            "alerting": {
                "enabled": True,
                "channels": {
                    "console": True,
                    "file": True,
                    "email": False,
                    "webhook": False
                },
                "severity_filters": {
                    "console": ["Critique", "Élevé"],
                    "email": ["Critique"],
                    "webhook": ["Critique", "Élevé"]
                },
                "rate_limiting": {
                    "enabled": True,
                    "max_alerts_per_minute": 10,
                    "max_alerts_per_device": 5
                }
            },
            
            "web": {
                "host": "0.0.0.0",
                "port": 5000,
                "debug": False,
                "auto_refresh": True,
                "refresh_interval": 30,
                "theme": "dark",
                "authentication": {
                    "enabled": False,
                    "type": "basic",
                    "users": {}
                }
            },
            
            "logging": {
                "level": "INFO",
                "file_enabled": True,
                "file_path": "logs/aegislan.log",
                "max_file_size": "10MB",
                "backup_count": 5,
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
            
            "deployment": {
                "environment": "development",  # development, staging, production
                "version": "1.0.0",
                "instance_id": None,
                "startup_checks": True,
                "health_checks": True,
                "metrics_enabled": True
            }
        }
    
    def save_config(self):
        """Sauvegarde la configuration dans le fichier"""
        
        # Créer le répertoire config s'il n'existe pas
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4, default=str)
            print(f"✅ Configuration sauvegardée dans {self.config_file}")
        except Exception as e:
            print(f"❌ Erreur sauvegarde config: {e}")
    
    def update_config(self, section: str, key: str, value: Any):
        """Met à jour une valeur de configuration"""
        
        if section not in self.config:
            self.config[section] = {}
        
        self.config[section][key] = value
        self.save_config()
        print(f"✅ Configuration mise à jour: {section}.{key} = {value}")
    
    def get_database_config(self) -> Dict[str, Any]:
        """Configuration de base de données"""
        return self.config.get("database", {})
    
    def get_network_config(self) -> Dict[str, Any]:
        """Configuration réseau"""
        return self.config.get("network", {})
    
    def get_ai_config(self) -> Dict[str, Any]:
        """Configuration IA"""
        return self.config.get("ai", {})
    
    def get_web_config(self) -> Dict[str, Any]:
        """Configuration interface web"""
        return self.config.get("web", {})
    
    def switch_to_postgresql(self, connection_string: str = None):
        """Bascule vers PostgreSQL"""
        
        self.config["database"]["type"] = "postgresql"
        
        if connection_string:
            self.config["database"]["postgresql"]["connection_string"] = connection_string
        
        self.save_config()
        print("🔄 Basculement vers PostgreSQL configuré")
    
    def switch_to_sqlite(self, db_path: str = None):
        """Bascule vers SQLite"""
        
        self.config["database"]["type"] = "sqlite"
        
        if db_path:
            self.config["database"]["sqlite"]["path"] = db_path
        
        self.save_config()
        print("🔄 Basculement vers SQLite configuré")
    
    def is_production(self) -> bool:
        """Vérifie si on est en environnement de production"""
        return self.config.get("deployment", {}).get("environment") == "production"
    
    def setup_production_environment(self):
        """Configure l'environnement de production"""
        
        self.config["deployment"]["environment"] = "production"
        self.config["database"]["type"] = "postgresql"
        self.config["web"]["debug"] = False
        self.config["logging"]["level"] = "WARNING"
        self.config["ai"]["training"]["retrain_interval"] = "daily"
        self.config["network"]["monitoring"]["monitoring_interval"] = 60  # 1 minute
        
        self.save_config()
        print("🚀 Environnement de production configuré")

# Factory pour créer le bon gestionnaire de base selon la config
def create_database_manager(config_manager: ConfigManager):
    """Factory qui crée le bon gestionnaire de base selon la configuration"""
    
    db_config = config_manager.get_database_config()
    db_type = db_config.get("type", "sqlite")
    
    if db_type == "postgresql":
        from postgresql_manager import PostgreSQLManager
        
        pg_config = db_config.get("postgresql", {})
        connection_string = pg_config.get("connection_string")
        
        if not connection_string:
            # Construire la chaîne de connexion
            host = pg_config.get("host", "localhost")
            port = pg_config.get("port", 5432)
            database = pg_config.get("database", "aegislan")
            user = pg_config.get("user", "postgres")
            password = pg_config.get("password", "")
            
            connection_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        
        return PostgreSQLManager(connection_string)
    
    else:  # SQLite par défaut
        from database_manager import DatabaseManager
        
        sqlite_config = db_config.get("sqlite", {})
        db_path = sqlite_config.get("path", "data/aegislan.db")
        
        return DatabaseManager(db_path)

if __name__ == "__main__":
    # Test de configuration
    
    config = ConfigManager()
    
    # Test basculement PostgreSQL
    config.switch_to_postgresql("postgresql://user:pass@neon.tech:5432/aegislan")
    
    # Créer le bon gestionnaire
    db_manager = create_database_manager(config)
    
    print(f"Type de base utilisé: {type(db_manager).__name__}")