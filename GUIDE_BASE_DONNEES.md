# GUIDE COMPLET BASE DE DONNÉES AEGISLAN

## Vue d'ensemble Stratégie Base de Données

AEGISLAN utilise une approche progressive pour la gestion des données : SQLite pour le développement et les tests, PostgreSQL pour la production. Cette stratégie permet un déploiement flexible selon l'échelle et les besoins.

## 1. Choix Technologiques et Justifications

### SQLite - Base de Développement

#### Pourquoi SQLite ?
- **Simplicité maximale** : Aucune installation serveur requise
- **Fichier unique** : Base complète dans un seul fichier .db
- **Performance locale** : Excellente pour lectures intensives
- **Déploiement facile** : Copie simple du fichier .db
- **Développement rapide** : Pas de configuration réseau
- **ACID compliant** : Transactions sûres
- **Intégration Python native** : Module sqlite3 inclus

#### Limitations SQLite
- **Concurrence limitée** : Un seul écrivain simultané
- **Taille maximale** : Recommandé < 1TB (pratiquement ~100GB)
- **Fonctionnalités avancées** : Pas de types spécialisés réseau
- **Scalabilité** : Pas de distribution horizontale

#### Utilisation dans AEGISLAN
```python
# Fichier: database_manager.py
class DatabaseManager:
    def __init__(self, db_path="aegislan_production.db"):
        self.db_path = db_path
        self.connection = sqlite3.connect(db_path, check_same_thread=False)
```

### PostgreSQL - Base de Production

#### Pourquoi PostgreSQL ?
- **Scalabilité enterprise** : Gestion de téraoctets de données
- **Concurrence élevée** : MVCC (Multi-Version Concurrency Control)
- **Types avancés** : INET, MACADDR, JSONB, Arrays
- **Index sophistiqués** : GiST, GIN, BRIN pour performance
- **Réplication** : Master-slave, streaming replication
- **Extensibilité** : Extensions comme PostGIS, pg_stat_statements
- **Conformité SQL** : Standard SQL le plus complet
- **Écosystème mature** : Outils de monitoring, backup, tuning

#### Types de Données Spécialisés
```sql
-- Types réseau natifs PostgreSQL
ip_address INET,              -- Adresses IP avec validation
mac_address MACADDR,          -- Adresses MAC avec validation
port_range INT4RANGE,         -- Plages de ports
network_cidr CIDR,            -- Notation CIDR pour réseaux

-- Types avancés
metadata JSONB,               -- JSON binaire indexable
port_list INTEGER[],          -- Arrays natifs
timestamps TIMESTAMP WITH TIME ZONE  -- Gestion timezone
```

## 2. Architecture des Tables Détaillée

### Table `network_data` - Données Réseau Principales

#### Structure SQLite
```sql
CREATE TABLE network_data (
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
    bytes_sent INTEGER DEFAULT 0,
    bytes_received INTEGER DEFAULT 0,
    is_anomaly BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Index pour performance
    INDEX idx_network_timestamp (timestamp),
    INDEX idx_network_device (device_id),
    INDEX idx_network_ip (ip_address)
);
```

#### Structure PostgreSQL Optimisée
```sql
CREATE TABLE network_data (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    device_id VARCHAR(100) NOT NULL,
    ip_address INET NOT NULL,                    -- Type réseau natif
    mac_address MACADDR,                         -- Type MAC natif
    port INTEGER NOT NULL CHECK (port >= 0 AND port <= 65535),
    protocol VARCHAR(20) NOT NULL,
    device_type VARCHAR(50),
    data_volume_mb DECIMAL(10,2) NOT NULL,
    connection_duration INTEGER,
    bytes_sent BIGINT DEFAULT 0,
    bytes_received BIGINT DEFAULT 0,
    session_id UUID DEFAULT gen_random_uuid(),   -- Session unique
    metadata JSONB,                              -- Métadonnées flexibles
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index composites pour requêtes fréquentes
CREATE INDEX idx_network_data_timestamp_device ON network_data(timestamp, device_id);
CREATE INDEX idx_network_data_ip_port ON network_data(ip_address, port);
CREATE INDEX idx_network_data_time_range ON network_data USING BRIN(timestamp);

-- Index GIN pour recherche JSONB
CREATE INDEX idx_network_data_metadata ON network_data USING GIN(metadata);

-- Partitioning par mois pour performance
CREATE TABLE network_data_y2025m01 PARTITION OF network_data
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
```

### Table `anomalies` - Anomalies Détectées

#### Structure PostgreSQL
```sql
CREATE TABLE anomalies (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    device_id VARCHAR(100) NOT NULL,
    ip_address INET NOT NULL,
    port INTEGER,
    protocol VARCHAR(20),
    anomaly_score DECIMAL(5,3) NOT NULL CHECK (anomaly_score >= 0 AND anomaly_score <= 1),
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('Critique', 'Élevé', 'Moyen', 'Faible')),
    anomaly_type VARCHAR(100),
    confidence DECIMAL(5,3),
    data_volume_mb DECIMAL(10,2),
    baseline_volume DECIMAL(10,2),               -- Volume normal attendu
    deviation_factor DECIMAL(8,2),               -- Facteur de déviation
    affected_sessions UUID[],                    -- Sessions impactées
    correlation_id UUID,                         -- Groupement anomalies liées
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'resolved', 'false_positive')),
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolved_by VARCHAR(100),
    resolution_notes TEXT,
    analyst_feedback JSONB,                      -- Retour analyste
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index pour recherches d'anomalies
CREATE INDEX idx_anomalies_timestamp ON anomalies(timestamp);
CREATE INDEX idx_anomalies_severity_status ON anomalies(severity, status);
CREATE INDEX idx_anomalies_device_time ON anomalies(device_id, timestamp);
CREATE INDEX idx_anomalies_score ON anomalies(anomaly_score DESC);
```

### Table `devices` - Inventaire Appareils

```sql
CREATE TABLE devices (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(100) UNIQUE NOT NULL,
    ip_address INET NOT NULL,
    mac_address MACADDR UNIQUE,
    hostname VARCHAR(200),
    device_type VARCHAR(50),
    vendor VARCHAR(100),
    os_info VARCHAR(200),
    first_seen TIMESTAMP WITH TIME ZONE NOT NULL,
    last_seen TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'quarantined', 'unknown')),
    
    -- Informations réseau
    open_ports INTEGER[],                        -- Array des ports ouverts
    services JSONB,                              -- Services détectés
    network_interfaces JSONB,                    -- Interfaces multiples
    
    -- Profil comportemental
    typical_volume_mb DECIMAL(10,2),             -- Volume habituel
    peak_hours INTEGER[],                        -- Heures de pic
    common_protocols VARCHAR(50)[],              -- Protocoles habituels
    
    -- Scoring risque
    risk_score INTEGER DEFAULT 0 CHECK (risk_score >= 0 AND risk_score <= 100),
    risk_factors JSONB,                          -- Facteurs de risque détaillés
    
    -- Métadonnées
    location VARCHAR(100),
    department VARCHAR(100),
    responsible_user VARCHAR(100),
    notes TEXT,
    tags VARCHAR(50)[],                          -- Tags flexibles
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index performants
CREATE INDEX idx_devices_ip ON devices(ip_address);
CREATE INDEX idx_devices_last_seen ON devices(last_seen);
CREATE INDEX idx_devices_type_status ON devices(device_type, status);
CREATE INDEX idx_devices_risk_score ON devices(risk_score DESC);

-- Index pour recherche textuelle
CREATE INDEX idx_devices_search ON devices USING GIN(to_tsvector('english', hostname || ' ' || vendor || ' ' || COALESCE(notes, '')));
```

### Table `alerts` - Alertes Système

```sql
CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('critical', 'high', 'medium', 'low', 'info')),
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    
    -- Contexte
    source_component VARCHAR(50),
    affected_devices VARCHAR(100)[],             -- Liste appareils impactés
    affected_ips INET[],                         -- IPs concernées
    anomaly_id INTEGER REFERENCES anomalies(id),
    correlation_group UUID,                      -- Groupement alertes liées
    
    -- Gestion
    status VARCHAR(20) DEFAULT 'open' CHECK (status IN ('open', 'acknowledged', 'resolved', 'closed')),
    acknowledged_by VARCHAR(100),
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolution_notes TEXT,
    escalation_level INTEGER DEFAULT 1,
    
    -- Métadonnées
    additional_data JSONB,
    external_ticket_id VARCHAR(100),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index pour gestion alertes
CREATE INDEX idx_alerts_timestamp ON alerts(timestamp);
CREATE INDEX idx_alerts_status_severity ON alerts(status, severity);
CREATE INDEX idx_alerts_type ON alerts(alert_type);
CREATE INDEX idx_alerts_correlation ON alerts(correlation_group);
```

### Table `system_logs` - Logs Système

```sql
CREATE TABLE system_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    level VARCHAR(20) NOT NULL CHECK (level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')),
    component VARCHAR(50) NOT NULL,
    event_type VARCHAR(50),
    message TEXT NOT NULL,
    
    -- Contexte détaillé
    details JSONB,                               -- Détails techniques
    user_id VARCHAR(100),
    session_id VARCHAR(100),
    ip_address INET,
    user_agent TEXT,
    
    -- Traçabilité
    trace_id UUID,                               -- Traçage distributed
    span_id VARCHAR(50),
    parent_span_id VARCHAR(50),
    
    -- Performance
    duration_ms INTEGER,                         -- Durée opération
    memory_usage_mb DECIMAL(8,2),
    cpu_usage_percent DECIMAL(5,2),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index pour recherche logs
CREATE INDEX idx_system_logs_timestamp ON system_logs(timestamp);
CREATE INDEX idx_system_logs_level_component ON system_logs(level, component);
CREATE INDEX idx_system_logs_event_type ON system_logs(event_type);

-- Index GIN pour recherche dans détails JSON
CREATE INDEX idx_system_logs_details ON system_logs USING GIN(details);

-- Index pour recherche textuelle
CREATE INDEX idx_system_logs_message ON system_logs USING GIN(to_tsvector('english', message));
```

### Table `ml_models` - Gestion Modèles IA

```sql
CREATE TABLE ml_models (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(20) NOT NULL,
    algorithm VARCHAR(50) NOT NULL,
    
    -- Configuration
    parameters JSONB NOT NULL,                   -- Hyperparamètres
    feature_schema JSONB,                        -- Schema des features
    preprocessing_config JSONB,                  -- Configuration preprocessing
    
    -- Données d'entraînement
    training_data_start TIMESTAMP WITH TIME ZONE,
    training_data_end TIMESTAMP WITH TIME ZONE,
    training_samples INTEGER,
    training_duration_seconds INTEGER,
    
    -- Performance
    performance_metrics JSONB,                   -- Métriques détaillées
    validation_results JSONB,
    cross_validation_scores DECIMAL(5,3)[],
    
    -- Déploiement
    is_active BOOLEAN DEFAULT FALSE,
    deployment_date TIMESTAMP WITH TIME ZONE,
    model_file_path TEXT,                        -- Chemin fichier modèle
    model_size_mb DECIMAL(8,2),
    
    -- Métadonnées
    description TEXT,
    trained_by VARCHAR(100),
    environment VARCHAR(50),                     -- dev, staging, prod
    git_commit_hash VARCHAR(40),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(model_name, model_version)
);

-- Index pour gestion modèles
CREATE INDEX idx_ml_models_active ON ml_models(is_active, created_at);
CREATE INDEX idx_ml_models_name_version ON ml_models(model_name, model_version);
```

## 3. Implémentation Pratique

### 3.1 Configuration Manager - Basculement Bases

Le fichier `config_manager.py` permet de basculer facilement entre SQLite et PostgreSQL :

```python
class ConfigManager:
    def switch_to_postgresql(self, connection_string=None):
        """Bascule vers PostgreSQL pour production"""
        self.config["database"]["type"] = "postgresql"
        if connection_string:
            self.config["database"]["postgresql"]["connection_string"] = connection_string
        self.save_config()
    
    def switch_to_sqlite(self, db_path=None):
        """Bascule vers SQLite pour développement"""
        self.config["database"]["type"] = "sqlite"
        if db_path:
            self.config["database"]["sqlite"]["path"] = db_path
        self.save_config()

# Factory pour créer le bon gestionnaire
def create_database_manager(config_manager):
    db_config = config_manager.get_database_config()
    
    if db_config.get("type") == "postgresql":
        from postgresql_manager import PostgreSQLManager
        return PostgreSQLManager(db_config.get("postgresql", {}).get("connection_string"))
    else:
        from database_manager import DatabaseManager
        return DatabaseManager(db_config.get("sqlite", {}).get("path", "aegislan.db"))
```

### 3.2 Utilisation Pratique

#### Développement (SQLite)
```python
from config_manager import ConfigManager, create_database_manager

# Configuration développement
config = ConfigManager()
config.switch_to_sqlite("dev_aegislan.db")

# Création gestionnaire
db_manager = create_database_manager(config)

# Initialisation tables
db_manager.init_database()

# Insertion données
sample_data = {
    'timestamp': datetime.now(),
    'device_id': 'WS001',
    'ip_address': '192.168.1.100',
    'port': 443,
    'protocol': 'HTTPS',
    'data_volume_mb': 25.5
}

db_manager.insert_network_data(sample_data)
```

#### Production (PostgreSQL)
```python
# Configuration production avec Neon Database
config = ConfigManager()
config.switch_to_postgresql("postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/aegislan?sslmode=require")

# Même interface, implémentation différente
db_manager = create_database_manager(config)
db_manager.init_database()

# Insertion en lot pour performance
batch_data = [
    {'timestamp': datetime.now(), 'device_id': 'WS001', ...},
    {'timestamp': datetime.now(), 'device_id': 'WS002', ...},
    # ... 1000 enregistrements
]

db_manager.insert_network_data(batch_data)  # Optimisé pour PostgreSQL
```

### 3.3 Migration SQLite → PostgreSQL

Le fichier `postgresql_manager.py` inclut une classe de migration automatique :

```python
class DatabaseMigration:
    def __init__(self, sqlite_path, postgresql_manager):
        self.sqlite_path = sqlite_path
        self.pg_manager = postgresql_manager
    
    def migrate_data(self):
        """Migration complète SQLite → PostgreSQL"""
        import sqlite3
        
        tables_to_migrate = ['network_data', 'anomalies', 'alerts', 'system_logs']
        
        sqlite_conn = sqlite3.connect(self.sqlite_path)
        
        for table_name in tables_to_migrate:
            print(f"Migration table {table_name}...")
            
            # Lecture SQLite
            df = pd.read_sql(f"SELECT * FROM {table_name}", sqlite_conn)
            
            if not df.empty:
                # Adaptation des données
                if table_name == 'network_data':
                    df = self._adapt_network_data(df)
                
                # Insertion PostgreSQL
                self.pg_manager.insert_network_data(df)
                print(f"[SUCCESS] {len(df)} enregistrements migrés")
        
        sqlite_conn.close()

# Utilisation migration
sqlite_db = DatabaseManager("production.db")
postgres_db = PostgreSQLManager("postgresql://...")

migration = DatabaseMigration("production.db", postgres_db)
migration.migrate_data()
```

## 4. Optimisation et Performance

### 4.1 Index Stratégiques

#### Requêtes Temporelles (Fréquentes)
```sql
-- Index composite pour filtres temps + appareil
CREATE INDEX idx_network_time_device ON network_data(timestamp, device_id);

-- Index BRIN pour colonnes temporelles (très efficace sur gros volumes)
CREATE INDEX idx_network_timestamp_brin ON network_data USING BRIN(timestamp);
```

#### Recherches d'Anomalies
```sql
-- Index pour tri par score d'anomalie
CREATE INDEX idx_anomalies_score_desc ON anomalies(anomaly_score DESC, timestamp DESC);

-- Index pour filtres multiples
CREATE INDEX idx_anomalies_status_severity_time ON anomalies(status, severity, timestamp);
```

### 4.2 Partitioning (Tables Volumineuses)

```sql
-- Partitioning mensuel pour network_data
CREATE TABLE network_data (
    -- ... colonnes ...
) PARTITION BY RANGE (timestamp);

-- Partitions automatiques
CREATE TABLE network_data_y2025m01 PARTITION OF network_data
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE network_data_y2025m02 PARTITION OF network_data
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');
```

### 4.3 Politiques de Rétention

```python
def cleanup_old_data(self, days=90):
    """Nettoyage automatique données anciennes"""
    
    cleanup_queries = [
        ("network_data", f"""
            DELETE FROM network_data 
            WHERE timestamp < NOW() - INTERVAL '{days} days'
        """),
        ("system_logs", f"""
            DELETE FROM system_logs 
            WHERE timestamp < NOW() - INTERVAL '{days} days' 
            AND level NOT IN ('ERROR', 'CRITICAL')
        """),
        ("anomalies", f"""
            UPDATE anomalies SET status = 'archived'
            WHERE timestamp < NOW() - INTERVAL '{days} days' 
            AND status = 'resolved'
        """)
    ]
    
    for table_name, query in cleanup_queries:
        cursor.execute(query)
        print(f"[CLEAN] {table_name}: {cursor.rowcount} enregistrements nettoyés")
```

## 5. Monitoring et Maintenance

### 5.1 Monitoring PostgreSQL

```sql
-- Taille des tables
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
    pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY size_bytes DESC;

-- Performance des requêtes
SELECT query, calls, total_time, mean_time, rows
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 10;

-- Index inutilisés
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0;
```

### 5.2 Backup Automatique

```python
def backup_database():
    """Sauvegarde automatique PostgreSQL"""
    
    import subprocess
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backup_aegislan_{timestamp}.sql"
    
    # pg_dump avec compression
    cmd = [
        "pg_dump",
        "-h", os.getenv("PGHOST"),
        "-p", os.getenv("PGPORT"),
        "-U", os.getenv("PGUSER"),
        "-d", os.getenv("PGDATABASE"),
        "-f", backup_file,
        "--verbose",
        "--no-password"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"[SUCCESS] Backup créé: {backup_file}")
        
        # Compression
        subprocess.run(["gzip", backup_file])
        print(f"[SUCCESS] Backup compressé: {backup_file}.gz")
    else:
        print(f"[ERROR] Backup failed: {result.stderr}")

# Programmation backup quotidien
import schedule
schedule.every().day.at("02:00").do(backup_database)
```

Cette architecture de base de données évolutive permet à AEGISLAN de gérer efficacement des volumes de données importants tout en maintenant des performances optimales pour la détection d'anomalies en temps réel.