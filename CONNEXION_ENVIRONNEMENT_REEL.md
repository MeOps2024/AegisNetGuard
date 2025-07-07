Connexion à un Environnement Réel
Ce que fait l'IA actuellement

L'IA analyse 4 types de données :

Qui se connecte (adresses IP, MAC)

Quand (heures de connexion)

Comment (ports, protocoles utilisés)

Combien (volume de données échangées)

L’algorithme Isolation Forest :

Apprend ce qui est "normal" pour chaque appareil

Détecte quand un comportement sort de l'ordinaire

Classe les anomalies par niveau de danger

Exemples :

Imprimante active entre 8h-18h, port 9100, 50MB par jour

Serveur actif 24h/24, ports 80 et 443, 10GB par jour

PC utilisateur actif de 9h à 17h, ports web, 500MB par jour

Anomalies détectées :

Imprimante qui transfère 5GB à 3h du matin

PC utilisant un port jamais vu (ex : 1337)

Serveur silencieux pendant 6h

Connexion avec Nmap
Étape 1 : Remplacer le simulateur par Nmap

python
Copier
Modifier
import subprocess
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime

class NmapCollector:
    def __init__(self, network_range="192.168.1.0/24"):
        self.network_range = network_range
    
    def scan_network(self):
        cmd = f"nmap -sn -oX scan_results.xml {self.network_range}"
        subprocess.run(cmd, shell=True)
        return self.parse_nmap_results("scan_results.xml")
    
    def parse_nmap_results(self, xml_file):
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
Étape 2 : Modifier l’application principale

python
Copier
Modifier
from nmap_collector import NmapCollector

st.session_state.collector = NmapCollector("192.168.1.0/24")

if st.sidebar.button("Scanner le Réseau", type="primary"):
    with st.spinner("Scan Nmap en cours..."):
        st.session_state.network_data = st.session_state.collector.scan_network()
    st.sidebar.success("Scan terminé")
Connexion à des Données Réelles
Option A : Logs de routeur ou firewall

python
Copier
Modifier
def parse_router_logs(log_file):
    data = []
    with open(log_file, 'r') as f:
        for line in f:
            parts = line.split()
            data.append({
                'timestamp': pd.to_datetime(parts[0]),
                'ip_address': parts[1],
                'port': int(parts[3]),
                'protocol': parts[4],
                'data_volume_mb': random.randint(1, 1000)
            })
    return pd.DataFrame(data)
Option B : Données SNMP

python
Copier
Modifier
from pysnmp.hlapi import *

def collect_snmp_data(router_ip, community="public"):
    for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(
        SnmpEngine(),
        CommunityData(community),
        UdpTransportTarget((router_ip, 161)),
        ContextData(),
        ObjectType(ObjectIdentity('1.3.6.1.2.1.2.2.1.10')),
        lexicographicMode=False):
        
        if errorIndication or errorStatus:
            break
            
        for varBind in varBinds:
            print(' = '.join([x.prettyPrint() for x in varBind]))
Option C : Analyse de paquets (Wireshark)

python
Copier
Modifier
import pyshark
from datetime import datetime

def analyze_packets(interface="eth0", duration=60):
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
Architecture pour Environnement Réel
Structure recommandée :

arduino
Copier
Modifier
aegislan_production/
├── collectors/
│   ├── nmap_collector.py
│   ├── snmp_collector.py
│   ├── log_parser.py
│   └── packet_analyzer.py
├── database/
│   ├── db_manager.py
│   └── models.py
├── detection/
│   ├── anomaly_detector.py
│   └── alert_manager.py
├── api/
│   └── rest_api.py
├── app.py
└── config.py
Base de données SQLite

python
Copier
Modifier
import sqlite3
import pandas as pd

class DatabaseManager:
    def __init__(self, db_path="aegislan.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
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
        conn = sqlite3.connect(self.db_path)
        df.to_sql('network_data', conn, if_exists='append', index=False)
        conn.close()
    
    def get_recent_data(self, hours=24):
        conn = sqlite3.connect(self.db_path)
        query = f'''
            SELECT * FROM network_data 
            WHERE timestamp > datetime('now', '-{hours} hours')
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
Collecte Automatique
python
Copier
Modifier
import schedule
import time

def collect_and_analyze():
    collector = NmapCollector()
    data = collector.scan_network()
    
    db = DatabaseManager()
    db.insert_data(data)
    
    detector = AnomalyDetector()
    if not detector.is_trained:
        historical_data = db.get_recent_data(hours=72)
        detector.train_model(historical_data)
    
    anomalies = detector.detect_anomalies(data)
    
    if not anomalies.empty:
        send_alerts(anomalies)

schedule.every(10).minutes.do(collect_and_analyze)

while True:
    schedule.run_pending()
    time.sleep(1)
Installation sur Serveur de Production
Prérequis

bash
Copier
Modifier
sudo apt update
sudo apt install python3 python3-pip nmap wireshark-common
pip3 install streamlit pandas numpy plotly scikit-learn pyshark
Fichier de configuration

python
Copier
Modifier
NETWORK_RANGE = "192.168.1.0/24"
SCAN_INTERVAL = 600
DATABASE_PATH = "/var/lib/aegislan/data.db"
LOG_LEVEL = "INFO"
ALERT_EMAIL = "admin@entreprise.com"
WEB_PORT = 8501
Déploiement Linux (service)

ini
Copier
Modifier
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
Résumé final
L’IA reste identique, seule la source de données change

Tu peux basculer vers des données réelles : Nmap, SNMP, logs ou captures de paquets

Architecture modulaire : collecte, stockage, détection, alertes

Le système peut tourner automatiquement en tâche de fond