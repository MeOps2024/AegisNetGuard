"""
Gestionnaire PostgreSQL pour AEGISLAN - Version Production Enterprise
Remplace SQLite pour déploiements scalables avec Neon Database
"""

import psycopg2
import pandas as pd
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any

class PostgreSQLManager:
    """Gestionnaire PostgreSQL optimisé pour AEGISLAN Production"""
    
    def __init__(self, connection_string: str = None):
        """
        Initialise la connexion PostgreSQL
        
        Args:
            connection_string: URL de connexion PostgreSQL
                             Format: postgresql://user:password@host:port/database
                             Si None, utilise les variables d'environnement
        """
        self.connection_string = connection_string or self._get_connection_string()
        self.connection = None
        self._connect()
    
    def _get_connection_string(self) -> str:
        """Construit la chaîne de connexion depuis les variables d'environnement"""
        
        # Variables d'environnement standard
        host = os.getenv('PGHOST', 'localhost')
        port = os.getenv('PGPORT', '5432')
        database = os.getenv('PGDATABASE', 'aegislan')
        user = os.getenv('PGUSER', 'postgres')
        password = os.getenv('PGPASSWORD', '')
        
        # Support Neon Database (format spécial)
        if os.getenv('DATABASE_URL'):
            return os.getenv('DATABASE_URL')
        
        return f"postgresql://{user}:{password}@{host}:{port}/{database}"
    
    def _connect(self):
        """Établit la connexion à PostgreSQL"""
        try:
            self.connection = psycopg2.connect(self.connection_string)
            self.connection.autocommit = True
            print(f"✅ Connexion PostgreSQL établie")
        except psycopg2.Error as e:
            print(f"❌ Erreur connexion PostgreSQL: {e}")
            raise
    
    def init_database(self):
        """Initialise la base de données avec toutes les tables nécessaires"""
        
        tables_sql = {
            # Table principale des données réseau
            "network_data": """
                CREATE TABLE IF NOT EXISTS network_data (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                    device_id VARCHAR(100) NOT NULL,
                    ip_address INET NOT NULL,
                    mac_address MACADDR,
                    port INTEGER NOT NULL,
                    protocol VARCHAR(20) NOT NULL,
                    device_type VARCHAR(50),
                    data_volume_mb DECIMAL(10,2) NOT NULL,
                    connection_duration INTEGER,
                    bytes_sent BIGINT DEFAULT 0,
                    bytes_received BIGINT DEFAULT 0,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
                
                -- Index pour optimiser les requêtes temporelles
                CREATE INDEX IF NOT EXISTS idx_network_data_timestamp 
                ON network_data(timestamp);
                
                CREATE INDEX IF NOT EXISTS idx_network_data_device 
                ON network_data(device_id);
                
                CREATE INDEX IF NOT EXISTS idx_network_data_ip 
                ON network_data(ip_address);
            """,
            
            # Table des anomalies détectées
            "anomalies": """
                CREATE TABLE IF NOT EXISTS anomalies (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                    device_id VARCHAR(100) NOT NULL,
                    ip_address INET NOT NULL,
                    port INTEGER,
                    protocol VARCHAR(20),
                    anomaly_score DECIMAL(5,3) NOT NULL,
                    severity VARCHAR(20) NOT NULL CHECK (severity IN ('Critique', 'Élevé', 'Moyen', 'Faible')),
                    anomaly_type VARCHAR(100),
                    confidence DECIMAL(5,3),
                    data_volume_mb DECIMAL(10,2),
                    baseline_volume DECIMAL(10,2),
                    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'resolved', 'false_positive')),
                    resolved_at TIMESTAMP WITH TIME ZONE,
                    notes TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
                
                CREATE INDEX IF NOT EXISTS idx_anomalies_timestamp 
                ON anomalies(timestamp);
                
                CREATE INDEX IF NOT EXISTS idx_anomalies_severity 
                ON anomalies(severity);
                
                CREATE INDEX IF NOT EXISTS idx_anomalies_status 
                ON anomalies(status);
            """,
            
            # Table des alertes système
            "alerts": """
                CREATE TABLE IF NOT EXISTS alerts (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                    alert_type VARCHAR(50) NOT NULL,
                    severity VARCHAR(20) NOT NULL,
                    title VARCHAR(200) NOT NULL,
                    message TEXT NOT NULL,
                    source_component VARCHAR(50),
                    affected_devices TEXT[], -- Array PostgreSQL
                    anomaly_id INTEGER REFERENCES anomalies(id),
                    status VARCHAR(20) DEFAULT 'open' CHECK (status IN ('open', 'acknowledged', 'resolved')),
                    acknowledged_by VARCHAR(100),
                    acknowledged_at TIMESTAMP WITH TIME ZONE,
                    resolved_at TIMESTAMP WITH TIME ZONE,
                    resolution_notes TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
                
                CREATE INDEX IF NOT EXISTS idx_alerts_timestamp 
                ON alerts(timestamp);
                
                CREATE INDEX IF NOT EXISTS idx_alerts_status 
                ON alerts(status);
            """,
            
            # Table des événements système
            "system_logs": """
                CREATE TABLE IF NOT EXISTS system_logs (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                    level VARCHAR(20) NOT NULL CHECK (level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')),
                    component VARCHAR(50) NOT NULL,
                    event_type VARCHAR(50),
                    message TEXT NOT NULL,
                    details JSONB, -- JSON natif PostgreSQL
                    user_id VARCHAR(100),
                    session_id VARCHAR(100),
                    ip_address INET,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
                
                CREATE INDEX IF NOT EXISTS idx_system_logs_timestamp 
                ON system_logs(timestamp);
                
                CREATE INDEX IF NOT EXISTS idx_system_logs_level 
                ON system_logs(level);
                
                CREATE INDEX IF NOT EXISTS idx_system_logs_component 
                ON system_logs(component);
                
                -- Index GIN pour recherche dans JSONB
                CREATE INDEX IF NOT EXISTS idx_system_logs_details 
                ON system_logs USING GIN(details);
            """,
            
            # Table des appareils découverts
            "devices": """
                CREATE TABLE IF NOT EXISTS devices (
                    id SERIAL PRIMARY KEY,
                    device_id VARCHAR(100) UNIQUE NOT NULL,
                    ip_address INET NOT NULL,
                    mac_address MACADDR,
                    hostname VARCHAR(200),
                    device_type VARCHAR(50),
                    vendor VARCHAR(100),
                    os_info VARCHAR(200),
                    first_seen TIMESTAMP WITH TIME ZONE NOT NULL,
                    last_seen TIMESTAMP WITH TIME ZONE NOT NULL,
                    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'unknown')),
                    open_ports INTEGER[],
                    services JSONB,
                    risk_score INTEGER DEFAULT 0 CHECK (risk_score >= 0 AND risk_score <= 100),
                    notes TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
                
                CREATE INDEX IF NOT EXISTS idx_devices_ip 
                ON devices(ip_address);
                
                CREATE INDEX IF NOT EXISTS idx_devices_last_seen 
                ON devices(last_seen);
            """,
            
            # Table de configuration IA/ML
            "ml_models": """
                CREATE TABLE IF NOT EXISTS ml_models (
                    id SERIAL PRIMARY KEY,
                    model_name VARCHAR(100) NOT NULL,
                    model_version VARCHAR(20) NOT NULL,
                    algorithm VARCHAR(50) NOT NULL,
                    parameters JSONB NOT NULL,
                    training_data_start TIMESTAMP WITH TIME ZONE,
                    training_data_end TIMESTAMP WITH TIME ZONE,
                    training_samples INTEGER,
                    performance_metrics JSONB,
                    is_active BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    
                    UNIQUE(model_name, model_version)
                );
            """
        }
        
        try:
            cursor = self.connection.cursor()
            
            for table_name, sql in tables_sql.items():
                print(f"Création table {table_name}...")
                cursor.execute(sql)
            
            cursor.close()
            print("✅ Base de données PostgreSQL initialisée avec succès")
            
        except psycopg2.Error as e:
            print(f"❌ Erreur initialisation base: {e}")
            raise
    
    def insert_network_data(self, data: Dict[str, Any]) -> int:
        """
        Insère des données réseau en lot optimisé
        
        Args:
            data: Dict ou DataFrame avec les données réseau
            
        Returns:
            Nombre de lignes insérées
        """
        
        if isinstance(data, pd.DataFrame):
            data_list = data.to_dict('records')
        elif isinstance(data, dict):
            data_list = [data]
        else:
            data_list = data
        
        insert_sql = """
            INSERT INTO network_data (
                timestamp, device_id, ip_address, mac_address, port, protocol,
                device_type, data_volume_mb, connection_duration, bytes_sent, bytes_received
            ) VALUES (
                %(timestamp)s, %(device_id)s, %(ip_address)s, %(mac_address)s,
                %(port)s, %(protocol)s, %(device_type)s, %(data_volume_mb)s,
                %(connection_duration)s, %(bytes_sent)s, %(bytes_received)s
            )
        """
        
        try:
            cursor = self.connection.cursor()
            cursor.executemany(insert_sql, data_list)
            inserted_count = cursor.rowcount
            cursor.close()
            
            return inserted_count
            
        except psycopg2.Error as e:
            print(f"❌ Erreur insertion données réseau: {e}")
            raise
    
    def insert_anomaly(self, anomaly_data: Dict[str, Any]) -> int:
        """Insère une anomalie détectée"""
        
        insert_sql = """
            INSERT INTO anomalies (
                timestamp, device_id, ip_address, port, protocol, anomaly_score,
                severity, anomaly_type, confidence, data_volume_mb, baseline_volume
            ) VALUES (
                %(timestamp)s, %(device_id)s, %(ip_address)s, %(port)s, %(protocol)s,
                %(anomaly_score)s, %(severity)s, %(anomaly_type)s, %(confidence)s,
                %(data_volume_mb)s, %(baseline_volume)s
            ) RETURNING id
        """
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(insert_sql, anomaly_data)
            anomaly_id = cursor.fetchone()[0]
            cursor.close()
            
            return anomaly_id
            
        except psycopg2.Error as e:
            print(f"❌ Erreur insertion anomalie: {e}")
            raise
    
    def get_network_data(self, hours: int = 24, limit: int = None, 
                        device_id: str = None) -> pd.DataFrame:
        """
        Récupère les données réseau récentes avec filtres avancés
        
        Args:
            hours: Nombre d'heures à récupérer
            limit: Limite nombre de résultats
            device_id: Filtrer par appareil spécifique
            
        Returns:
            DataFrame avec les données réseau
        """
        
        base_sql = """
            SELECT timestamp, device_id, ip_address, mac_address, port, protocol,
                   device_type, data_volume_mb, connection_duration, bytes_sent, bytes_received
            FROM network_data
            WHERE timestamp >= NOW() - INTERVAL '%s hours'
        """
        
        params = [hours]
        
        if device_id:
            base_sql += " AND device_id = %s"
            params.append(device_id)
        
        base_sql += " ORDER BY timestamp DESC"
        
        if limit:
            base_sql += " LIMIT %s"
            params.append(limit)
        
        try:
            return pd.read_sql(base_sql, self.connection, params=params)
        except psycopg2.Error as e:
            print(f"❌ Erreur récupération données: {e}")
            raise
    
    def get_anomalies(self, hours: int = 24, status: str = 'active', 
                     severity: str = None) -> pd.DataFrame:
        """
        Récupère les anomalies avec filtres
        
        Args:
            hours: Période à analyser
            status: Statut des anomalies (active, resolved, false_positive)
            severity: Niveau de criticité
            
        Returns:
            DataFrame avec les anomalies
        """
        
        base_sql = """
            SELECT id, timestamp, device_id, ip_address, port, protocol,
                   anomaly_score, severity, anomaly_type, confidence,
                   data_volume_mb, baseline_volume, status
            FROM anomalies
            WHERE timestamp >= NOW() - INTERVAL '%s hours'
        """
        
        params = [hours]
        
        if status:
            base_sql += " AND status = %s"
            params.append(status)
        
        if severity:
            base_sql += " AND severity = %s"
            params.append(severity)
        
        base_sql += " ORDER BY anomaly_score DESC, timestamp DESC"
        
        try:
            return pd.read_sql(base_sql, self.connection, params=params)
        except psycopg2.Error as e:
            print(f"❌ Erreur récupération anomalies: {e}")
            raise
    
    def get_device_statistics(self, device_id: str, days: int = 7) -> Dict[str, Any]:
        """Statistiques détaillées pour un appareil"""
        
        stats_sql = """
            SELECT 
                COUNT(*) as total_connections,
                SUM(data_volume_mb) as total_volume,
                AVG(data_volume_mb) as avg_volume,
                MAX(data_volume_mb) as max_volume,
                COUNT(DISTINCT port) as unique_ports,
                COUNT(DISTINCT protocol) as unique_protocols,
                MIN(timestamp) as first_activity,
                MAX(timestamp) as last_activity
            FROM network_data
            WHERE device_id = %s 
            AND timestamp >= NOW() - INTERVAL '%s days'
        """
        
        anomalies_sql = """
            SELECT severity, COUNT(*) as count
            FROM anomalies
            WHERE device_id = %s 
            AND timestamp >= NOW() - INTERVAL '%s days'
            GROUP BY severity
        """
        
        try:
            cursor = self.connection.cursor()
            
            # Statistiques générales
            cursor.execute(stats_sql, (device_id, days))
            stats = dict(zip([desc[0] for desc in cursor.description], cursor.fetchone()))
            
            # Statistiques anomalies
            cursor.execute(anomalies_sql, (device_id, days))
            anomaly_stats = {row[0]: row[1] for row in cursor.fetchall()}
            
            cursor.close()
            
            return {
                'device_stats': stats,
                'anomaly_stats': anomaly_stats
            }
            
        except psycopg2.Error as e:
            print(f"❌ Erreur statistiques appareil: {e}")
            raise
    
    def create_alert(self, alert_data: Dict[str, Any]) -> int:
        """Crée une nouvelle alerte système"""
        
        insert_sql = """
            INSERT INTO alerts (
                timestamp, alert_type, severity, title, message,
                source_component, affected_devices, anomaly_id
            ) VALUES (
                %(timestamp)s, %(alert_type)s, %(severity)s, %(title)s,
                %(message)s, %(source_component)s, %(affected_devices)s, %(anomaly_id)s
            ) RETURNING id
        """
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(insert_sql, alert_data)
            alert_id = cursor.fetchone()[0]
            cursor.close()
            
            return alert_id
            
        except psycopg2.Error as e:
            print(f"❌ Erreur création alerte: {e}")
            raise
    
    def log_system_event(self, level: str, component: str, message: str, 
                        details: Dict = None, event_type: str = None):
        """Enregistre un événement système avec détails JSON"""
        
        insert_sql = """
            INSERT INTO system_logs (
                timestamp, level, component, event_type, message, details
            ) VALUES (
                NOW(), %s, %s, %s, %s, %s
            )
        """
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(insert_sql, (
                level, component, event_type, message, 
                json.dumps(details) if details else None
            ))
            cursor.close()
            
        except psycopg2.Error as e:
            print(f"❌ Erreur log système: {e}")
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Statistiques générales du système"""
        
        stats_sql = """
            SELECT 
                (SELECT COUNT(*) FROM network_data WHERE timestamp >= NOW() - INTERVAL '24 hours') as connections_24h,
                (SELECT COUNT(*) FROM anomalies WHERE timestamp >= NOW() - INTERVAL '24 hours' AND status = 'active') as active_anomalies,
                (SELECT COUNT(DISTINCT device_id) FROM network_data WHERE timestamp >= NOW() - INTERVAL '24 hours') as active_devices,
                (SELECT SUM(data_volume_mb) FROM network_data WHERE timestamp >= NOW() - INTERVAL '24 hours') as total_volume_24h,
                (SELECT COUNT(*) FROM alerts WHERE status = 'open') as open_alerts
        """
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(stats_sql)
            stats = dict(zip([desc[0] for desc in cursor.description], cursor.fetchone()))
            cursor.close()
            
            return stats
            
        except psycopg2.Error as e:
            print(f"❌ Erreur statistiques système: {e}")
            raise
    
    def cleanup_old_data(self, days: int = 90):
        """Nettoie les anciennes données selon politique de rétention"""
        
        cleanup_queries = [
            ("network_data", f"DELETE FROM network_data WHERE timestamp < NOW() - INTERVAL '{days} days'"),
            ("anomalies", f"DELETE FROM anomalies WHERE timestamp < NOW() - INTERVAL '{days} days' AND status = 'resolved'"),
            ("system_logs", f"DELETE FROM system_logs WHERE timestamp < NOW() - INTERVAL '{days} days' AND level NOT IN ('ERROR', 'CRITICAL')"),
            ("alerts", f"DELETE FROM alerts WHERE timestamp < NOW() - INTERVAL '{days} days' AND status = 'resolved'")
        ]
        
        try:
            cursor = self.connection.cursor()
            
            for table_name, query in cleanup_queries:
                cursor.execute(query)
                deleted_count = cursor.rowcount
                print(f"🧹 {table_name}: {deleted_count} anciens enregistrements supprimés")
            
            cursor.close()
            
        except psycopg2.Error as e:
            print(f"❌ Erreur nettoyage données: {e}")
    
    def export_data(self, table_name: str, start_date: str = None, 
                   end_date: str = None, format: str = 'csv') -> str:
        """
        Exporte les données pour analyse externe
        
        Args:
            table_name: Table à exporter
            start_date: Date début (YYYY-MM-DD)
            end_date: Date fin (YYYY-MM-DD)
            format: Format export (csv, json, parquet)
            
        Returns:
            Chemin du fichier exporté
        """
        
        base_sql = f"SELECT * FROM {table_name}"
        params = []
        
        if start_date or end_date:
            base_sql += " WHERE"
            if start_date:
                base_sql += " timestamp >= %s"
                params.append(start_date)
            if end_date:
                if start_date:
                    base_sql += " AND"
                base_sql += " timestamp <= %s"
                params.append(end_date)
        
        try:
            df = pd.read_sql(base_sql, self.connection, params=params)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"export_{table_name}_{timestamp}.{format}"
            
            if format == 'csv':
                df.to_csv(filename, index=False)
            elif format == 'json':
                df.to_json(filename, orient='records', date_format='iso')
            elif format == 'parquet':
                df.to_parquet(filename, index=False)
            
            return filename
            
        except psycopg2.Error as e:
            print(f"❌ Erreur export données: {e}")
            raise
    
    def get_database_size(self) -> Dict[str, Any]:
        """Informations sur la taille de la base"""
        
        size_sql = """
            SELECT 
                pg_size_pretty(pg_database_size(current_database())) as database_size,
                schemaname,
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as table_size,
                pg_total_relation_size(schemaname||'.'||tablename) as table_size_bytes
            FROM pg_tables 
            WHERE schemaname = 'public'
            ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
        """
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(size_sql)
            
            results = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            cursor.close()
            
            return {
                'database_size': results[0][0] if results else 'Unknown',
                'tables': [dict(zip(columns[1:], row[1:])) for row in results]
            }
            
        except psycopg2.Error as e:
            print(f"❌ Erreur taille base: {e}")
            raise
    
    def close(self):
        """Ferme la connexion à la base"""
        if self.connection:
            self.connection.close()
            print("🔒 Connexion PostgreSQL fermée")

# Exemple d'utilisation et migration depuis SQLite
class DatabaseMigration:
    """Utilitaire de migration SQLite vers PostgreSQL"""
    
    def __init__(self, sqlite_path: str, postgresql_manager: PostgreSQLManager):
        self.sqlite_path = sqlite_path
        self.pg_manager = postgresql_manager
    
    def migrate_data(self):
        """Migre toutes les données de SQLite vers PostgreSQL"""
        
        import sqlite3
        
        # Tables à migrer
        tables_to_migrate = [
            'network_data', 'anomalies', 'alerts', 'system_logs'
        ]
        
        try:
            sqlite_conn = sqlite3.connect(self.sqlite_path)
            
            for table_name in tables_to_migrate:
                print(f"Migration table {table_name}...")
                
                # Lire depuis SQLite
                df = pd.read_sql(f"SELECT * FROM {table_name}", sqlite_conn)
                
                if not df.empty:
                    # Adapter les colonnes si nécessaire
                    if table_name == 'network_data':
                        df = self._adapt_network_data(df)
                    elif table_name == 'anomalies':
                        df = self._adapt_anomalies(df)
                    
                    # Insérer dans PostgreSQL
                    self.pg_manager.insert_network_data(df)
                    print(f"✅ {len(df)} enregistrements migrés pour {table_name}")
                else:
                    print(f"⚠️ Table {table_name} vide")
            
            sqlite_conn.close()
            print("🎉 Migration complète vers PostgreSQL")
            
        except Exception as e:
            print(f"❌ Erreur migration: {e}")
            raise
    
    def _adapt_network_data(self, df):
        """Adapte les données réseau pour PostgreSQL"""
        # Conversion des types si nécessaire
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    
    def _adapt_anomalies(self, df):
        """Adapte les données d'anomalies pour PostgreSQL"""
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df

if __name__ == "__main__":
    # Exemple d'utilisation
    
    # Initialisation avec Neon Database (ou PostgreSQL local)
    db_manager = PostgreSQLManager()
    
    # Initialisation des tables
    db_manager.init_database()
    
    # Test d'insertion
    sample_data = {
        'timestamp': datetime.now(),
        'device_id': 'WS001',
        'ip_address': '192.168.1.100',
        'port': 443,
        'protocol': 'HTTPS',
        'device_type': 'Workstation',
        'data_volume_mb': 25.5
    }
    
    db_manager.insert_network_data(sample_data)
    
    # Récupération des données
    recent_data = db_manager.get_network_data(hours=1)
    print(f"Données récentes: {len(recent_data)} enregistrements")
    
    # Fermeture
    db_manager.close()