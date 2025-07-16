# GUIDE COMPLET DE DÉPLOIEMENT PRODUCTION AEGISLAN

## Vue d'ensemble du Déploiement

Le déploiement d'AEGISLAN en production nécessite une approche méthodique couvrant l'infrastructure, la sécurité, la connectivité réseau et la maintenance. Ce guide détaille chaque étape pour un déploiement enterprise sur Windows 11 Server.

## 1. Architecture de Déploiement Production

### Infrastructure Cible
```
Windows 11 Server (Serveur Dédié)
├── AEGISLAN Application (Port 5000)
├── PostgreSQL Database (Port 5432)
├── Network Monitoring (Nmap + SNMP)
├── Firewall Configuration
└── Service Windows (Auto-start)
```

### Prérequis Système
- **OS** : Windows 11 Pro/Enterprise ou Windows Server 2022
- **RAM** : Minimum 8GB (16GB recommandé)
- **CPU** : 4 cores minimum (8 cores recommandé)
- **Stockage** : 100GB SSD minimum
- **Réseau** : Interface Gigabit, accès administrateur équipements réseau

## 2. Installation et Configuration Étape par Étape

### Étape 1 : Préparation de l'Environnement

#### 1.1 Installation Python 3.11
```powershell
# Télécharger depuis python.org ou utiliser winget
winget install Python.Python.3.11

# Vérification installation
python --version
pip --version
```

#### 1.2 Installation Outils Réseau
```powershell
# Nmap (télécharger depuis nmap.org)
# Installation manuelle requise pour Windows

# Vérification Nmap
nmap --version
```

#### 1.3 Droits Administrateur
```powershell
# Exécuter PowerShell en tant qu'administrateur
# Vérifier privilèges
net session
```

### Étape 2 : Installation AEGISLAN

#### 2.1 Structure des Dossiers
```powershell
# Création structure projet
$ProjectPath = "C:\AEGISLAN"
New-Item -ItemType Directory -Path $ProjectPath
New-Item -ItemType Directory -Path "$ProjectPath\data"
New-Item -ItemType Directory -Path "$ProjectPath\logs"
New-Item -ItemType Directory -Path "$ProjectPath\config"
New-Item -ItemType Directory -Path "$ProjectPath\scripts"
New-Item -ItemType Directory -Path "$ProjectPath\exports"
```

#### 2.2 Installation Dépendances
```powershell
# Naviguer vers le dossier projet
cd C:\AEGISLAN

# Installation des packages Python
pip install streamlit pandas numpy scikit-learn plotly psutil psycopg2-binary

# Vérification installations
pip list | Select-String "streamlit|pandas|numpy|scikit-learn|plotly|psutil|psycopg2"
```

#### 2.3 Copie des Fichiers
```powershell
# Copier tous les fichiers .py vers C:\AEGISLAN\
# Structure finale :
C:\AEGISLAN\
├── app.py
├── anomaly_detector.py
├── data_simulator.py
├── dashboard_clean.py
├── database_manager.py
├── postgresql_manager.py
├── real_network_collector.py
├── config_manager.py
├── production_config.py
└── windows_deployment_guide.py
```

### Étape 3 : Configuration Base de Données Production

#### 3.1 Choix Base de Données

**Option A : PostgreSQL Local (Autonome)**
```powershell
# Installation PostgreSQL 15
winget install PostgreSQL.PostgreSQL

# Configuration utilisateur
createuser --username=postgres --createdb --createrole aegislan_user
createdb --username=postgres --owner=aegislan_user aegislan_db

# Variables d'environnement
[Environment]::SetEnvironmentVariable("PGHOST", "localhost", "Machine")
[Environment]::SetEnvironmentVariable("PGPORT", "5432", "Machine")
[Environment]::SetEnvironmentVariable("PGDATABASE", "aegislan_db", "Machine")
[Environment]::SetEnvironmentVariable("PGUSER", "aegislan_user", "Machine")
[Environment]::SetEnvironmentVariable("PGPASSWORD", "VotreMotDePasseSecurise", "Machine")
```

**Option B : Neon Database Cloud (Recommandé)**
```powershell
# Créer compte sur neon.tech
# Créer projet "AEGISLAN"
# Récupérer chaîne de connexion

# Variable d'environnement
[Environment]::SetEnvironmentVariable("DATABASE_URL", "postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/aegislan?sslmode=require", "Machine")
```

#### 3.2 Initialisation Base de Données
```python
# Script d'initialisation (init_database.py)
from config_manager import ConfigManager, create_database_manager

def init_production_database():
    print("Initialisation base de données production...")
    
    # Chargement configuration
    config = ConfigManager()
    
    # Basculement vers PostgreSQL si nécessaire
    if config.get_database_config()['type'] != 'postgresql':
        config.switch_to_postgresql()
    
    # Création gestionnaire base
    db_manager = create_database_manager(config)
    
    # Initialisation tables
    db_manager.init_database()
    
    print("Base de données initialisée avec succès!")
    
    return db_manager

if __name__ == "__main__":
    init_production_database()
```

### Étape 4 : Configuration Réseau

#### 4.1 Configuration du Monitoring Réseau

**Fichier config/network_config.json** :
```json
{
    "network_monitoring": {
        "scan_range": "192.168.1.0/24",
        "monitoring_interval": 300,
        "discovery_interval": 3600,
        "deep_scan_interval": 86400
    },
    "nmap_settings": {
        "port_range": "1-1000",
        "scan_technique": "SYN",
        "timing": "T3",
        "os_detection": true,
        "service_detection": true,
        "script_scanning": false
    },
    "snmp_settings": {
        "enabled": false,
        "community": "public",
        "version": "2c",
        "timeout": 10,
        "retries": 3,
        "router_ips": []
    }
}
```

#### 4.2 Test de Connectivité Réseau
```python
# Script de test (test_network.py)
import subprocess
import json
from real_network_collector import RealNetworkCollector

def test_network_connectivity():
    print("Test de connectivité réseau...")
    
    # Test ping réseau local
    result = subprocess.run(
        ["ping", "-n", "1", "192.168.1.1"], 
        capture_output=True, text=True
    )
    
    if result.returncode == 0:
        print("[SUCCESS] Ping routeur OK")
    else:
        print("[ERROR] Impossible de contacter le routeur")
        return False
    
    # Test Nmap
    try:
        collector = RealNetworkCollector()
        devices = collector.scan_network_nmap()
        print(f"[SUCCESS] Nmap détecte {len(devices)} appareils")
    except Exception as e:
        print(f"[ERROR] Nmap error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_network_connectivity()
```

### Étape 5 : Configuration du Service Windows

#### 5.1 Création du Service
```python
# Script service Windows (aegislan_service.py)
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import subprocess
import time
import sys
import os

class AEGISLANService(win32serviceutil.ServiceFramework):
    _svc_name_ = "AEGISLANMonitoring"
    _svc_display_name_ = "AEGISLAN Network Monitoring Service"
    _svc_description_ = "Service de surveillance réseau et détection d'anomalies"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        self.is_alive = True
        self.streamlit_process = None
        
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.is_alive = False
        
        # Arrêt du processus Streamlit
        if self.streamlit_process:
            self.streamlit_process.terminate()
            
    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        
        self.main()
        
    def main(self):
        # Changement vers répertoire AEGISLAN
        os.chdir("C:\\AEGISLAN")
        
        # Démarrage Streamlit
        try:
            self.streamlit_process = subprocess.Popen([
                sys.executable, "-m", "streamlit", "run", 
                "app.py", "--server.port", "5000", 
                "--server.address", "0.0.0.0"
            ])
            
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STARTED,
                (self._svc_name_, 'Streamlit démarré sur port 5000')
            )
            
            # Boucle de surveillance
            while self.is_alive:
                # Vérification processus Streamlit
                if self.streamlit_process.poll() is not None:
                    # Redémarrage automatique
                    servicemanager.LogMsg(
                        servicemanager.EVENTLOG_WARNING_TYPE,
                        servicemanager.PYS_SERVICE_STARTED,
                        (self._svc_name_, 'Redémarrage Streamlit')
                    )
                    
                    self.streamlit_process = subprocess.Popen([
                        sys.executable, "-m", "streamlit", "run", 
                        "app.py", "--server.port", "5000", 
                        "--server.address", "0.0.0.0"
                    ])
                
                time.sleep(30)  # Vérification toutes les 30 secondes
                
        except Exception as e:
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_ERROR_TYPE,
                servicemanager.PYS_SERVICE_STARTED,
                (self._svc_name_, f'Erreur: {str(e)}')
            )

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(AEGISLANService)
```

#### 5.2 Installation du Service
```powershell
# Installation service (PowerShell administrateur)
cd C:\AEGISLAN
python aegislan_service.py install

# Démarrage service
python aegislan_service.py start

# Vérification statut
python aegislan_service.py status

# Configuration démarrage automatique
sc config AEGISLANMonitoring start= auto
```

### Étape 6 : Configuration Pare-feu

#### 6.1 Règles Pare-feu Windows
```powershell
# Autoriser port 5000 (interface Streamlit)
New-NetFirewallRule -DisplayName "AEGISLAN Web Interface" -Direction Inbound -Port 5000 -Protocol TCP -Action Allow

# Autoriser Nmap (optionnel si scan externe)
New-NetFirewallRule -DisplayName "AEGISLAN Nmap Outbound" -Direction Outbound -Program "C:\Program Files (x86)\Nmap\nmap.exe" -Action Allow

# Autoriser PostgreSQL (si base locale)
New-NetFirewallRule -DisplayName "PostgreSQL" -Direction Inbound -Port 5432 -Protocol TCP -Action Allow

# Vérification règles
Get-NetFirewallRule -DisplayName "*AEGISLAN*"
```

## 3. Entraînement et Configuration de l'IA

### 3.1 Collecte de Données de Base (Baseline)

#### Phase 1 : Collecte Données Normales (1 semaine)
```python
# Script collecte baseline (collect_baseline.py)
from real_network_collector import RealNetworkCollector
from config_manager import ConfigManager, create_database_manager
import time
import schedule

def collect_baseline_data():
    print("Démarrage collecte données baseline...")
    
    # Initialisation
    config = ConfigManager()
    db_manager = create_database_manager(config)
    collector = RealNetworkCollector(db_manager=db_manager)
    
    # Collecte continue pendant 7 jours
    def collect_cycle():
        try:
            # Scan réseau
            network_data = collector.scan_network_nmap()
            
            # Collecte connexions locales
            connections = collector.collect_active_connections()
            
            # Stockage en base
            if not network_data.empty:
                db_manager.insert_network_data(network_data.to_dict('records'))
                
            if not connections.empty:
                db_manager.insert_network_data(connections.to_dict('records'))
                
            print(f"Cycle collecte terminé: {len(network_data) + len(connections)} enregistrements")
            
        except Exception as e:
            print(f"Erreur collecte: {e}")
    
    # Programmation collecte toutes les 5 minutes
    schedule.every(5).minutes.do(collect_cycle)
    
    print("Collecte baseline programmée (5 minutes). Arrêt après 7 jours.")
    
    # Boucle collecte (7 jours)
    start_time = time.time()
    week_seconds = 7 * 24 * 60 * 60
    
    while time.time() - start_time < week_seconds:
        schedule.run_pending()
        time.sleep(60)
    
    print("Collecte baseline terminée. Données prêtes pour entraînement.")

if __name__ == "__main__":
    collect_baseline_data()
```

### 3.2 Entraînement du Modèle IA

#### Script d'Entraînement Automatisé
```python
# Script entraînement (train_model.py)
from anomaly_detector import AnomalyDetector
from config_manager import ConfigManager, create_database_manager
import pandas as pd
import joblib
from datetime import datetime, timedelta

def train_production_model():
    print("Démarrage entraînement modèle production...")
    
    # Initialisation
    config = ConfigManager()
    db_manager = create_database_manager(config)
    detector = AnomalyDetector()
    
    # Récupération données baseline (7 derniers jours)
    print("Chargement données d'entraînement...")
    training_data = db_manager.get_network_data(hours=168)  # 7 jours = 168 heures
    
    if len(training_data) < 1000:
        print(f"[WARNING] Peu de données ({len(training_data)}). Recommandé: >10000")
        response = input("Continuer l'entraînement ? (y/n): ")
        if response.lower() != 'y':
            return
    
    # Préparation données
    print("Préparation features...")
    training_data['hour'] = training_data['timestamp'].dt.hour
    training_data['day_of_week'] = training_data['timestamp'].dt.dayofweek
    
    # Calculs statistiques par appareil
    device_stats = training_data.groupby('device_id').agg({
        'data_volume_mb': ['mean', 'std', 'max'],
        'port': 'nunique'
    })
    
    # Merge avec données principales
    device_stats.columns = ['avg_data_volume', 'std_data_volume', 'max_data_volume', 'unique_ports']
    training_data = training_data.merge(
        device_stats, 
        left_on='device_id', 
        right_index=True, 
        how='left'
    )
    
    # Entraînement modèle
    print("Entraînement Isolation Forest...")
    
    # Paramètres optimisés pour production
    contamination = 0.05  # 5% d'anomalies attendues
    detector.train_model(training_data, contamination=contamination)
    
    # Évaluation modèle
    print("Évaluation modèle...")
    test_predictions = detector.detect_anomalies(training_data.sample(n=min(1000, len(training_data))))
    
    anomaly_rate = len(test_predictions) / min(1000, len(training_data))
    print(f"Taux d'anomalies détecté: {anomaly_rate:.2%}")
    
    # Sauvegarde modèle
    model_path = "models/aegislan_model.joblib"
    os.makedirs("models", exist_ok=True)
    
    model_data = {
        'model': detector.model,
        'scaler': detector.scaler,
        'encoders': detector.label_encoders,
        'features': detector.feature_columns,
        'training_stats': {
            'training_size': len(training_data),
            'contamination': contamination,
            'training_date': datetime.now().isoformat(),
            'anomaly_rate': anomaly_rate
        }
    }
    
    joblib.dump(model_data, model_path)
    print(f"Modèle sauvegardé: {model_path}")
    
    # Enregistrement en base
    model_info = {
        'model_name': 'IsolationForest_Production',
        'model_version': '1.0',
        'algorithm': 'IsolationForest',
        'parameters': {
            'contamination': contamination,
            'n_estimators': 100,
            'training_samples': len(training_data)
        },
        'training_data_start': training_data['timestamp'].min(),
        'training_data_end': training_data['timestamp'].max(),
        'training_samples': len(training_data),
        'performance_metrics': {
            'anomaly_rate': anomaly_rate
        },
        'is_active': True
    }
    
    # Stockage métadonnées modèle
    if hasattr(db_manager, 'insert_ml_model'):
        db_manager.insert_ml_model(model_info)
    
    print("Entraînement terminé avec succès!")
    return detector

if __name__ == "__main__":
    train_production_model()
```

### 3.3 Re-entraînement Automatique

#### Script de Re-entraînement Périodique
```python
# Script re-entrainement (retrain_scheduler.py)
import schedule
import time
from train_model import train_production_model
from datetime import datetime

def weekly_retrain():
    """Re-entraînement hebdomadaire automatique"""
    print(f"[{datetime.now()}] Démarrage re-entraînement hebdomadaire...")
    
    try:
        train_production_model()
        print(f"[{datetime.now()}] Re-entraînement réussi")
    except Exception as e:
        print(f"[{datetime.now()}] Erreur re-entraînement: {e}")

def setup_retrain_schedule():
    """Configuration planning re-entraînement"""
    
    # Re-entraînement tous les dimanche à 3h du matin
    schedule.every().sunday.at("03:00").do(weekly_retrain)
    
    print("Planning re-entraînement configuré (Dimanche 3h00)")
    
    # Boucle de surveillance
    while True:
        schedule.run_pending()
        time.sleep(3600)  # Vérification toutes les heures

if __name__ == "__main__":
    setup_retrain_schedule()
```

## 4. Surveillance et Monitoring Production

### 4.1 Monitoring Système

#### Script de Monitoring
```python
# Script monitoring (system_monitor.py)
import psutil
import time
from config_manager import ConfigManager, create_database_manager
from datetime import datetime

def monitor_system_health():
    """Surveillance santé système"""
    
    config = ConfigManager()
    db_manager = create_database_manager(config)
    
    while True:
        try:
            # Métriques système
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('C:')
            
            # Connexions réseau
            network_connections = len(psutil.net_connections())
            
            # Processus Streamlit
            streamlit_running = any(
                'streamlit' in p.name().lower() 
                for p in psutil.process_iter(['name'])
            )
            
            # Log événements
            system_status = {
                'timestamp': datetime.now(),
                'level': 'INFO',
                'component': 'SystemMonitor',
                'message': 'Health check',
                'details': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'disk_percent': disk.percent,
                    'network_connections': network_connections,
                    'streamlit_running': streamlit_running
                }
            }
            
            db_manager.log_system_event(**system_status)
            
            # Alertes si problèmes
            if cpu_percent > 80:
                alert = {
                    'timestamp': datetime.now(),
                    'alert_type': 'system_performance',
                    'severity': 'high',
                    'title': 'CPU élevé',
                    'message': f'Utilisation CPU: {cpu_percent}%'
                }
                db_manager.create_alert(alert)
            
            if memory.percent > 85:
                alert = {
                    'timestamp': datetime.now(),
                    'alert_type': 'system_performance',
                    'severity': 'high',
                    'title': 'Mémoire élevée',
                    'message': f'Utilisation mémoire: {memory.percent}%'
                }
                db_manager.create_alert(alert)
            
            if not streamlit_running:
                alert = {
                    'timestamp': datetime.now(),
                    'alert_type': 'application_error',
                    'severity': 'critical',
                    'title': 'Service AEGISLAN arrêté',
                    'message': 'Interface Streamlit non accessible'
                }
                db_manager.create_alert(alert)
            
            print(f"[{datetime.now()}] Health check OK - CPU: {cpu_percent}% | RAM: {memory.percent}% | Streamlit: {streamlit_running}")
            
        except Exception as e:
            print(f"Erreur monitoring: {e}")
        
        time.sleep(300)  # Vérification toutes les 5 minutes

if __name__ == "__main__":
    monitor_system_health()
```

### 4.2 Export et Rapports Automatiques

#### Script Rapports Hebdomadaires
```python
# Script rapports (weekly_reports.py)
from config_manager import ConfigManager, create_database_manager
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns

def generate_weekly_report():
    """Génération rapport hebdomadaire automatique"""
    
    config = ConfigManager()
    db_manager = create_database_manager(config)
    
    # Période: 7 derniers jours
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    print(f"Génération rapport {start_date.date()} -> {end_date.date()}")
    
    # Récupération données
    network_data = db_manager.get_network_data(hours=168)  # 7 jours
    anomalies_data = db_manager.get_anomalies(hours=168)
    system_stats = db_manager.get_system_statistics()
    
    # Calculs statistiques
    report_data = {
        'period': f"{start_date.date()} to {end_date.date()}",
        'total_devices': network_data['device_id'].nunique(),
        'total_connections': len(network_data),
        'total_volume_mb': network_data['data_volume_mb'].sum(),
        'total_anomalies': len(anomalies_data),
        'critical_anomalies': len(anomalies_data[anomalies_data['severity'] == 'Critique']),
        'top_devices': network_data.groupby('device_id')['data_volume_mb'].sum().nlargest(10),
        'top_ports': network_data.groupby('port')['data_volume_mb'].sum().nlargest(10),
        'hourly_activity': network_data.groupby(network_data['timestamp'].dt.hour)['data_volume_mb'].sum()
    }
    
    # Export CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    
    # Données réseau
    network_data.to_csv(f"exports/network_data_week_{timestamp}.csv", index=False)
    
    # Anomalies
    if not anomalies_data.empty:
        anomalies_data.to_csv(f"exports/anomalies_week_{timestamp}.csv", index=False)
    
    # Rapport JSON
    import json
    with open(f"exports/weekly_report_{timestamp}.json", 'w') as f:
        json.dump(report_data, f, indent=2, default=str)
    
    print(f"Rapport généré: exports/weekly_report_{timestamp}.json")
    
    return report_data

# Programmation automatique
import schedule

def setup_weekly_reports():
    """Configuration rapports automatiques"""
    
    # Rapport tous les lundi à 6h du matin
    schedule.every().monday.at("06:00").do(generate_weekly_report)
    
    print("Rapports hebdomadaires programmés (Lundi 6h00)")
    
    while True:
        schedule.run_pending()
        time.sleep(3600)

if __name__ == "__main__":
    # Génération rapport immédiate pour test
    generate_weekly_report()
    
    # Ou programmation automatique
    # setup_weekly_reports()
```

## 5. Accès et Utilisation

### 5.1 Accès Interface Web

**URL Locale** : http://localhost:5000
**URL Réseau** : http://[IP-SERVEUR]:5000

### 5.2 Dashboard Principal

1. **Vue d'ensemble** : Métriques temps réel
2. **Analyse Réseau** : Trafic détaillé par appareil
3. **Détection Menaces** : Anomalies et alertes
4. **Configuration** : Paramètres système
5. **Rapports** : Exports et historiques

### 5.3 Maintenance

#### Logs Système
```powershell
# Logs service Windows
Get-EventLog -LogName Application -Source "AEGISLANMonitoring" -Newest 50

# Logs Streamlit
Get-Content C:\AEGISLAN\logs\streamlit.log -Tail 100

# Logs base de données
# Localisation selon configuration PostgreSQL
```

#### Commandes Utiles
```powershell
# Redémarrage service
Restart-Service AEGISLANMonitoring

# Vérification port
Test-NetConnection -ComputerName localhost -Port 5000

# Statut base de données
Test-NetConnection -ComputerName localhost -Port 5432
```

Cette documentation complète vous permet de déployer AEGISLAN en production de manière professionnelle et sécurisée.