# GUIDE COMPLET D'ANALYSE DES FICHIERS AEGISLAN

## Vue d'ensemble des Fichiers

Le projet AEGISLAN est organisé en modules spécialisés, chacun ayant un rôle précis dans l'architecture globale. Voici l'analyse détaillée de chaque fichier.

## 1. app.py - Point d'Entrée Principal

### Rôle et Responsabilités
- **Point d'entrée unique** : Lance l'application Streamlit
- **Orchestrateur** : Coordonne tous les autres modules
- **Gestionnaire d'état** : Maintient les sessions utilisateur
- **Interface utilisateur** : Définit la structure de l'interface

### Contenu Technique Détaillé

#### Configuration Streamlit
```python
st.set_page_config(
    page_title="AEGISLAN - Enterprise Network Security",
    page_icon=":zap:",
    layout="wide",                    # Utilise toute la largeur écran
    initial_sidebar_state="expanded"  # Sidebar ouverte par défaut
)
```

#### Gestion des Sessions
```python
# Initialisation des composants en session state (persistance)
if 'simulator' not in st.session_state:
    st.session_state.simulator = NetworkDataSimulator()
if 'detector' not in st.session_state:
    st.session_state.detector = AnomalyDetector()
if 'dashboard' not in st.session_state:
    st.session_state.dashboard = Dashboard()
```

#### Fonctions Principales

**1. `main()`**
- Point d'entrée principal
- Configuration thème CSS corporate
- Initialisation composants
- Routage vers sections

**2. `render_dashboard_section()`**
- Affichage du tableau de bord principal
- Métriques temps réel
- Graphiques de surveillance
- Statut système global

**3. `render_network_analysis_section()`**
- Analyse détaillée du trafic réseau
- Visualisations par appareil/protocole/port
- Historiques et tendances
- Filtres avancés

**4. `render_threat_detection_section()`**
- Interface de gestion des anomalies
- Configuration modèle IA
- Entraînement et évaluation
- Alertes et notifications

**5. `render_system_config_section()`**
- Paramètres de configuration système
- Gestion base de données
- Configuration réseau
- Paramètres IA

**6. `render_reports_section()`**
- Génération de rapports
- Exports de données
- Statistiques historiques
- Visualisations avancées

### Pourquoi cette Architecture ?
- **Modularité** : Chaque section est indépendante
- **Maintenabilité** : Code organisé par fonctionnalité
- **Extensibilité** : Ajout facile de nouvelles sections
- **Performance** : Chargement conditionnel des composants

## 2. data_simulator.py - Générateur de Données Réalistes

### Rôle et Responsabilités
- **Génération de données** : Crée du trafic réseau simulé réaliste
- **Profils d'appareils** : Simule différents types d'équipements
- **Injection d'anomalies** : Crée des comportements suspects contrôlés
- **Support développement** : Fournit données pour tests et démos

### Architecture de Classes

#### Classe NetworkDataSimulator
```python
class NetworkDataSimulator:
    def __init__(self):
        self.device_profiles = self._init_device_profiles()
        self.anomaly_patterns = self._init_anomaly_patterns()
        self.network_topology = self._init_network_topology()
```

### Fonctions Principales Détaillées

#### 1. `_generate_device_profile(device_id)`
**Objectif** : Crée un profil comportemental pour un appareil

**Profils supportés** :
```python
'Workstation': {
    'base_ports': [80, 443, 22, 3389],        # HTTP, HTTPS, SSH, RDP
    'activity_hours': (8, 18),                # 8h-18h bureau
    'volume_range': (10, 500),                # 10-500 MB/heure
    'protocols': ['TCP', 'UDP', 'ICMP'],
    'peak_hours': [9, 14, 16],                # Pics d'activité
    'anomaly_probability': 0.02               # 2% chance anomalie
},
'Server': {
    'base_ports': [80, 443, 22, 25, 993, 995],
    'activity_hours': (0, 24),               # 24h/24
    'volume_range': (100, 5000),             # Volume élevé
    'protocols': ['TCP', 'UDP'],
    'peak_hours': [10, 14, 20],
    'anomaly_probability': 0.01              # Moins d'anomalies
},
'IoT_Device': {
    'base_ports': [80, 443, 8080],
    'activity_hours': (0, 24),
    'volume_range': (1, 50),                 # Volume faible
    'protocols': ['TCP', 'UDP'],
    'communication_pattern': 'periodic',     # Envoi périodique
    'anomaly_probability': 0.05              # Plus vulnérable
}
```

#### 2. `_generate_normal_traffic(device_profile, timestamp)`
**Objectif** : Génère du trafic normal basé sur le profil

**Algorithme** :
```python
def _generate_normal_traffic(self, device_profile, timestamp):
    hour = timestamp.hour
    
    # Facteur d'activité selon l'heure
    if self._is_active_hour(hour, device_profile['activity_hours']):
        activity_factor = 1.0
        
        # Pics d'activité
        if hour in device_profile.get('peak_hours', []):
            activity_factor = random.uniform(1.5, 2.5)
        
        # Volume de base avec variations
        base_volume = random.uniform(*device_profile['volume_range'])
        volume = base_volume * activity_factor
        
        # Sélection port aléatoire du profil
        port = random.choice(device_profile['base_ports'])
        protocol = random.choice(device_profile['protocols'])
        
        return {
            'volume': volume,
            'port': port,
            'protocol': protocol,
            'is_anomaly': False
        }
```

#### 3. `_generate_anomalous_traffic(device_profile, timestamp)`
**Objectif** : Crée des anomalies réalistes pour test du modèle

**Types d'anomalies générées** :
```python
anomaly_types = {
    'volume_spike': {
        'description': 'Volume anormalement élevé',
        'implementation': lambda vol: vol * random.uniform(5, 15),
        'probability': 0.3
    },
    'unusual_port': {
        'description': 'Port inhabituel ou suspect',
        'ports': [1234, 4444, 6666, 9999, 31337],  # Ports backdoor
        'probability': 0.25
    },
    'night_activity': {
        'description': 'Activité en dehors des heures normales',
        'hours': [2, 3, 4, 5],  # 2h-5h du matin
        'probability': 0.2
    },
    'protocol_anomaly': {
        'description': 'Protocole inhabituel',
        'protocols': ['ICMP', 'GRE', 'ESP'],  # Protocoles tunneling
        'probability': 0.15
    },
    'rapid_connections': {
        'description': 'Multiples connexions rapides',
        'connection_count': random.randint(50, 200),
        'time_window': 60,  # 60 secondes
        'probability': 0.1
    }
}
```

#### 4. `generate_network_data(num_devices, hours, anomaly_percentage)`
**Objectif** : Génère un dataset complet avec timeline réaliste

**Paramètres** :
- `num_devices` : Nombre d'appareils à simuler (recommandé : 20-100)
- `hours` : Période de simulation (24h = 1 jour complet)
- `anomaly_percentage` : Pourcentage d'anomalies (5-15% réaliste)

**Algorithme de génération** :
```python
def generate_network_data(self, num_devices=50, hours=24, anomaly_percentage=8):
    network_data = []
    start_time = datetime.now() - timedelta(hours=hours)
    
    # Génération des appareils
    devices = self._create_device_fleet(num_devices)
    
    # Timeline par intervalles de 5 minutes
    for minute_offset in range(0, hours * 60, 5):
        current_time = start_time + timedelta(minutes=minute_offset)
        
        # Pour chaque appareil actif
        for device in devices:
            if self._is_device_active(device, current_time):
                
                # Décision anomalie
                if random.random() < (anomaly_percentage / 100):
                    traffic = self._generate_anomalous_traffic(device, current_time)
                else:
                    traffic = self._generate_normal_traffic(device, current_time)
                
                # Ajout métadonnées
                record = {
                    'timestamp': current_time,
                    'device_id': device['id'],
                    'ip_address': device['ip'],
                    'mac_address': device['mac'],
                    'device_type': device['type'],
                    **traffic
                }
                
                network_data.append(record)
    
    return pd.DataFrame(network_data)
```

### Pourquoi ce Simulateur ?
- **Réalisme** : Patterns basés sur comportements réels d'entreprise
- **Contrôle** : Anomalies injectées de manière contrôlée
- **Diversité** : Multiple types d'appareils et d'anomalies
- **Évolutivité** : Facile d'ajouter nouveaux profils

## 3. anomaly_detector.py - Cœur de l'Intelligence Artificielle

### Rôle et Responsabilités
- **Intelligence artificielle** : Implémente l'algorithme Isolation Forest
- **Feature Engineering** : Transforme données brutes en features ML
- **Entraînement** : Apprend les patterns normaux du réseau
- **Détection** : Identifie anomalies temps réel avec scoring

### Architecture de la Classe AnomalyDetector

```python
class AnomalyDetector:
    def __init__(self):
        self.model = None                    # Modèle Isolation Forest
        self.scaler = StandardScaler()       # Normalisation features
        self.label_encoders = {}            # Encodage variables catégorielles
        self.feature_columns = []           # Liste des features utilisées
        self.is_trained = False             # État entraînement
        self.training_stats = {}            # Statistiques entraînement
```

### Fonctions Principales Techniques

#### 1. `_prepare_features(df, fit_encoders=False)` - Feature Engineering

**Objectif** : Transforme données réseau brutes en features numériques pour l'IA

**Features temporelles** :
```python
# Cyclicité temporelle (sine/cosine encoding)
data['hour_sin'] = np.sin(2 * np.pi * data['hour'] / 24)
data['hour_cos'] = np.cos(2 * np.pi * data['hour'] / 24)
data['day_sin'] = np.sin(2 * np.pi * data['day_of_week'] / 7)
data['day_cos'] = np.cos(2 * np.pi * data['day_of_week'] / 7)

# Pourquoi sine/cosine ? 
# - Préserve la cyclicité (23h proche de 0h)
# - Évite discontinuité artificielle
# - ML comprend mieux les patterns temporels
```

**Features statistiques agrégées** :
```python
# Calculs roulants par appareil (fenêtre 1h)
device_stats = data.groupby('device_id').rolling('1H', on='timestamp').agg({
    'data_volume_mb': ['mean', 'std', 'max', 'min'],
    'port': 'nunique',  # Nombre ports uniques
    'protocol': 'nunique'
}).fillna(method='forward')

features_df['avg_data_volume'] = device_stats['data_volume_mb']['mean']
features_df['std_data_volume'] = device_stats['data_volume_mb']['std']
features_df['max_data_volume'] = device_stats['data_volume_mb']['max']
features_df['unique_ports'] = device_stats['port']['nunique']
```

**Features catégorielles** :
```python
# Encodage des types d'appareils et protocoles
categorical_features = ['device_type', 'protocol']

for feature in categorical_features:
    if fit_encoders:  # Mode entraînement
        self.label_encoders[feature] = LabelEncoder()
        encoded_values = self.label_encoders[feature].fit_transform(
            data[feature].fillna('unknown')
        )
    else:  # Mode prédiction
        # Gestion valeurs inconnues
        def safe_transform(values):
            known_classes = set(self.label_encoders[feature].classes_)
            safe_values = [v if v in known_classes else 'unknown' for v in values]
            return self.label_encoders[feature].transform(safe_values)
        
        encoded_values = safe_transform(data[feature].fillna('unknown'))
    
    features_df[f'{feature}_encoded'] = encoded_values
```

**Features de ports** :
```python
# Classification intelligence des ports
common_ports = [22, 25, 53, 80, 110, 143, 443, 993, 995, 3389, 5432, 3306]
features_df['is_common_port'] = data['port'].isin(common_ports).astype(int)
features_df['is_system_port'] = (data['port'] <= 1024).astype(int)
features_df['is_ephemeral_port'] = (data['port'] >= 32768).astype(int)
features_df['is_registered_port'] = ((data['port'] > 1024) & (data['port'] < 49152)).astype(int)
```

#### 2. `train_model(df, contamination=0.1)` - Entraînement IA

**Objectif** : Entraîne le modèle Isolation Forest sur données normales

**Paramètres techniques** :
```python
self.model = IsolationForest(
    contamination=0.1,      # 10% de données considérées comme anomalies
    random_state=42,        # Reproductibilité
    n_estimators=100,       # 100 arbres dans la forêt
    max_samples='auto',     # Échantillonnage automatique
    bootstrap=False,        # Pas de bootstrap (évite overfitting)
    max_features=1.0,       # Utilise toutes les features
    behaviour='new'         # Version récente algorithme
)
```

**Algorithme Isolation Forest Détaillé** :

1. **Construction des Arbres** :
```python
# Pour chaque arbre de la forêt :
def build_isolation_tree(data, max_depth):
    if len(data) <= 1 or max_depth <= 0:
        return LeafNode(size=len(data))
    
    # Sélection aléatoire d'une feature
    feature = random.choice(available_features)
    
    # Sélection point de split aléatoire
    min_val, max_val = data[feature].min(), data[feature].max()
    split_point = random.uniform(min_val, max_val)
    
    # Division des données
    left_data = data[data[feature] < split_point]
    right_data = data[data[feature] >= split_point]
    
    # Récursion
    left_child = build_isolation_tree(left_data, max_depth - 1)
    right_child = build_isolation_tree(right_data, max_depth - 1)
    
    return InternalNode(feature, split_point, left_child, right_child)
```

2. **Calcul Score d'Anomalie** :
```python
def anomaly_score(point, trees):
    path_lengths = []
    
    for tree in trees:
        path_length = compute_path_length(point, tree, depth=0)
        path_lengths.append(path_length)
    
    avg_path_length = np.mean(path_lengths)
    
    # Normalisation selon formule Isolation Forest
    # s(x,n) = 2^(-E(h(x))/c(n))
    # où c(n) = 2*H(n-1) - (2*(n-1)/n) (longueur moyenne path BST)
    normalized_score = 2 ** (-avg_path_length / average_path_length_BST(n))
    
    return normalized_score  # Score entre 0 et 1
```

3. **Interprétation Scores** :
- **Score proche de 1** : Anomalie très probable (isolé rapidement)
- **Score proche de 0.5** : Comportement normal
- **Score proche de 0** : Très normal (difficile à isoler)

#### 3. `detect_anomalies(df)` - Détection Temps Réel

**Objectif** : Applique le modèle entraîné sur nouvelles données

**Pipeline de détection** :
```python
def detect_anomalies(self, df):
    # 1. Vérification modèle entraîné
    if not self.is_trained:
        raise ValueError("Modèle non entraîné")
    
    # 2. Préparation features (sans réentraînement encodeurs)
    X = self._prepare_features(df, fit_encoders=False)
    
    # 3. Normalisation avec scaler entraîné
    X_scaled = self.scaler.transform(X)
    
    # 4. Prédiction binaire (-1 = anomalie, 1 = normal)
    predictions = self.model.predict(X_scaled)
    
    # 5. Scores continus (plus négatif = plus anormal)
    anomaly_scores = self.model.score_samples(X_scaled)
    
    # 6. Normalisation scores vers [0,1]
    min_score = anomaly_scores.min()
    max_score = anomaly_scores.max()
    confidence_scores = 1 - (anomaly_scores - min_score) / (max_score - min_score)
    
    # 7. Classification par seuils
    def classify_severity(confidence):
        if confidence >= 0.8:    return 'Critique'
        elif confidence >= 0.6:  return 'Élevé'
        elif confidence >= 0.4:  return 'Moyen'
        else:                   return 'Faible'
    
    # 8. Création DataFrame résultats
    results = df.copy()
    results['predicted_anomaly'] = (predictions == -1).astype(int)
    results['anomaly_score'] = anomaly_scores
    results['anomaly_confidence'] = confidence_scores
    results['severity'] = confidence_scores.apply(classify_severity)
    
    # 9. Filtrage anomalies uniquement
    anomalies = results[results['predicted_anomaly'] == 1]
    
    return anomalies.sort_values('anomaly_confidence', ascending=False)
```

### Pourquoi Isolation Forest ?

**Avantages pour la cybersécurité** :
- **Apprentissage non supervisé** : Pas besoin d'exemples d'attaques
- **Efficace sur outliers** : Détecte comportements rares naturellement
- **Scalable** : Performance linéaire O(n log n)
- **Robuste** : Résistant au bruit dans les données
- **Explicable** : Score continu interprétable

**Limitations connues** :
- **Données déséquilibrées** : Si >50% anomalies, performance dégradée
- **Features irrelevantes** : Nécessite bon feature engineering
- **Concept drift** : Besoin réentraînement périodique

## 4. dashboard_clean.py - Interface Professionnelle

### Rôle et Responsabilités
- **Visualisation temps réel** : Affiche métriques et graphiques actualisés
- **Interface corporate** : Design professionnel pour entreprises
- **Interaction utilisateur** : Contrôles et filtres avancés
- **Reporting** : Génération de rapports et exports

### Architecture de la Classe Dashboard

```python
class Dashboard:
    def __init__(self):
        self.color_scheme = self._init_corporate_colors()
        self.chart_templates = self._init_chart_templates()
        self.refresh_interval = 30  # secondes
```

### Fonctions de Visualisation Détaillées

#### 1. `_render_system_status()` - État Système Temps Réel

**Métriques affichées** :
```python
def _render_system_status(self, network_data, anomalies_data, model_trained):
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_devices = network_data['device_id'].nunique()
        st.metric(
            label="Appareils Actifs",
            value=total_devices,
            delta=f"+{new_devices_today}" if new_devices_today > 0 else None
        )
    
    with col2:
        anomaly_count = len(anomalies_data)
        critical_anomalies = len(anomalies_data[anomalies_data['severity'] == 'Critique'])
        st.metric(
            label="Anomalies Détectées",
            value=anomaly_count,
            delta=f"{critical_anomalies} critiques" if critical_anomalies > 0 else "Aucune critique",
            delta_color="inverse"
        )
    
    with col3:
        total_volume = network_data['data_volume_mb'].sum()
        st.metric(
            label="Volume Total (MB)",
            value=f"{total_volume:.1f}",
            delta=f"{volume_trend}%" if volume_trend != 0 else None
        )
    
    with col4:
        model_status = "Opérationnel" if model_trained else "Non entraîné"
        accuracy = self._calculate_model_accuracy() if model_trained else 0
        st.metric(
            label="Statut IA",
            value=model_status,
            delta=f"{accuracy:.1%} précision" if model_trained else "Entraînement requis"
        )
```

#### 2. `_render_traffic_timeline()` - Analyse Temporelle

**Graphique principal** :
```python
def _render_traffic_timeline(self, network_data, anomalies_data):
    # Agrégation temporelle par heure
    hourly_traffic = network_data.groupby(
        network_data['timestamp'].dt.floor('H')
    ).agg({
        'data_volume_mb': 'sum',
        'device_id': 'nunique',
        'port': 'nunique'
    }).reset_index()
    
    # Création graphique Plotly avec double axe Y
    fig = make_subplots(
        rows=1, cols=1,
        secondary_y=True,
        subplot_titles=["Trafic Réseau Temporel"]
    )
    
    # Volume de données (axe principal)
    fig.add_trace(
        go.Scatter(
            x=hourly_traffic['timestamp'],
            y=hourly_traffic['data_volume_mb'],
            mode='lines+markers',
            name='Volume (MB)',
            line=dict(color='#00D4FF', width=2),
            fill='tonexty'
        )
    )
    
    # Nombre d'appareils (axe secondaire)
    fig.add_trace(
        go.Scatter(
            x=hourly_traffic['timestamp'],
            y=hourly_traffic['device_id'],
            mode='lines',
            name='Appareils Actifs',
            line=dict(color='#FF6B6B', width=2),
            yaxis='y2'
        ),
        secondary_y=True
    )
    
    # Overlay des anomalies
    if not anomalies_data.empty:
        fig.add_trace(
            go.Scatter(
                x=anomalies_data['timestamp'],
                y=anomalies_data['data_volume_mb'],
                mode='markers',
                name='Anomalies',
                marker=dict(
                    color='red',
                    size=8,
                    symbol='x',
                    line=dict(width=2, color='darkred')
                )
            )
        )
    
    # Configuration axes et style
    fig.update_layout(
        title="Évolution du Trafic Réseau",
        xaxis_title="Temps",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=400
    )
    
    fig.update_yaxes(title_text="Volume (MB)", secondary_y=False)
    fig.update_yaxes(title_text="Nombre d'Appareils", secondary_y=True)
    
    st.plotly_chart(fig, use_container_width=True)
```

#### 3. `_render_device_activity()` - Heatmap d'Activité

```python
def _render_device_activity(self, network_data):
    # Création pivot table pour heatmap
    activity_matrix = network_data.pivot_table(
        index='device_id',
        columns=network_data['timestamp'].dt.hour,
        values='data_volume_mb',
        aggfunc='sum',
        fill_value=0
    )
    
    # Graphique heatmap
    fig = go.Figure(data=go.Heatmap(
        z=activity_matrix.values,
        x=activity_matrix.columns,  # Heures
        y=activity_matrix.index,    # Appareils
        colorscale='Viridis',
        colorbar=dict(title="Volume (MB)"),
        hoverongaps=False
    ))
    
    fig.update_layout(
        title="Heatmap d'Activité par Appareil",
        xaxis_title="Heure de la Journée",
        yaxis_title="Identifiant Appareil",
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
```

#### 4. `_render_port_analysis()` - Analyse des Ports

```python
def _render_port_analysis(self, network_data, anomalies_data):
    # Top ports utilisés
    port_usage = network_data.groupby('port').agg({
        'data_volume_mb': 'sum',
        'device_id': 'nunique'
    }).sort_values('data_volume_mb', ascending=False).head(15)
    
    # Classification des ports
    def classify_port(port):
        if port <= 1023:
            return 'Système'
        elif port <= 49151:
            return 'Enregistré'
        else:
            return 'Dynamique'
    
    port_usage['category'] = port_usage.index.map(classify_port)
    
    # Graphique en barres
    fig = px.bar(
        port_usage.reset_index(),
        x='port',
        y='data_volume_mb',
        color='category',
        title="Top 15 Ports par Volume",
        labels={'data_volume_mb': 'Volume (MB)', 'port': 'Port'}
    )
    
    # Annotation ports suspects
    suspicious_ports = [1234, 4444, 6666, 9999, 31337]
    for port in suspicious_ports:
        if port in port_usage.index:
            fig.add_annotation(
                x=port,
                y=port_usage.loc[port, 'data_volume_mb'],
                text="SUSPECT",
                showarrow=True,
                arrowcolor="red"
            )
    
    st.plotly_chart(fig, use_container_width=True)
```

## Continuons avec les autres fichiers dans le prochain guide...

Cette analyse détaillée vous donne une compréhension complète de l'architecture et du fonctionnement de chaque composant. Souhaitez-vous que je continue avec les fichiers restants (base de données, collecte réseau, etc.) ?