# GUIDE COMPLET D'ENTRAÎNEMENT IA AEGISLAN

## Comprendre l'Isolation Forest en Détail

### Principe Fondamental

L'Isolation Forest est un algorithme d'apprentissage non supervisé spécialement conçu pour la détection d'anomalies. Il fonctionne sur un principe simple mais puissant : **les anomalies sont plus faciles à isoler que les données normales**.

### Métaphore Explicative

Imaginez que vous voulez identifier des personnes inhabituellement grandes dans une foule :
- **Données normales** : Tailles entre 1.60m et 1.80m (difficiles à séparer)
- **Anomalies** : Personne de 2.10m (facile à isoler avec une seule question : "Plus grand que 1.95m ?")

L'Isolation Forest applique ce principe aux données réseau multidimensionnelles.

### Fonctionnement Technique Détaillé

#### 1. Construction de la Forêt d'Arbres

**Algorithme de Construction** :
```python
def build_isolation_tree(data, current_depth=0, max_depth=10):
    # Condition d'arrêt
    if len(data) <= 1 or current_depth >= max_depth:
        return LeafNode(size=len(data), depth=current_depth)
    
    # Sélection aléatoire d'une feature
    available_features = ['data_volume_mb', 'port', 'hour_sin', 'hour_cos', ...]
    selected_feature = random.choice(available_features)
    
    # Point de division aléatoire
    min_val = data[selected_feature].min()
    max_val = data[selected_feature].max()
    split_point = random.uniform(min_val, max_val)
    
    # Division des données
    left_data = data[data[selected_feature] < split_point]
    right_data = data[data[selected_feature] >= split_point]
    
    # Construction récursive
    left_child = build_isolation_tree(left_data, current_depth + 1, max_depth)
    right_child = build_isolation_tree(right_data, current_depth + 1, max_depth)
    
    return InternalNode(selected_feature, split_point, left_child, right_child)
```

**Pourquoi cette randomisation ?**
- **Évite l'overfitting** : Pas de biais vers certaines features
- **Capture diverse patterns** : Chaque arbre explore différents aspects
- **Robustesse** : Résistant au bruit dans les données

#### 2. Calcul du Score d'Anomalie

**Mesure de la Longueur de Chemin** :
```python
def path_length(point, tree, current_depth=0):
    """Calcule la profondeur nécessaire pour isoler un point"""
    
    if isinstance(tree, LeafNode):
        # Ajustement pour les feuilles avec plusieurs points
        return current_depth + average_path_length_BST(tree.size)
    
    # Navigation dans l'arbre
    feature_value = point[tree.feature]
    
    if feature_value < tree.split_point:
        return path_length(point, tree.left_child, current_depth + 1)
    else:
        return path_length(point, tree.right_child, current_depth + 1)

def average_path_length_BST(n):
    """Longueur moyenne dans un arbre binaire de recherche équilibré"""
    if n <= 1:
        return 0
    return 2 * (np.log(n - 1) + 0.5772156649) - (2 * (n - 1) / n)
```

**Normalisation du Score** :
```python
def anomaly_score(point, isolation_forest):
    """Score d'anomalie normalisé entre 0 et 1"""
    
    path_lengths = []
    for tree in isolation_forest.trees:
        path_length_value = path_length(point, tree)
        path_lengths.append(path_length_value)
    
    average_path = np.mean(path_lengths)
    
    # Normalisation selon la formule Isolation Forest
    # s(x,n) = 2^(-E(h(x))/c(n))
    c_n = average_path_length_BST(isolation_forest.training_size)
    score = 2 ** (-average_path / c_n)
    
    return score
```

**Interprétation des Scores** :
- **Score ≈ 1** : Anomalie très probable (chemin court)
- **Score ≈ 0.5** : Comportement normal typique
- **Score ≈ 0** : Très normal (chemin long)

## Préparation des Données pour l'IA

### Feature Engineering Avancé

#### 1. Features Temporelles Cycliques

**Problème** : L'heure 23 et l'heure 0 sont proches temporellement mais éloignées numériquement.

**Solution** : Encodage trigonométrique
```python
def encode_cyclical_features(df):
    """Encode les features temporelles en préservant la cyclicité"""
    
    # Heures (24h cycle)
    df['hour'] = df['timestamp'].dt.hour
    df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
    
    # Jours de la semaine (7 jours cycle)
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['day_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
    df['day_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
    
    # Mois (pour saisonnalité)
    df['month'] = df['timestamp'].dt.month
    df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
    df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
    
    return df
```

**Avantage** : L'IA comprend que 23h59 et 00h01 sont temporellement proches.

#### 2. Features Statistiques Roulantes

**Objectif** : Capturer les patterns comportementaux des appareils

```python
def compute_rolling_features(df, window='1H'):
    """Calcule des statistiques roulantes par appareil"""
    
    # Tri par appareil et temps
    df = df.sort_values(['device_id', 'timestamp'])
    
    # Groupement par appareil
    grouped = df.groupby('device_id')
    
    # Features roulantes (fenêtre 1 heure)
    rolling_features = {}
    
    for device_id, device_data in grouped:
        device_data = device_data.set_index('timestamp')
        
        # Statistiques roulantes
        rolling_stats = device_data.rolling(window).agg({
            'data_volume_mb': ['mean', 'std', 'max', 'min'],
            'port': 'nunique',
            'protocol': 'nunique'
        })
        
        # Aplatissement colonnes
        rolling_stats.columns = ['_'.join(col).strip() for col in rolling_stats.columns]
        
        # Ratios par rapport à la normale
        rolling_stats['volume_ratio'] = (
            device_data['data_volume_mb'] / 
            rolling_stats['data_volume_mb_mean'].shift(1)
        )
        
        rolling_features[device_id] = rolling_stats
    
    # Reconstruction DataFrame
    result = pd.concat(rolling_features.values(), keys=rolling_features.keys())
    result.index.names = ['device_id', 'timestamp']
    
    return result.reset_index()
```

#### 3. Features de Classification de Ports

```python
def classify_port_features(df):
    """Ajoute des features de classification des ports"""
    
    # Ports bien connus (0-1023)
    df['is_well_known_port'] = (df['port'] <= 1023).astype(int)
    
    # Ports enregistrés (1024-49151)
    df['is_registered_port'] = (
        (df['port'] > 1023) & (df['port'] <= 49151)
    ).astype(int)
    
    # Ports dynamiques/privés (49152-65535)
    df['is_dynamic_port'] = (df['port'] > 49151).astype(int)
    
    # Ports critiques pour sécurité
    critical_ports = [22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 3389, 5432, 3306]
    df['is_critical_port'] = df['port'].isin(critical_ports).astype(int)
    
    # Ports suspects (backdoors connus)
    suspicious_ports = [1234, 4444, 6666, 9999, 31337, 12345, 54321]
    df['is_suspicious_port'] = df['port'].isin(suspicious_ports).astype(int)
    
    # Ports de tunneling
    tunneling_ports = [443, 80, 53, 22]  # Souvent utilisés pour tunneling
    df['is_tunneling_candidate'] = df['port'].isin(tunneling_ports).astype(int)
    
    return df
```

#### 4. Features de Comportement Réseau

```python
def network_behavior_features(df):
    """Features comportementales avancées"""
    
    # Durée de session estimée (groupement par IP et port)
    session_groups = df.groupby(['ip_address', 'port', 'protocol'])
    df['session_duration'] = session_groups['timestamp'].transform(
        lambda x: (x.max() - x.min()).total_seconds()
    )
    
    # Fréquence de connexion par appareil
    device_freq = df.groupby('device_id')['timestamp'].transform('count')
    df['connection_frequency'] = device_freq
    
    # Diversité de protocoles par appareil
    protocol_diversity = df.groupby('device_id')['protocol'].transform('nunique')
    df['protocol_diversity'] = protocol_diversity
    
    # Ratio upload/download (si disponible)
    if 'bytes_sent' in df.columns and 'bytes_received' in df.columns:
        df['upload_download_ratio'] = np.where(
            df['bytes_received'] > 0,
            df['bytes_sent'] / df['bytes_received'],
            df['bytes_sent']  # Si pas de download, utiliser upload brut
        )
    
    # Entropie des ports utilisés par appareil (diversité)
    def port_entropy(ports):
        """Calcule l'entropie des ports utilisés"""
        from scipy.stats import entropy
        
        port_counts = pd.Series(ports).value_counts()
        probabilities = port_counts / port_counts.sum()
        
        return entropy(probabilities, base=2)
    
    port_entropy_by_device = df.groupby('device_id')['port'].transform(
        lambda x: port_entropy(x.values)
    )
    df['port_entropy'] = port_entropy_by_device
    
    return df
```

### Processus d'Entraînement Étape par Étape

#### Phase 1 : Collecte de Données Baseline

**Durée Recommandée** : 7-14 jours minimum
**Objectif** : Capturer les patterns normaux du réseau

```python
def collect_training_baseline():
    """Collecte systématique des données d'entraînement"""
    
    print("Phase 1: Collecte baseline (7-14 jours)")
    
    collector = RealNetworkCollector()
    db_manager = create_database_manager(config)
    
    # Configuration collecte
    collection_config = {
        'scan_interval': 300,      # 5 minutes
        'deep_scan_interval': 3600, # 1 heure (scan complet)
        'discovery_interval': 7200, # 2 heures (nouveaux appareils)
        'max_concurrent_scans': 3
    }
    
    # Métriques de collecte
    collection_stats = {
        'total_scans': 0,
        'devices_discovered': set(),
        'data_points_collected': 0,
        'errors': 0
    }
    
    def collection_cycle():
        try:
            # Scan réseau principal
            network_data = collector.scan_network_nmap()
            
            if not network_data.empty:
                # Enrichissement des données
                network_data = encode_cyclical_features(network_data)
                network_data = classify_port_features(network_data)
                network_data = network_behavior_features(network_data)
                
                # Stockage
                db_manager.insert_network_data(network_data.to_dict('records'))
                
                # Statistiques
                collection_stats['total_scans'] += 1
                collection_stats['devices_discovered'].update(network_data['device_id'].unique())
                collection_stats['data_points_collected'] += len(network_data)
                
                print(f"Cycle {collection_stats['total_scans']}: "
                      f"{len(network_data)} enregistrements, "
                      f"{len(collection_stats['devices_discovered'])} appareils")
            
        except Exception as e:
            collection_stats['errors'] += 1
            print(f"Erreur collecte: {e}")
    
    # Programmation de la collecte
    schedule.every(collection_config['scan_interval']).seconds.do(collection_cycle)
    
    # Collecte pour la durée spécifiée
    baseline_duration = 7 * 24 * 60 * 60  # 7 jours en secondes
    start_time = time.time()
    
    while time.time() - start_time < baseline_duration:
        schedule.run_pending()
        time.sleep(60)
        
        # Rapport de progression quotidien
        if collection_stats['total_scans'] % 288 == 0:  # Toutes les 24h (288 * 5min)
            days_elapsed = (time.time() - start_time) / (24 * 60 * 60)
            print(f"Jour {days_elapsed:.1f}: "
                  f"{collection_stats['data_points_collected']} points collectés, "
                  f"{len(collection_stats['devices_discovered'])} appareils")
    
    print(f"Collecte baseline terminée: {collection_stats}")
    return collection_stats
```

#### Phase 2 : Validation et Nettoyage des Données

```python
def validate_training_data():
    """Validation et nettoyage des données d'entraînement"""
    
    print("Phase 2: Validation des données d'entraînement")
    
    # Chargement des données
    raw_data = db_manager.get_network_data(hours=168)  # 7 jours
    
    print(f"Données brutes: {len(raw_data)} enregistrements")
    
    # Validation 1: Volume minimal
    min_records = 10000
    if len(raw_data) < min_records:
        print(f"[WARNING] Peu de données ({len(raw_data)} < {min_records})")
        print("Recommandation: Collecter plus de données ou utiliser le simulateur")
    
    # Validation 2: Couverture temporelle
    time_span = raw_data['timestamp'].max() - raw_data['timestamp'].min()
    print(f"Couverture temporelle: {time_span.days} jours")
    
    if time_span.days < 3:
        print("[WARNING] Couverture temporelle insuffisante (< 3 jours)")
    
    # Validation 3: Diversité des appareils
    unique_devices = raw_data['device_id'].nunique()
    print(f"Appareils uniques: {unique_devices}")
    
    if unique_devices < 5:
        print("[WARNING] Peu d'appareils différents (< 5)")
    
    # Nettoyage 1: Suppression des doublons
    before_dedup = len(raw_data)
    raw_data = raw_data.drop_duplicates(
        subset=['timestamp', 'device_id', 'port', 'protocol']
    )
    after_dedup = len(raw_data)
    
    if before_dedup != after_dedup:
        print(f"Doublons supprimés: {before_dedup - after_dedup}")
    
    # Nettoyage 2: Valeurs aberrantes extrêmes
    # Volume de données > 10GB = probablement erreur
    outliers = raw_data[raw_data['data_volume_mb'] > 10000]
    if not outliers.empty:
        print(f"Valeurs aberrantes supprimées: {len(outliers)}")
        raw_data = raw_data[raw_data['data_volume_mb'] <= 10000]
    
    # Nettoyage 3: Ports invalides
    invalid_ports = raw_data[
        (raw_data['port'] < 0) | (raw_data['port'] > 65535)
    ]
    if not invalid_ports.empty:
        print(f"Ports invalides supprimés: {len(invalid_ports)}")
        raw_data = raw_data[
            (raw_data['port'] >= 0) & (raw_data['port'] <= 65535)
        ]
    
    # Validation finale
    print(f"Données nettoyées: {len(raw_data)} enregistrements")
    
    # Statistiques descriptives
    print("\nStatistiques des données d'entraînement:")
    print(f"Volume moyen: {raw_data['data_volume_mb'].mean():.2f} MB")
    print(f"Volume médian: {raw_data['data_volume_mb'].median():.2f} MB")
    print(f"Écart-type volume: {raw_data['data_volume_mb'].std():.2f} MB")
    print(f"Ports uniques: {raw_data['port'].nunique()}")
    print(f"Protocoles: {raw_data['protocol'].unique()}")
    
    return raw_data
```

#### Phase 3 : Configuration Optimale du Modèle

```python
def optimize_model_parameters(training_data):
    """Optimisation des hyperparamètres du modèle"""
    
    print("Phase 3: Optimisation des paramètres du modèle")
    
    # Préparation des features
    detector = AnomalyDetector()
    X = detector._prepare_features(training_data, fit_encoders=True)
    
    # Grille de paramètres à tester
    param_grid = {
        'contamination': [0.01, 0.03, 0.05, 0.08, 0.10],
        'n_estimators': [50, 100, 150, 200],
        'max_samples': ['auto', 0.5, 0.8],
        'max_features': [0.5, 0.8, 1.0]
    }
    
    best_score = -1
    best_params = {}
    
    print("Test des configurations...")
    
    for contamination in param_grid['contamination']:
        for n_estimators in param_grid['n_estimators']:
            for max_samples in param_grid['max_samples']:
                for max_features in param_grid['max_features']:
                    
                    # Configuration modèle
                    model = IsolationForest(
                        contamination=contamination,
                        n_estimators=n_estimators,
                        max_samples=max_samples,
                        max_features=max_features,
                        random_state=42,
                        n_jobs=-1  # Parallélisation
                    )
                    
                    # Entraînement
                    model.fit(X)
                    
                    # Évaluation par validation croisée
                    scores = []
                    for _ in range(3):  # 3 évaluations
                        # Échantillonnage aléatoire
                        sample_idx = np.random.choice(len(X), size=min(1000, len(X)), replace=False)
                        X_sample = X[sample_idx]
                        
                        # Prédiction
                        predictions = model.predict(X_sample)
                        anomaly_scores = model.score_samples(X_sample)
                        
                        # Métrique: stabilité du taux d'anomalies
                        anomaly_rate = np.mean(predictions == -1)
                        score_std = np.std(anomaly_scores)
                        
                        # Score composite (proche de contamination + faible variance)
                        stability_score = 1 - abs(anomaly_rate - contamination) - (score_std * 0.1)
                        scores.append(stability_score)
                    
                    avg_score = np.mean(scores)
                    
                    if avg_score > best_score:
                        best_score = avg_score
                        best_params = {
                            'contamination': contamination,
                            'n_estimators': n_estimators,
                            'max_samples': max_samples,
                            'max_features': max_features
                        }
                    
                    print(f"contamination={contamination:.2f}, "
                          f"n_estimators={n_estimators}, "
                          f"score={avg_score:.3f}")
    
    print(f"\nMeilleurs paramètres: {best_params}")
    print(f"Score: {best_score:.3f}")
    
    return best_params
```

#### Phase 4 : Entraînement Final et Validation

```python
def train_production_model(training_data, optimal_params):
    """Entraînement du modèle final pour production"""
    
    print("Phase 4: Entraînement du modèle de production")
    
    # Initialisation avec paramètres optimaux
    detector = AnomalyDetector()
    
    # Configuration du modèle Isolation Forest
    detector.model = IsolationForest(
        contamination=optimal_params['contamination'],
        n_estimators=optimal_params['n_estimators'],
        max_samples=optimal_params['max_samples'],
        max_features=optimal_params['max_features'],
        random_state=42,
        n_jobs=-1,
        behaviour='new'
    )
    
    # Entraînement avec monitoring
    start_time = time.time()
    print("Début de l'entraînement...")
    
    # Préparation features (avec fit des encodeurs)
    X = detector._prepare_features(training_data, fit_encoders=True)
    print(f"Features préparées: {X.shape[1]} dimensions")
    
    # Normalisation
    X_scaled = detector.scaler.fit_transform(X)
    
    # Entraînement du modèle
    detector.model.fit(X_scaled)
    
    training_time = time.time() - start_time
    print(f"Entraînement terminé en {training_time:.2f} secondes")
    
    # Marquage comme entraîné
    detector.is_trained = True
    detector.feature_columns = [f'feature_{i}' for i in range(X.shape[1])]
    
    # Validation sur données d'entraînement
    print("Validation du modèle...")
    
    # Test sur échantillon représentatif
    test_size = min(5000, len(training_data))
    test_sample = training_data.sample(n=test_size, random_state=42)
    
    detected_anomalies = detector.detect_anomalies(test_sample)
    
    # Métriques de validation
    anomaly_rate = len(detected_anomalies) / len(test_sample)
    
    print(f"Taux d'anomalies détecté: {anomaly_rate:.1%}")
    print(f"Anomalies par sévérité:")
    
    if not detected_anomalies.empty:
        severity_counts = detected_anomalies['severity'].value_counts()
        for severity, count in severity_counts.items():
            percentage = count / len(detected_anomalies) * 100
            print(f"  {severity}: {count} ({percentage:.1f}%)")
    
    # Sauvegarde du modèle
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_filename = f"models/aegislan_isolation_forest_{timestamp}.joblib"
    
    os.makedirs("models", exist_ok=True)
    
    model_data = {
        'model': detector.model,
        'scaler': detector.scaler,
        'label_encoders': detector.label_encoders,
        'feature_columns': detector.feature_columns,
        'training_metadata': {
            'training_samples': len(training_data),
            'training_time_seconds': training_time,
            'contamination': optimal_params['contamination'],
            'n_estimators': optimal_params['n_estimators'],
            'validation_anomaly_rate': anomaly_rate,
            'training_date': datetime.now().isoformat(),
            'data_time_range': {
                'start': training_data['timestamp'].min().isoformat(),
                'end': training_data['timestamp'].max().isoformat()
            }
        }
    }
    
    joblib.dump(model_data, model_filename)
    print(f"Modèle sauvegardé: {model_filename}")
    
    # Enregistrement en base de données
    model_record = {
        'model_name': 'IsolationForest_Production',
        'model_version': f'v{timestamp}',
        'algorithm': 'IsolationForest',
        'parameters': optimal_params,
        'training_data_start': training_data['timestamp'].min(),
        'training_data_end': training_data['timestamp'].max(),
        'training_samples': len(training_data),
        'performance_metrics': {
            'validation_anomaly_rate': anomaly_rate,
            'training_time_seconds': training_time
        },
        'model_file_path': model_filename,
        'is_active': True
    }
    
    if hasattr(db_manager, 'insert_ml_model'):
        db_manager.insert_ml_model(model_record)
    
    print("Modèle prêt pour la production!")
    return detector, model_filename
```

### Configuration du Fichier `config_manager.py`

Le fichier `config_manager.py` sert à centraliser tous les paramètres de configuration et permet de basculer facilement entre environnements (développement/production).

#### Utilité du Fichier Python vs JSON/YAML

**Avantages du format Python** :
1. **Validation native** : Types de données Python validés automatiquement
2. **Logique conditionnelle** : Configuration adaptative selon l'environnement
3. **Documentation intégrée** : Docstrings explicatives
4. **Import simple** : Pas de parsing externe nécessaire
5. **Valeurs par défaut intelligentes** : Calculs dynamiques des paramètres

#### Structure et Utilisation

```python
# Utilisation pratique du ConfigManager
from config_manager import ConfigManager, create_database_manager

# Initialisation
config = ConfigManager()

# Développement : SQLite + Simulateur
config.switch_to_sqlite("development.db")
config.update_config("ai", "contamination", 0.08)
config.update_config("network", "use_simulator", True)

# Production : PostgreSQL + Réseau réel
config.switch_to_postgresql("postgresql://user:pass@host/db")
config.update_config("ai", "contamination", 0.05)
config.update_config("network", "use_simulator", False)
config.setup_production_environment()

# Création automatique du bon gestionnaire
db_manager = create_database_manager(config)
```

Cette approche d'entraînement méthodique garantit un modèle IA robuste et adapté aux spécificités de votre réseau d'entreprise.