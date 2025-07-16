# GUIDE COMPLET DES TECHNOLOGIES AEGISLAN

## Vue d'ensemble du Système

AEGISLAN est un système de détection d'anomalies réseau (NDR - Network Detection & Response) basé sur l'intelligence artificielle. Il surveille en temps réel le trafic réseau d'une entreprise pour identifier automatiquement les comportements suspects et potentiellement malveillants.

## Pourquoi cette Architecture IA ?

### Problème Résolu
- **Limitation des systèmes traditionnels** : Les solutions de sécurité basées sur signatures ne détectent que les menaces connues
- **Volume de données** : Les réseaux d'entreprise génèrent des téraoctets de logs quotidiennement, impossibles à analyser manuellement
- **Attaques Zero-Day** : Les nouvelles menaces n'ont pas de signatures connues
- **Faux positifs** : Les systèmes basés sur règles génèrent trop d'alertes non pertinentes

### Solution AEGISLAN
- **Apprentissage non supervisé** : Détecte les anomalies sans avoir besoin d'exemples d'attaques préalables
- **Analyse comportementale** : Apprend les patterns normaux du réseau et détecte les déviations
- **Traitement temps réel** : Analyse continue avec alertes instantanées
- **Interface intuitive** : Dashboard professionnel pour les équipes de sécurité

## Technologies, Langages et Frameworks

### 1. Python 3.11 - Langage Principal

**Rôle général** : Langage de programmation polyvalent orienté objet et fonctionnel

**Utilisation dans AEGISLAN** :
- Traitement et analyse des données réseau
- Implémentation des algorithmes d'IA
- Interface web et visualisations
- Gestion des bases de données
- Collecte de données réseau

**Pourquoi Python ?** :
- Écosystème IA/ML le plus riche au monde (scikit-learn, pandas, numpy)
- Libraries réseau natives (socket, psutil, subprocess)
- Développement rapide et maintenance facile
- Intégration simple avec outils système (Nmap, SNMP)
- Performance suffisante pour traitement temps réel réseau

### 2. Streamlit - Framework Interface Web

**Rôle général** : Framework web Python pour créer rapidement des applications de data science

**Utilisation dans AEGISLAN** :
- Interface utilisateur principale du dashboard
- Affichage temps réel des métriques réseau
- Panneaux de contrôle pour configuration IA
- Visualisation interactive des anomalies
- Reports et exports de données

**Pourquoi Streamlit ?** :
- Développement ultra-rapide (pas de HTML/CSS/JavaScript)
- Intégration native avec pandas et plotly
- Auto-refresh pour monitoring temps réel
- Déploiement simple en une commande
- Thèmes professionnels intégrés

**Architecture Streamlit dans AEGISLAN** :
```python
# Structure modulaire
app.py               # Point d'entrée principal
├── Sidebar          # Contrôles et paramètres
├── Main Dashboard   # Vue d'ensemble temps réel
├── Network Analysis # Analyse détaillée trafic
├── Threat Detection # Gestion anomalies
├── System Config    # Configuration système
└── Reports          # Exports et rapports
```

### 3. Scikit-learn - Machine Learning

**Rôle général** : Bibliothèque d'apprentissage automatique la plus utilisée en Python

**Utilisation dans AEGISLAN** :
- Algorithme Isolation Forest pour détection anomalies
- Preprocessing des données (StandardScaler, LabelEncoder)
- Pipeline de traitement des features
- Validation et métriques de performance

**Pourquoi Scikit-learn ?** :
- Implémentation Isolation Forest optimisée et testée
- API cohérente et bien documentée
- Intégration parfaite avec pandas/numpy
- Performance production-ready
- Écosystème mature avec support communautaire

**Isolation Forest - Principe Technique** :
```
1. Construction d'arbres binaires aléatoires
2. Isolation des points par subdivisions récursives
3. Calcul du chemin moyen d'isolation pour chaque point
4. Points isolés rapidement = anomalies (chemin court)
5. Points normaux = chemin long dans l'arbre
```

### 4. Pandas - Manipulation de Données

**Rôle général** : Bibliothèque d'analyse et manipulation de données structurées

**Utilisation dans AEGISLAN** :
- Traitement des logs réseau (parsing, nettoyage, transformation)
- Agrégations temporelles (par heure, jour, appareil)
- Jointures entre données réseau et métadonnées appareils
- Calculs statistiques (moyennes, écarts-types, percentiles)
- Interface avec bases de données

**Pourquoi Pandas ?** :
- Performance optimisée pour gros datasets (C/Cython backend)
- API intuitive pour manipulations complexes
- Fonctions temporelles avancées (resampling, rolling windows)
- Intégration native avec scikit-learn
- Formats d'import/export multiples (CSV, JSON, SQL, Parquet)

### 5. Plotly - Visualisation Interactive

**Rôle général** : Bibliothèque de graphiques interactifs pour web

**Utilisation dans AEGISLAN** :
- Graphiques temps réel du trafic réseau
- Heatmaps d'activité par appareil/heure
- Scatter plots des anomalies avec scores
- Histogrammes de distribution ports/protocoles
- Graphiques en camembert répartition traffic

**Pourquoi Plotly ?** :
- Interactivité native (zoom, hover, filtres)
- Rendu web optimisé avec WebGL
- Thèmes corporate professionnels
- Export haute résolution (PNG, SVG, PDF)
- Intégration seamless avec Streamlit

### 6. NumPy - Calculs Numériques

**Rôle général** : Bibliothèque de calcul scientifique fondamentale

**Utilisation dans AEGISLAN** :
- Calculs vectorisés sur arrays de données réseau
- Opérations mathématiques pour feature engineering
- Transformations trigonométriques (sin/cos) pour features temporelles
- Optimisation performance algorithmes ML

**Pourquoi NumPy ?** :
- Performance C-level sur opérations vectorielles
- Base de tout l'écosystème scientifique Python
- Gestion mémoire optimisée pour gros datasets
- Fonctions mathématiques complètes

## Outils de Déploiement et Collecte

### 7. Nmap - Scanning Réseau

**Rôle général** : Outil de découverte réseau et audit de sécurité

**Utilisation dans AEGISLAN** :
- Découverte automatique d'appareils sur le réseau
- Détection de services et ports ouverts
- Fingerprinting OS pour classification appareils
- Monitoring changements topologie réseau

**Pourquoi Nmap ?** :
- Standard de facto pour reconnaissance réseau
- Base de données fingerprints la plus complète
- Performance élevée avec techniques scan optimisées
- Sortie XML parsable programmatiquement
- Détection passive et active

**Intégration technique** :
```python
def scan_network_nmap(self, ports="1-1000"):
    cmd = f"nmap -sS -O -sV {self.network_range}"
    result = subprocess.run(cmd, capture_output=True, text=True)
    return self._parse_nmap_xml(result.stdout)
```

### 8. SNMP - Monitoring Équipements

**Rôle général** : Protocole de gestion et supervision d'équipements réseau

**Utilisation dans AEGISLAN** :
- Collecte métriques temps réel routeurs/switches
- Monitoring bande passante par interface
- Surveillance erreurs et collisions
- Statistiques utilisation CPU/mémoire équipements

**Pourquoi SNMP ?** :
- Protocole standard supporté par tous équipements réseau
- Métriques précises et temps réel
- Faible overhead réseau
- MIBs standardisées pour interopérabilité

### 9. psutil - Monitoring Système

**Rôle général** : Bibliothèque monitoring système multiplateforme

**Utilisation dans AEGISLAN** :
- Surveillance connexions réseau actives locales
- Monitoring utilisation CPU/mémoire/disque
- Détection processus suspects
- Statistiques interfaces réseau

**Pourquoi psutil ?** :
- API Python native (pas de commandes système)
- Multiplateforme (Windows/Linux/macOS)
- Performance optimisée
- Données temps réel précises

## Bases de Données

### 10. SQLite - Base de Développement

**Rôle général** : Base de données relationnelle embarquée

**Utilisation dans AEGISLAN** :
- Stockage données développement et tests
- Base locale pour démos et prototypage
- Persistence modèles IA entraînés
- Cache temporaire pour données fréquentes

**Pourquoi SQLite ?** :
- Zéro configuration (pas de serveur)
- Performance excellente pour lectures
- Fichier unique facilement déployable
- ACID compliant
- Intégration Python native

### 11. PostgreSQL - Base de Production

**Rôle général** : Système de gestion de base de données relationnelle-objet

**Utilisation dans AEGISLAN** :
- Stockage production pour gros volumes
- Données réseau historiques (millions d'enregistrements)
- Gestion concurrentielle multi-utilisateurs
- Fonctionnalités avancées (JSONB, Arrays, Index composites)

**Pourquoi PostgreSQL ?** :
- Scalabilité horizontale et verticale
- Types de données avancés (INET, MACADDR, JSONB)
- Index performants pour requêtes temporelles
- Réplication et haute disponibilité
- Écosystème cloud (Neon, AWS RDS, Azure)

## Architecture Globale

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Collecte Data  │───▶│   Traitement IA  │───▶│   Interface     │
│                 │    │                  │    │                 │
│ • Nmap Scan     │    │ • Preprocessing  │    │ • Streamlit UI  │
│ • SNMP Polling  │    │ • Isolation F.   │    │ • Plotly Charts │
│ • psutil Monitor│    │ • Classification │    │ • Real-time     │
│ • Log Parsing   │    │ • Scoring        │    │ • Alerting      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
                    ┌─────────────────────┐
                    │   Base de Données   │
                    │                     │
                    │ • SQLite (Dev)      │
                    │ • PostgreSQL (Prod) │
                    │ • Indexation        │
                    │ • Rétention         │
                    └─────────────────────┘
```

## Justification des Choix Techniques

### Performance
- **Python** : Compromis optimal performance/développement pour analyse de données
- **Pandas** : Backend C optimisé pour manipulations sur millions d'enregistrements
- **NumPy** : Vectorisation pour calculs 10x-100x plus rapides qu'en Python pur
- **PostgreSQL** : Gestion efficace de téraoctets avec index optimisés

### Maintenabilité
- **Streamlit** : Interface réactive sans code frontend complexe
- **Scikit-learn** : API stable et bien documentée
- **Standards** : Technologies mainstream avec large communauté

### Scalabilité
- **Architecture modulaire** : Séparation claire collecte/traitement/présentation
- **Base de données** : Migration facile SQLite → PostgreSQL selon charge
- **Déploiement** : Conteneurisation possible pour orchestration

### Sécurité
- **Isolation** : Chaque composant dans son environnement
- **Authentification** : Support LDAP/OAuth pour PostgreSQL
- **Chiffrement** : TLS pour communications base de données
- **Audit** : Logs complets de toutes opérations

Cette architecture permet une évolution progressive depuis un prototype de laboratoire jusqu'à un système de production enterprise gérant des centaines de milliers d'événements réseau par jour.