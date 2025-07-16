import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import json
import os

class DatabaseManager:
    """Gestionnaire de base de données pour AEGISLAN"""
    
    def __init__(self, db_path="aegislan_production.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialise la base de données avec les tables nécessaires"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table pour les données réseau
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS network_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                device_id TEXT NOT NULL,
                ip_address TEXT NOT NULL,
                mac_address TEXT,
                device_type TEXT,
                port INTEGER,
                protocol TEXT,
                data_volume_mb REAL,
                connection_duration INTEGER,
                is_anomaly BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table pour les anomalies détectées
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS anomalies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                device_id TEXT NOT NULL,
                anomaly_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                anomaly_score REAL,
                description TEXT,
                status TEXT DEFAULT 'active',
                resolved_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table pour les modèles IA
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT NOT NULL,
                model_version TEXT,
                training_data_size INTEGER,
                contamination_rate REAL,
                features_count INTEGER,
                accuracy_score REAL,
                model_path TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Table pour les logs système
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                log_level TEXT NOT NULL,
                component TEXT NOT NULL,
                message TEXT NOT NULL,
                details TEXT
            )
        ''')
        
        # Table pour les alertes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                device_id TEXT,
                status TEXT DEFAULT 'open',
                acknowledged_by TEXT,
                acknowledged_at DATETIME,
                resolved_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Index pour les performances
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_network_timestamp ON network_data(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_network_device ON network_data(device_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_anomalies_timestamp ON anomalies(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp)')
        
        conn.commit()
        conn.close()
        
        self.log_system_event("INFO", "Database", "Database initialized successfully")
    
    def insert_network_data(self, data):
        """Insère des données réseau dans la base"""
        conn = sqlite3.connect(self.db_path)
        
        if isinstance(data, pd.DataFrame):
            data.to_sql('network_data', conn, if_exists='append', index=False)
        else:
            # Données individuelles
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO network_data 
                (timestamp, device_id, ip_address, mac_address, device_type, port, protocol, data_volume_mb, is_anomaly)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('timestamp', datetime.now()),
                data['device_id'],
                data['ip_address'],
                data.get('mac_address', ''),
                data.get('device_type', 'unknown'),
                data.get('port', 0),
                data.get('protocol', 'unknown'),
                data.get('data_volume_mb', 0),
                data.get('is_anomaly', False)
            ))
            conn.commit()
        
        conn.close()
    
    def insert_anomaly(self, anomaly_data):
        """Insère une anomalie détectée"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO anomalies 
            (timestamp, device_id, anomaly_type, severity, anomaly_score, description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            anomaly_data['timestamp'],
            anomaly_data['device_id'],
            anomaly_data.get('anomaly_type', 'behavioral'),
            anomaly_data['severity'],
            anomaly_data['anomaly_score'],
            anomaly_data.get('description', '')
        ))
        
        conn.commit()
        conn.close()
    
    def get_network_data(self, hours=24, limit=None):
        """Récupère les données réseau récentes"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT * FROM network_data 
            WHERE timestamp > datetime('now', '-{} hours')
            ORDER BY timestamp DESC
        '''.format(hours)
        
        if limit:
            query += f' LIMIT {limit}'
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df
    
    def get_anomalies(self, hours=24, status='active'):
        """Récupère les anomalies récentes"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT * FROM anomalies 
            WHERE timestamp > datetime('now', '-{} hours')
            AND status = ?
            ORDER BY timestamp DESC
        '''.format(hours)
        
        df = pd.read_sql_query(query, conn, params=(status,))
        conn.close()
        
        return df
    
    def get_device_statistics(self, device_id, days=7):
        """Statistiques pour un appareil spécifique"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT 
                COUNT(*) as total_connections,
                AVG(data_volume_mb) as avg_volume,
                MAX(data_volume_mb) as max_volume,
                COUNT(DISTINCT port) as unique_ports,
                COUNT(DISTINCT protocol) as unique_protocols,
                SUM(CASE WHEN is_anomaly = 1 THEN 1 ELSE 0 END) as anomaly_count
            FROM network_data 
            WHERE device_id = ?
            AND timestamp > datetime('now', '-{} days')
        '''.format(days)
        
        cursor = conn.cursor()
        cursor.execute(query, (device_id,))
        result = cursor.fetchone()
        conn.close()
        
        return {
            'total_connections': result[0],
            'avg_volume': result[1],
            'max_volume': result[2],
            'unique_ports': result[3],
            'unique_protocols': result[4],
            'anomaly_count': result[5]
        }
    
    def create_alert(self, alert_data):
        """Crée une nouvelle alerte"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO alerts 
            (timestamp, alert_type, severity, title, description, device_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            alert_data['timestamp'],
            alert_data['alert_type'],
            alert_data['severity'],
            alert_data['title'],
            alert_data.get('description', ''),
            alert_data.get('device_id', '')
        ))
        
        conn.commit()
        conn.close()
    
    def log_system_event(self, level, component, message, details=None):
        """Enregistre un événement système"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO system_logs (log_level, component, message, details)
            VALUES (?, ?, ?, ?)
        ''', (level, component, message, json.dumps(details) if details else None))
        
        conn.commit()
        conn.close()
    
    def get_system_statistics(self):
        """Statistiques générales du système"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Statistiques réseau
        cursor.execute('''
            SELECT 
                COUNT(*) as total_connections,
                COUNT(DISTINCT device_id) as unique_devices,
                SUM(data_volume_mb) as total_volume,
                COUNT(DISTINCT port) as unique_ports
            FROM network_data 
            WHERE timestamp > datetime('now', '-24 hours')
        ''')
        network_stats = cursor.fetchone()
        
        # Statistiques anomalies
        cursor.execute('''
            SELECT 
                COUNT(*) as total_anomalies,
                COUNT(CASE WHEN severity = 'Critique' THEN 1 END) as critical_count,
                COUNT(CASE WHEN severity = 'Élevé' THEN 1 END) as high_count,
                COUNT(CASE WHEN severity = 'Moyen' THEN 1 END) as medium_count,
                COUNT(CASE WHEN severity = 'Faible' THEN 1 END) as low_count
            FROM anomalies 
            WHERE timestamp > datetime('now', '-24 hours')
            AND status = 'active'
        ''')
        anomaly_stats = cursor.fetchone()
        
        conn.close()
        
        return {
            'network': {
                'total_connections': network_stats[0],
                'unique_devices': network_stats[1],
                'total_volume': network_stats[2],
                'unique_ports': network_stats[3]
            },
            'anomalies': {
                'total': anomaly_stats[0],
                'critical': anomaly_stats[1],
                'high': anomaly_stats[2],
                'medium': anomaly_stats[3],
                'low': anomaly_stats[4]
            }
        }
    
    def cleanup_old_data(self, days=30):
        """Nettoie les anciennes données"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Supprimer les données réseau anciennes
        cursor.execute('''
            DELETE FROM network_data 
            WHERE timestamp < datetime('now', '-{} days')
        '''.format(days))
        
        # Supprimer les logs anciens
        cursor.execute('''
            DELETE FROM system_logs 
            WHERE timestamp < datetime('now', '-{} days')
        '''.format(days))
        
        conn.commit()
        conn.close()
        
        self.log_system_event("INFO", "Database", f"Cleaned up data older than {days} days")
    
    def export_data(self, table_name, start_date=None, end_date=None):
        """Exporte les données pour analyse"""
        conn = sqlite3.connect(self.db_path)
        
        if start_date and end_date:
            query = f'''
                SELECT * FROM {table_name} 
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp
            '''
            df = pd.read_sql_query(query, conn, params=(start_date, end_date))
        else:
            query = f'SELECT * FROM {table_name} ORDER BY timestamp'
            df = pd.read_sql_query(query, conn)
        
        conn.close()
        return df
    
    def get_database_size(self):
        """Taille de la base de données"""
        if os.path.exists(self.db_path):
            size_bytes = os.path.getsize(self.db_path)
            size_mb = size_bytes / (1024 * 1024)
            return f"{size_mb:.2f} MB"
        return "0 MB"