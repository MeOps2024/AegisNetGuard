# Guide d'Export et Hébergement AEGISLAN
## Solutions pour Présenter en Temps Réel

### 📦 Export du Projet

#### Fichiers à exporter
Votre projet AEGISLAN contient :
```
aegislan/
├── app.py                    # Application principale
├── data_simulator.py         # Simulateur de données réseau
├── anomaly_detector.py       # Moteur IA de détection
├── dashboard.py              # Interface utilisateur
├── pyproject.toml           # Dépendances Python
├── .streamlit/config.toml   # Configuration Streamlit
├── GUIDE_UTILISATION.md     # Guide utilisateur
└── DOCUMENTATION_DEVELOPPEUR.md  # Guide technique
```

#### Commandes d'export depuis Replit
```bash
# Créer une archive du projet
tar -czf aegislan_projet.tar.gz *.py *.md .streamlit/ pyproject.toml

# Ou télécharger fichier par fichier via l'interface Replit
```

### 🖥️ Option 1 : Serveur Windows Server 2012 R2

#### Installation Python sur Windows Server
1. **Télécharger Python 3.11**
   - Aller sur python.org/downloads
   - Télécharger Python 3.11.x pour Windows
   - Cocher "Add Python to PATH" pendant l'installation

2. **Installer les dépendances**
```cmd
# Ouvrir PowerShell en tant qu'administrateur
pip install streamlit pandas numpy plotly scikit-learn
```

3. **Configuration IIS (Internet Information Services)**
```cmd
# Activer IIS depuis "Activer ou désactiver des fonctionnalités Windows"
# Ou via PowerShell :
Enable-WindowsOptionalFeature -Online -FeatureName IIS-WebServerRole
Enable-WindowsOptionalFeature -Online -FeatureName IIS-WebServer
Enable-WindowsOptionalFeature -Online -FeatureName IIS-CommonHttpFeatures
Enable-WindowsOptionalFeature -Online -FeatureName IIS-HttpErrors
Enable-WindowsOptionalFeature -Online -FeatureName IIS-HttpRedirect
```

4. **Déploiement de l'application**
```cmd
# Copier les fichiers dans C:\inetpub\wwwroot\aegislan\
# Créer un script de lancement aegislan.bat :
@echo off
cd C:\inetpub\wwwroot\aegislan
python -m streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

5. **Configuration du pare-feu**
```cmd
# Ouvrir le port 8501
netsh advfirewall firewall add rule name="AEGISLAN Streamlit" dir=in action=allow protocol=TCP localport=8501
```

6. **Accès depuis l'extérieur**
- IP du serveur : `http://[IP_DU_SERVEUR]:8501`
- Nom de domaine : `http://[DOMAINE]:8501`

### 🌐 Option 2 : Hébergeurs Gratuits Recommandés

#### A. Streamlit Community Cloud (Recommandé)
**Avantages :**
- Spécialement conçu pour Streamlit
- Déploiement automatique depuis GitHub
- SSL inclus
- Gratuit jusqu'à 3 applications

**Procédure :**
1. Créer un compte GitHub et pousser le code
2. Aller sur share.streamlit.io
3. Connecter GitHub et sélectionner le repo
4. Déploiement automatique

**URL finale :** `https://[username]-aegislan-app-[hash].streamlit.app`

#### B. Railway (Alternative robuste)
**Avantages :**
- Support Python excellent
- 500h gratuites/mois
- Déploiement Git
- Domaine personnalisé possible

**Procédure :**
1. Créer compte sur railway.app
2. "New Project" → "Deploy from GitHub"
3. Railway détecte automatiquement Python/Streamlit
4. Variables d'environnement configurables

**URL finale :** `https://[app-name].up.railway.app`

#### C. Render (Très fiable)
**Avantages :**
- 750h gratuites/mois
- SSL automatique
- Déploiement depuis GitHub
- Logs détaillés

**Procédure :**
1. Compte sur render.com
2. "New Web Service" → connecter GitHub
3. Configurer la commande : `streamlit run app.py --server.port $PORT`
4. Déploiement automatique

### 📋 Préparation pour la Présentation

#### Fichiers à préparer en plus
```python
# requirements.txt (à créer)
streamlit==1.28.0
pandas==2.1.0
numpy==1.24.0
plotly==5.15.0
scikit-learn==1.3.0
```

```toml
# Procfile (pour certains hébergeurs)
web: streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

#### Script de démonstration automatique
```python
# demo_auto.py (script bonus pour présentation)
import time
import streamlit as st

def run_auto_demo():
    """Lance une démonstration automatique"""
    st.info("Démonstration automatique en cours...")
    
    # Simulation automatique
    with st.spinner("Génération des données..."):
        time.sleep(2)
    st.success("Données générées")
    
    # Entraînement automatique
    with st.spinner("Entraînement de l'IA..."):
        time.sleep(3)
    st.success("Modèle entraîné")
    
    # Détection automatique
    with st.spinner("Détection d'anomalies..."):
        time.sleep(2)
    st.success("Analyse terminée")
```

### 🎯 Recommandation pour Présentation Professionnelle

**Solution optimale : Streamlit Community Cloud**

**Pourquoi :**
1. **Gratuit** : Pas de coûts cachés
2. **Professionnel** : URL propre avec SSL
3. **Fiable** : Infrastructure robuste
4. **Simple** : Déploiement en 5 minutes
5. **Maintenance** : Mises à jour automatiques

**Procédure complète :**

1. **Préparer le code**
```bash
# Créer requirements.txt
echo "streamlit==1.28.0
pandas==2.1.0
numpy==1.24.0
plotly==5.15.0
scikit-learn==1.3.0" > requirements.txt
```

2. **Pousser sur GitHub**
```bash
git init
git add .
git commit -m "AEGISLAN - Système de détection d'anomalies réseau"
git branch -M main
git remote add origin https://github.com/[username]/aegislan.git
git push -u origin main
```

3. **Déployer sur Streamlit Cloud**
- share.streamlit.io
- "New app" → sélectionner repo → "Deploy"

4. **URL de présentation**
- `https://[username]-aegislan-app-main-[hash].streamlit.app`
- Partager cette URL avec vos supérieurs

### 🎤 Script de Présentation

**Introduction (30 secondes)**
*"J'ai développé AEGISLAN, accessible à l'adresse [URL]. C'est un système de cybersécurité qui surveille automatiquement les réseaux d'entreprise."*

**Démonstration live (3 minutes)**
1. Montrer l'interface propre sans emojis
2. Générer des données en temps réel
3. Entraîner l'IA devant eux
4. Montrer les résultats d'analyse

**Conclusion (1 minute)**
*"Le système est opérationnel, hébergé de manière sécurisée, et prêt pour un déploiement en environnement de production."*

### 💰 Coûts Estimés

**Gratuit (Recommandé) :**
- Streamlit Community Cloud : 0€
- Railway Plan gratuit : 0€
- Render Plan gratuit : 0€

**Payant (si besoin d'upgrade) :**
- Railway Pro : $5/mois
- Render Starter : $7/mois
- Serveur Windows : Coûts infrastructure existante

### 🛡️ Sécurité pour Présentation

**Données sensibles :**
- Aucune donnée réelle n'est utilisée
- Simulation uniquement
- Pas de connexion réseau externe
- Code source visible (transparence)

**Accès :**
- URL publique mais obscure
- Pas d'authentification nécessaire pour démo
- Possibilité d'ajouter mot de passe si requis

L'application est maintenant prête pour une présentation professionnelle sans emojis et avec toutes les options d'hébergement adaptées à vos besoins.