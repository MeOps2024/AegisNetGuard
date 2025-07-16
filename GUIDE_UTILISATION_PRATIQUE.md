# GUIDE UTILISATION PRATIQUE AEGISLAN

## Comment Utiliser l'IA : Guide Étape par Étape

### 1. Démarrage Initial

#### Lancement de l'Application
```bash
# Dans le dossier AEGISLAN
streamlit run app.py --server.port 5000 --server.address 0.0.0.0
```

**Interface accessible sur** : http://localhost:5000

#### Premier Démarrage - Configuration
1. **Accès à l'interface** → Section "Configuration Système"
2. **Base de données** → Choisir SQLite (développement) ou PostgreSQL (production)
3. **Réseau** → Configurer la plage d'IP à surveiller (ex: 192.168.1.0/24)
4. **IA** → Paramètres d'entraînement (contamination, seuils)

### 2. Collecte de Données Réseau

#### Option A : Simulation (Développement/Test)
1. **Section "Analyse Réseau"** → Onglet "Génération de Données"
2. **Paramètres** :
   - Nombre d'appareils : 20-50 pour tests
   - Période : 24-72 heures
   - Pourcentage d'anomalies : 5-10%
3. **Génération** → Cliquer "Générer Données Simulées"

#### Option B : Données Réelles (Production)
1. **Prérequis** : Nmap installé, droits administrateur
2. **Configuration réseau** :
   ```python
   # Dans real_network_collector.py
   collector = RealNetworkCollector(
       network_range="192.168.1.0/24",  # Votre réseau
       db_manager=db_manager
   )
   ```
3. **Démarrage collecte** :
   ```python
   # Script de collecte continue
   collector.start_continuous_monitoring(interval=300)  # 5 minutes
   ```

### 3. Entraînement du Modèle IA

#### Processus d'Entraînement Complet

**Étape 1 : Vérification des Données**
1. **Section "Détection de Menaces"** → Onglet "Données d'Entraînement"
2. **Vérification** : Minimum 1000 enregistrements (idéal : 10000+)
3. **Période** : Au moins 7 jours de données normales

**Étape 2 : Configuration du Modèle**
```python
# Paramètres recommandés pour production
contamination = 0.05    # 5% d'anomalies attendues
n_estimators = 100      # Nombre d'arbres
max_samples = 'auto'    # Échantillonnage automatique
```

**Étape 3 : Lancement Entraînement**
1. **Bouton "Entraîner Modèle"** → Configuration visible
2. **Surveillance** → Barre de progression en temps réel
3. **Validation** → Métriques de performance affichées

#### Comprendre les Métriques d'Entraînement

**Contamination** : Pourcentage d'anomalies attendues
- 0.01 (1%) : Réseau très sécurisé
- 0.05 (5%) : Réseau entreprise standard
- 0.10 (10%) : Environnement de test

**Score d'Anomalie** : De 0 à 1
- 0.8-1.0 : Anomalie critique (investigation immédiate)
- 0.6-0.8 : Anomalie élevée (surveillance renforcée)
- 0.4-0.6 : Anomalie moyenne (analyse routinière)
- 0.0-0.4 : Comportement normal

### 4. Surveillance et Détection Temps Réel

#### Dashboard Principal - Interprétation

**Métriques Système** :
- **Appareils Actifs** : Nombre d'équipements détectés
- **Anomalies Détectées** : Alertes en cours
- **Volume Total** : Trafic réseau agrégé
- **Statut IA** : État du modèle (Opérationnel/Non entraîné)

**Graphiques Temporels** :
- **Courbe bleue** : Volume de données normal
- **Points rouges** : Anomalies détectées
- **Pics inhabituels** : Activité suspecte

#### Gestion des Alertes

**Types d'Alertes** :
1. **Volume Anormal** : Trafic inhabituel d'un appareil
2. **Port Suspect** : Utilisation de ports non standards
3. **Activité Nocturne** : Trafic en dehors heures bureau
4. **Nouveau Appareil** : Équipement non reconnu

**Actions sur Alertes** :
1. **Investigation** → Clic sur l'anomalie → Détails complets
2. **Classification** → Vraie menace / Faux positif
3. **Résolution** → Marquer comme résolue
4. **Escalade** → Génération ticket ou notification

### 5. Utilisation de Nmap et Collecte Réseau

#### Configuration Nmap

**Installation Windows** :
```powershell
# Télécharger depuis nmap.org
# Installation manuelle requise
# Ajout au PATH système
```

**Paramètres de Scan** :
```python
# Dans real_network_collector.py
def scan_network_nmap(self, ports="1-1000"):
    # Scan SYN (discret et rapide)
    cmd = f"nmap -sS -O -sV {self.network_range} -p {ports}"
    
    # Options expliquées :
    # -sS : SYN scan (semi-ouvert, discret)
    # -O : Détection OS
    # -sV : Version des services
    # -p : Plage de ports
```

**Types de Scans** :
1. **Découverte** : `nmap -sn 192.168.1.0/24` (appareils actifs)
2. **Port Scan** : `nmap -sS 192.168.1.100` (ports ouverts)
3. **Service** : `nmap -sV 192.168.1.100` (versions services)
4. **OS Detection** : `nmap -O 192.168.1.100` (système d'exploitation)

#### Intégration SNMP

**Configuration Routeur/Switch** :
```
# Configuration SNMP v2c
snmp-server community public RO
snmp-server location "Bureau Principal"
snmp-server contact "admin@entreprise.com"
```

**Collecte Python** :
```python
def collect_snmp_data(self, router_ip, community="public"):
    from pysnmp.hlapi import *
    
    # OIDs standards
    oids = {
        'sysName': '1.3.6.1.2.1.1.5.0',
        'ifInOctets': '1.3.6.1.2.1.2.2.1.10',  # Octets entrants
        'ifOutOctets': '1.3.6.1.2.1.2.2.1.16'  # Octets sortants
    }
    
    for name, oid in oids.items():
        for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(
            SnmpEngine(),
            CommunityData(community),
            UdpTransportTarget((router_ip, 161)),
            ContextData(),
            ObjectType(ObjectIdentity(oid)),
            lexicographicMode=False):
            
            if errorIndication or errorStatus:
                break
                
            for varBind in varBinds:
                print(f"{name}: {varBind}")
```

### 6. Configuration et Utilisation Base de Données

#### SQLite (Développement)

**Avantages** :
- Configuration zéro
- Fichier unique
- Performance locale excellente
- Parfait pour prototypage

**Utilisation** :
```python
from config_manager import ConfigManager

# Basculement SQLite
config = ConfigManager()
config.switch_to_sqlite("aegislan_dev.db")

# Utilisation automatique
db_manager = create_database_manager(config)
```

**Inspection Données** :
```python
# Connexion directe SQLite
import sqlite3

conn = sqlite3.connect("aegislan_dev.db")
cursor = conn.cursor()

# Statistiques rapides
cursor.execute("SELECT COUNT(*) FROM network_data")
print(f"Enregistrements réseau: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM anomalies WHERE status='active'")
print(f"Anomalies actives: {cursor.fetchone()[0]}")
```

#### PostgreSQL (Production)

**Configuration Neon Database (Recommandé)** :
1. **Inscription** : neon.tech
2. **Création projet** : "AEGISLAN"
3. **Récupération URL** : Format `postgresql://user:pass@host/db`
4. **Configuration AEGISLAN** :
   ```python
   config.switch_to_postgresql("postgresql://user:pass@ep-xxx.neon.tech/aegislan")
   ```

**Avantages Production** :
- Gestion téraoctets de données
- Concurrence élevée
- Types réseau natifs (INET, MACADDR)
- Sauvegarde automatique cloud
- Monitoring intégré

**Requêtes Optimisées** :
```sql
-- Top appareils par volume (24h)
SELECT 
    device_id,
    ip_address,
    SUM(data_volume_mb) as total_volume,
    COUNT(*) as connections
FROM network_data 
WHERE timestamp > NOW() - INTERVAL '24 hours'
GROUP BY device_id, ip_address
ORDER BY total_volume DESC
LIMIT 10;

-- Anomalies par heure
SELECT 
    date_trunc('hour', timestamp) as hour,
    COUNT(*) as anomalies,
    AVG(anomaly_score) as avg_score
FROM anomalies 
WHERE timestamp > NOW() - INTERVAL '7 days'
GROUP BY hour
ORDER BY hour;
```

### 7. Export et Reporting

#### Exports Automatiques

**Configuration** :
```python
# Script export hebdomadaire
def generate_weekly_report():
    # Récupération données
    network_data = db_manager.get_network_data(hours=168)
    anomalies_data = db_manager.get_anomalies(hours=168)
    
    # Export CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    network_data.to_csv(f"exports/network_week_{timestamp}.csv")
    anomalies_data.to_csv(f"exports/anomalies_week_{timestamp}.csv")
    
    # Rapport JSON
    report = {
        'period': '7 days',
        'total_devices': network_data['device_id'].nunique(),
        'total_anomalies': len(anomalies_data),
        'critical_anomalies': len(anomalies_data[anomalies_data['severity'] == 'Critique'])
    }
    
    with open(f"exports/report_{timestamp}.json", 'w') as f:
        json.dump(report, f, indent=2)
```

#### Intégration SIEM

**Format CEF (Common Event Format)** :
```python
def export_to_cef(anomaly):
    """Export anomalie au format CEF pour SIEM"""
    
    cef_event = (
        f"CEF:0|AEGISLAN|NetworkMonitor|1.0|ANOMALY|Network Anomaly Detected|"
        f"{anomaly['severity']}|"
        f"src={anomaly['ip_address']} "
        f"dst=internal "
        f"spt={anomaly['port']} "
        f"proto={anomaly['protocol']} "
        f"cnt={anomaly['data_volume_mb']} "
        f"cs1Label=AnomalyScore cs1={anomaly['anomaly_score']} "
        f"cs2Label=DeviceID cs2={anomaly['device_id']}"
    )
    
    return cef_event
```

### 8. Maintenance et Optimisation

#### Maintenance Quotidienne

**Script Automatisé** :
```python
def daily_maintenance():
    print("Maintenance quotidienne AEGISLAN...")
    
    # Nettoyage logs anciens
    db_manager.cleanup_old_data(days=30)
    
    # Vérification santé modèle
    model_info = detector.get_model_info()
    if model_info['status'] == 'Entraîné':
        # Test performance sur échantillon
        test_data = db_manager.get_network_data(hours=24)
        anomalies = detector.detect_anomalies(test_data.sample(100))
        
        anomaly_rate = len(anomalies) / 100
        if anomaly_rate > 0.2:  # Plus de 20% anomalies
            print("[WARNING] Taux d'anomalie élevé, re-entraînement recommandé")
    
    # Backup base de données
    if config.get_database_config()['type'] == 'postgresql':
        backup_database()
    
    print("Maintenance terminée")

# Programmation
import schedule
schedule.every().day.at("03:00").do(daily_maintenance)
```

#### Re-entraînement Adaptatif

**Déclencheurs Re-entraînement** :
- Taux d'anomalie > 15% sur 48h (données nouvelles)
- Changement topologie réseau (nouveaux appareils)
- Performance dégradée (faux positifs élevés)
- Nouveau matériel réseau
- Modification politique sécurité

### 9. Résolution Problèmes Courants

#### Modèle Non Entraîné
**Symptôme** : "Modèle non entraîné" dans le dashboard
**Solution** :
1. Vérifier données disponibles (min 1000 enregistrements)
2. Section "Détection Menaces" → "Entraîner Modèle"
3. Attendre fin d'entraînement (barre progression)

#### Pas de Données Réseau
**Symptôme** : Dashboard vide, pas d'appareils détectés
**Solution** :
1. Vérifier droits administrateur
2. Tester Nmap : `nmap -sn 192.168.1.0/24`
3. Vérifier plage IP réseau dans configuration
4. Alternative : Utiliser simulateur pour tests

#### Performance Lente
**Symptôme** : Interface lente, requêtes longues
**Solution** :
1. SQLite → Basculer PostgreSQL si >100MB données
2. Nettoyer anciennes données : `db_manager.cleanup_old_data(15)`
3. Vérifier RAM disponible (min 4GB)
4. Réduire intervalle collecte réseau

#### Trop de Faux Positifs
**Symptôme** : Alertes fréquentes non pertinentes
**Solution** :
1. Augmenter contamination : 0.05 → 0.08
2. Re-entraîner avec plus de données (14+ jours)
3. Ajuster seuils de criticité
4. Marquer faux positifs pour apprentissage

Cette approche pratique vous permet d'utiliser AEGISLAN efficacement depuis l'installation jusqu'à la surveillance quotidienne.