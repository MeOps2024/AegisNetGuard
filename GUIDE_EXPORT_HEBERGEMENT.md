Guide d’Export et Hébergement AEGISLAN
Solutions pour Présenter en Temps Réel

Export du Projet


###  Export du Projet

#### Fichiers à exporter
Votre projet AEGISLAN contient :

aegislan/
├── app.py                    # Application principale
├── data_simulator.py         # Simulateur de données réseau
├── anomaly_detector.py       # Moteur IA de détection
├── dashboard.py              # Interface utilisateur
├── pyproject.toml           # Dépendances Python
├── .streamlit/config.toml   # Configuration Streamlit
├── GUIDE_UTILISATION.md     # Guide utilisateur
└── DOCUMENTATION_DEVELOPPEUR.md  # Guide technique
Commandes d’export depuis Replit

# Créer une archive du projet
tar -czf aegislan_projet.tar.gz *.py *.md .streamlit/ pyproject.toml

# Ou télécharger fichier par fichier via l’interface Replit

Option 1 : Déploiement sur Windows Server 2012 R2

1. Installer Python

    Télécharger Python 3.11 sur python.org

    Lancer l’installation en cochant "Add Python to PATH"

2. Installer les dépendances

pip install streamlit pandas numpy plotly scikit-learn

3. Activer IIS (Internet Information Services)

Enable-WindowsOptionalFeature -Online -FeatureName IIS-WebServerRole
Enable-WindowsOptionalFeature -Online -FeatureName IIS-WebServer
Enable-WindowsOptionalFeature -Online -FeatureName IIS-CommonHttpFeatures
Enable-WindowsOptionalFeature -Online -FeatureName IIS-HttpErrors
Enable-WindowsOptionalFeature -Online -FeatureName IIS-HttpRedirect

4. Déployer l’application

    Copier le dossier dans C:\inetpub\wwwroot\aegislan\

    Créer un fichier aegislan.bat avec le contenu :

@echo off
cd C:\inetpub\wwwroot\aegislan
python -m streamlit run app.py --server.port 8501 --server.address 0.0.0.0

5. Ouvrir le port dans le pare-feu

netsh advfirewall firewall add rule name="AEGISLAN Streamlit" dir=in action=allow protocol=TCP localport=8501

6. Accès

    Depuis un autre appareil : http://[IP_DU_SERVEUR]:8501

Option 2 : Hébergement Gratuit en Ligne

A. Streamlit Community Cloud

Avantages :

    Gratuit

    Dédié à Streamlit

    SSL automatique

    Déploiement simple depuis GitHub

Étapes :

    Créer un compte GitHub et y pousser le code

    Aller sur share.streamlit.io

    Connecter votre repo GitHub

    Cliquer sur "Deploy"

Exemple d’URL obtenue :
https://username-aegislan-app-main-xxxxx.streamlit.app

B. Railway (Alternative avancée)

Avantages :

    500 heures gratuites/mois

    Support Streamlit

    Domaine personnalisable

Étapes :

    Créer un compte sur railway.app

    "New Project" > "Deploy from GitHub"

    Configurer la commande d’exécution si nécessaire

Exemple d’URL :
https://aegislan.up.railway.app

C. Render

Avantages :

    750 heures gratuites/mois

    SSL et déploiement auto

    Logs en temps réel

Étapes :

    Créer un compte sur render.com

    "New Web Service" > connecter GitHub

    Commande de démarrage :

streamlit run app.py --server.port $PORT

Fichiers à Préparer

requirements.txt

streamlit==1.28.0
pandas==2.1.0
numpy==1.24.0
plotly==5.15.0
scikit-learn==1.3.0

Procfile (pour Render ou Railway)

web: streamlit run app.py --server.port $PORT --server.address 0.0.0.0

Script de Démonstration Automatique (optionnel)

demo_auto.py

import time
import streamlit as st

def run_auto_demo():
    st.info("Démonstration automatique en cours...")

    with st.spinner("Génération des données..."):
        time.sleep(2)
    st.success("Données générées")

    with st.spinner("Entraînement de l’IA..."):
        time.sleep(3)
    st.success("Modèle entraîné")

    with st.spinner("Détection d’anomalies..."):
        time.sleep(2)
    st.success("Analyse terminée")

Procédure Recommandée pour Présentation Professionnelle

1. Préparer le code

echo "streamlit==1.28.0
pandas==2.1.0
numpy==1.24.0
plotly==5.15.0
scikit-learn==1.3.0" > requirements.txt

2. Pousser sur GitHub

git init
git add .
git commit -m "Initial AEGISLAN deployment"
git branch -M main
git remote add origin https://github.com/[username]/aegislan.git
git push -u origin main

3. Déployer sur Streamlit Cloud

    Aller sur share.streamlit.io

    Cliquer sur "New app"

    Choisir le dépôt et lancer le déploiement

4. Partager l’URL obtenue
(avec les responsables, partenaires, ou lors d’une soutenance)

Script Oral de Présentation (Exemple)

Introduction
"Bonjour. Ce que vous allez voir est AEGISLAN, un système de cybersécurité intelligent que j’ai développé. Il surveille en temps réel l’activité réseau d’une entreprise pour détecter automatiquement les comportements suspects."

Démonstration Live

    Lancement de l’interface web

    Génération de données

    Entraînement de l’intelligence artificielle

    Détection des anomalies

    Présentation des résultats sur le tableau de bord

Conclusion
"L’application fonctionne dans un environnement en ligne sécurisé, elle est prête pour être testée ou intégrée dans un réseau réel. Elle offre une surveillance intelligente, rapide et autonome, accessible via une simple URL."

Coûts Estimés

Gratuit :

    Streamlit Community Cloud : 0 €

    Railway (plan Free) : 0 €

    Render (plan Free) : 0 €

Payant (si montée en charge) :

    Railway Pro : environ 5 $ / mois

    Render Starter : environ 7 $ / mois

    Hébergement Windows Server : dépend de l’infrastructure existante

Sécurité de la Démo

    Aucune donnée réelle utilisée

    100 % simulation locale

    Pas de connexion sortante

    Possibilité de restreindre l’accès via mot de passe ou filtrage IP
