# Connexion à un Environnement Réel

## Ce que fait l'IA actuellement

**L'IA analyse 4 types de données :**
1. **Qui** se connecte (adresses IP, MAC)
2. **Quand** (heures de connexion)
3. **Comment** (ports, protocoles utilisés)
4. **Combien** (volume de données échangées)

**L'algorithme Isolation Forest :**
- Apprend ce qui est "normal" pour chaque appareil
- Détecte quand quelque chose sort de l'ordinaire
- Classe les anomalies par niveau de danger

## Connexion avec Nmap

### Étape 1 : Remplacer le simulateur par Nmap

```python
# Nouveau fichier : nmap_collector.py
import subprocess
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime

class NmapCollector:
    def __init__(self, network_range="192.168.1.0/24"):
        self.network_range = network_range
    
    def scan_network(self):
        """Scan réseau avec Nmap"""
        cmd = f"nmap -sn -oX scan_results.xml {self.network_range}"
        subprocess.run(cmd, shell=True)
        
        return self.parse_nmap_results("scan_results.xml")
    
    def parse_nmap_results(self, xml_file):
        """Convertit résultats Nmap en données pour l'IA"""
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        devices = []
        for host in root.findall("host"):
            ip = host.find("address[@addrtype='ipv4']").get("addr")
            mac = host.find("address[@addrtype='mac']")
            mac_addr = mac.get("addr") if mac is not None else "Unknown"
            
            devices.append({
                'timestamp': datetime.now(),
                'ip_address': ip,
                'mac_address': mac_addr,
                'device_id': f"device_{ip.split('.')[-1]}",
                'device_type': 'unknown',
                'port': 0,
                'protocol': 'ICMP',
                'data_volume_mb': 1,
                'is_anomaly': False
            })
        
        return pd.DataFrame(devices)
```

### Étape 2 : Modifier app.py

```python
# Remplacer dans app.py
from nmap_collector import NmapCollector

# Remplacer cette ligne :
# st.session_state.simulator = NetworkDataSimulator()
# Par :
st.session_state.collector = NmapCollector("192.168.1.0/24")

# Remplacer le bouton génération par :
if st.sidebar.button("Scanner le Réseau", type="primary"):
    with st.spinner("Scan Nmap en cours..."):
        st.session_state.network_data = st.session_state.collector.scan_network()
    st.sidebar.success("Scan terminé!")
```

## Connexion avec des Données Réseau Réelles

### Option A : Logs de Routeur/Firewall

```python
# log_parser.py
def parse_router_logs(log_file):
    """Parse logs de routeur/firewall"""
    data = []
    with open(log_file, 'r') as f:
        for line in f:
            # Exemple format : timestamp src_ip dst_ip port protocol
            parts = line.split()
            data.append({
                'timestamp': pd.to_datetime(parts[0]),
                'ip_address': parts[1],
                'port': int(parts[3]),
                'protocol': parts[4],
                'data_volume_mb': random.randint(1, 1000)
            })
    return pd.DataFrame(data)
```

### Option B : API SNMP

```python
# snmp_collector.py
from pysnmp.hlapi import *

def collect_snmp_data(router_ip, community="public"):
    """Collecte données via SNMP"""
    for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(
        SnmpEngine(),
        CommunityData(community),
        UdpTransportTarget((router_ip, 161)),
        ContextData(),
        ObjectType(ObjectIdentity('1.3.6.1.2.1.2.2.1.10')),  # Interface octets
        lexicographicMode=False):
        
        if errorIndication:
            break
        if errorStatus:
            break
            
        for varBind in varBinds:
            print(' = '.join([x.prettyPrint() for x in varBind]))
```

### Option C : Wireshark/tcpdump

```python
# packet_analyzer.py
import pyshark

def analyze_packets(interface="eth0", duration=60):
    """Capture paquets réseau"""
    capture = pyshark.LiveCapture(interface=interface)
    capture.sniff(timeout=duration)
    
    data = []
    for packet in capture:
        if hasattr(packet, 'ip'):
            data.append({
                'timestamp': datetime.now(),
                'src_ip': packet.ip.src,
                'dst_ip': packet.ip.dst,
                'protocol': packet.transport_layer,
                'port': getattr(packet[packet.transport_layer], 'dstport', 0),
                'size': int(packet.length)
            })
    
    return pd.DataFrame(data)
```

## Architecture pour Environnement Réel

### Structure Recommandée

```
aegislan_production/
├── collectors/
│   ├── nmap_collector.py      # Scan réseau
│   ├── snmp_collector.py      # Données SNMP
│   ├── log_parser.py          # Parse logs
│   └── packet_analyzer.py     # Analyse paquets
├── database/
│   ├── db_manager.py          # Gestion base de données
│   └── models.py              # Modèles de données
├── detection/
│   ├── anomaly_detector.py    # IA existante
│   └── alert_manager.py       # Gestion alertes
├── api/
│   └── rest_api.py            # API REST
├── app.py                     # Interface Streamlit
└── config.py                  # Configuration
```

### Base de Données Persistante

```python
# db_manager.py
import sqlite3
import pandas as pd

class DatabaseManager:
    def __init__(self, db_path="aegislan.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Créer tables"""
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS network_data (
                id INTEGER PRIMARY KEY,
                timestamp DATETIME,
                device_id TEXT,
                ip_address TEXT,
                mac_address TEXT,
                port INTEGER,
                protocol TEXT,
                data_volume_mb REAL,
                is_anomaly BOOLEAN
            )
        ''')
        conn.close()
    
    def insert_data(self, df):
        """Insérer données réseau"""
        conn = sqlite3.connect(self.db_path)
        df.to_sql('network_data', conn, if_exists='append', index=False)
        conn.close()
    
    def get_recent_data(self, hours=24):
        """Récupérer données récentes"""
        conn = sqlite3.connect(self.db_path)
        query = f'''
            SELECT * FROM network_data 
            WHERE timestamp > datetime('now', '-{hours} hours')
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
```

### Collecte Automatique

```python
# scheduler.py
import schedule
import time

def collect_and_analyze():
    """Collecte et analyse automatique"""
    # 1. Collecter données
    collector = NmapCollector()
    data = collector.scan_network()
    
    # 2. Stocker en base
    db = DatabaseManager()
    db.insert_data(data)
    
    # 3. Analyser avec IA
    detector = AnomalyDetector()
    if not detector.is_trained:
        historical_data = db.get_recent_data(hours=72)
        detector.train_model(historical_data)
    
    anomalies = detector.detect_anomalies(data)
    
    # 4. Envoyer alertes
    if not anomalies.empty:
        send_alerts(anomalies)

# Planifier exécution
schedule.every(10).minutes.do(collect_and_analyze)

while True:
    schedule.run_pending()
    time.sleep(1)
```

## Installation sur Serveur de Production

### Prérequis
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip nmap wireshark-common
pip3 install streamlit pandas numpy plotly scikit-learn pyshark

# Windows
# Installer Nmap depuis nmap.org
# Installer WinPcap/Npcap
pip install streamlit pandas numpy plotly scikit-learn pyshark
```

### Configuration Sécurisée
```python
# config.py
NETWORK_RANGE = "192.168.1.0/24"
SCAN_INTERVAL = 600  # 10 minutes
DATABASE_PATH = "/var/lib/aegislan/data.db"
LOG_LEVEL = "INFO"
ALERT_EMAIL = "admin@entreprise.com"
WEB_PORT = 8501
```

### Déploiement Service Linux
```bash
# /etc/systemd/system/aegislan.service
[Unit]
Description=AEGISLAN Network Anomaly Detection
After=network.target

[Service]
Type=simple
User=aegislan
WorkingDirectory=/opt/aegislan
ExecStart=/usr/bin/python3 app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## Résumé Simple

**Actuellement :** L'IA analyse des données simulées
**Pour du réel :** Remplacer le simulateur par Nmap/SNMP/logs
**L'IA reste identique :** Elle analyse toujours les mêmes patterns
**Ajouts nécessaires :** Base de données + collecte automatique + alertes

L'IA fait exactement la même chose, elle reçoit juste de vraies données au lieu de données simulées.