"""
Guide de déploiement AEGISLAN sur Windows 11 Server
"""

import os
import sys
import subprocess
import json
from pathlib import Path

class WindowsDeploymentGuide:
    """Guide automatisé pour le déploiement sur Windows 11"""
    
    def __init__(self):
        self.python_version = "3.11"
        self.project_path = Path("C:/AEGISLAN")
        self.service_name = "AEGISLAN-NetworkSecurity"
        
    def check_prerequisites(self):
        """Vérifier les prérequis système"""
        print("🔍 Vérification des prérequis...")
        
        # Vérifier Python
        try:
            result = subprocess.run([sys.executable, "--version"], 
                                 capture_output=True, text=True)
            print(f"✅ Python détecté: {result.stdout.strip()}")
        except:
            print("❌ Python non installé")
            return False
        
        # Vérifier les droits administrateur
        import ctypes
        if not ctypes.windll.shell32.IsUserAnAdmin():
            print("❌ Droits administrateur requis")
            return False
        
        print("✅ Tous les prérequis sont satisfaits")
        return True
    
    def install_dependencies(self):
        """Installer les dépendances système"""
        print("📦 Installation des dépendances...")
        
        # Installer les packages Python
        packages = [
            "streamlit",
            "pandas",
            "numpy",
            "plotly",
            "scikit-learn",
            "psutil",
            "python-nmap"
        ]
        
        for package in packages:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", package], 
                             check=True)
                print(f"✅ {package} installé")
            except subprocess.CalledProcessError:
                print(f"❌ Erreur installation {package}")
        
        # Installer Nmap (optionnel)
        print("⚠️  Installez Nmap depuis https://nmap.org/download.html")
        
    def setup_project_structure(self):
        """Créer la structure du projet"""
        print("🏗️  Création de la structure projet...")
        
        # Créer les dossiers
        self.project_path.mkdir(exist_ok=True)
        (self.project_path / "logs").mkdir(exist_ok=True)
        (self.project_path / "data").mkdir(exist_ok=True)
        (self.project_path / "config").mkdir(exist_ok=True)
        
        # Créer le fichier de configuration
        config = {
            "network_range": "192.168.1.0/24",
            "scan_interval": 300,
            "database_path": str(self.project_path / "data" / "aegislan.db"),
            "log_level": "INFO",
            "web_port": 8501,
            "auto_start": True
        }
        
        with open(self.project_path / "config" / "config.json", "w") as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Structure créée dans {self.project_path}")
    
    def create_windows_service(self):
        """Créer le service Windows"""
        print("🔧 Création du service Windows...")
        
        # Script de service Windows
        service_script = f"""
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import subprocess
import os

class AegislanService(win32serviceutil.ServiceFramework):
    _svc_name_ = "{self.service_name}"
    _svc_display_name_ = "AEGISLAN Network Security Monitor"
    _svc_description_ = "AI-powered network anomaly detection system"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_,''))
        self.main()

    def main(self):
        os.chdir(r"{self.project_path}")
        
        # Démarrer Streamlit
        cmd = [
            r"{sys.executable}",
            "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0",
            "--server.headless", "true"
        ]
        
        subprocess.run(cmd)

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(AegislanService)
"""
        
        with open(self.project_path / "aegislan_service.py", "w") as f:
            f.write(service_script)
        
        print("✅ Script de service créé")
        
        # Instructions d'installation
        print("\n📋 Pour installer le service:")
        print(f"1. cd {self.project_path}")
        print("2. python aegislan_service.py install")
        print("3. python aegislan_service.py start")
    
    def create_startup_script(self):
        """Créer un script de démarrage"""
        print("🚀 Création du script de démarrage...")
        
        startup_script = f"""@echo off
echo Démarrage AEGISLAN...
cd /d "{self.project_path}"
python -m streamlit run app.py --server.port 8501 --server.address 0.0.0.0
pause
"""
        
        with open(self.project_path / "start_aegislan.bat", "w") as f:
            f.write(startup_script)
        
        print("✅ Script de démarrage créé: start_aegislan.bat")
    
    def setup_firewall(self):
        """Configurer le pare-feu Windows"""
        print("🛡️  Configuration du pare-feu...")
        
        # Commandes firewall
        firewall_commands = [
            'netsh advfirewall firewall add rule name="AEGISLAN-HTTP" dir=in action=allow protocol=TCP localport=8501',
            'netsh advfirewall firewall add rule name="AEGISLAN-HTTPS" dir=in action=allow protocol=TCP localport=8502'
        ]
        
        for cmd in firewall_commands:
            try:
                subprocess.run(cmd, shell=True, check=True)
                print(f"✅ Règle firewall ajoutée")
            except subprocess.CalledProcessError:
                print(f"❌ Erreur règle firewall")
    
    def create_database_setup(self):
        """Configuration de la base de données"""
        print("🗄️  Configuration de la base de données...")
        
        db_setup = f"""
# Base de données AEGISLAN
import sqlite3
from database_manager import DatabaseManager

# Initialiser la base de données
db = DatabaseManager(r"{self.project_path}/data/aegislan.db")
print("Base de données initialisée")

# Créer des données de test
import pandas as pd
from datetime import datetime

test_data = pd.DataFrame({{
    'timestamp': [datetime.now()],
    'device_id': ['test_device'],
    'ip_address': ['192.168.1.100'],
    'mac_address': ['00:11:22:33:44:55'],
    'device_type': ['workstation'],
    'port': [80],
    'protocol': ['HTTP'],
    'data_volume_mb': [1.5],
    'is_anomaly': [False]
}})

db.insert_network_data(test_data)
print("Données de test insérées")
"""
        
        with open(self.project_path / "setup_database.py", "w") as f:
            f.write(db_setup)
        
        print("✅ Script de configuration DB créé")
    
    def deploy_full_system(self):
        """Déploiement complet du système"""
        print("🚀 DÉPLOIEMENT COMPLET AEGISLAN SUR WINDOWS 11")
        print("=" * 50)
        
        if not self.check_prerequisites():
            print("❌ Prérequis non satisfaits. Arrêt du déploiement.")
            return
        
        self.install_dependencies()
        self.setup_project_structure()
        self.create_windows_service()
        self.create_startup_script()
        self.setup_firewall()
        self.create_database_setup()
        
        print("\n✅ DÉPLOIEMENT TERMINÉ!")
        print("=" * 50)
        print(f"📁 Dossier projet: {self.project_path}")
        print("🌐 URL d'accès: http://localhost:8501")
        print(f"🌐 Accès réseau: http://[IP-SERVEUR]:8501")
        print("\n📋 Prochaines étapes:")
        print("1. Copier les fichiers Python dans le dossier projet")
        print("2. Exécuter: python setup_database.py")
        print("3. Démarrer avec: start_aegislan.bat")
        print("4. Ou installer comme service Windows")

def main():
    """Fonction principale"""
    deployer = WindowsDeploymentGuide()
    deployer.deploy_full_system()

if __name__ == "__main__":
    main()