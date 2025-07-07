# Installation AEGISLAN sur Ubuntu 24.04

## Prérequis et Installation

### 1. Mise à jour du système
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Installation de Python et pip
```bash
sudo apt install python3 python3-pip python3-venv -y
```

### 3. Téléchargement du projet depuis Replit
```bash
# Créer dossier de travail
mkdir ~/aegislan
cd ~/aegislan

# Télécharger les fichiers depuis Replit (copier-coller le contenu)
# Ou utiliser git si vous avez poussé sur GitHub
```

### 4. Création de l'environnement virtuel
```bash
# Créer environnement virtuel
python3 -m venv aegislan_env

# Activer l'environnement
source aegislan_env/bin/activate
```

### 5. Installation des dépendances
```bash
# Installer les packages Python
pip install streamlit pandas numpy plotly scikit-learn

# Ou si vous avez un requirements.txt
pip install -r requirements.txt
```

## Déploiement Local

### 1. Test de l'application
```bash
# Dans le dossier aegislan avec environnement activé
streamlit run app.py
```
L'application sera accessible sur `http://localhost:8501`

### 2. Accès depuis le réseau local
```bash
# Pour accès depuis autres machines du réseau
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```
Accessible sur `http://[IP_DE_VOTRE_PC]:8501`

### 3. Trouver l'IP de votre machine
```bash
# Afficher l'adresse IP
ip addr show | grep "inet " | grep -v 127.0.0.1
```

## Configuration en Service Système

### 1. Créer un utilisateur dédié
```bash
sudo useradd -r -s /bin/false aegislan
sudo mkdir -p /opt/aegislan
sudo cp -r ~/aegislan/* /opt/aegislan/
sudo chown -R aegislan:aegislan /opt/aegislan
```

### 2. Créer le fichier de service systemd
```bash
sudo nano /etc/systemd/system/aegislan.service
```

Contenu du fichier :
```ini
[Unit]
Description=AEGISLAN Network Anomaly Detection System
After=network.target

[Service]
Type=simple
User=aegislan
Group=aegislan
WorkingDirectory=/opt/aegislan
Environment=PATH=/opt/aegislan/aegislan_env/bin
ExecStart=/opt/aegislan/aegislan_env/bin/streamlit run app.py --server.address 0.0.0.0 --server.port 8501
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### 3. Activer et démarrer le service
```bash
# Recharger systemd
sudo systemctl daemon-reload

# Activer le service au démarrage
sudo systemctl enable aegislan

# Démarrer le service
sudo systemctl start aegislan

# Vérifier le statut
sudo systemctl status aegislan
```

### 4. Gestion du service
```bash
# Arrêter le service
sudo systemctl stop aegislan

# Redémarrer le service
sudo systemctl restart aegislan

# Voir les logs
sudo journalctl -u aegislan -f
```

## Configuration du pare-feu

### 1. Ouvrir le port 8501
```bash
# Si ufw est actif
sudo ufw allow 8501

# Ou avec iptables
sudo iptables -A INPUT -p tcp --dport 8501 -j ACCEPT
sudo iptables-save > /etc/iptables/rules.v4
```

### 2. Vérifier que le port est ouvert
```bash
sudo netstat -tlnp | grep :8501
```

## Configuration avec Nginx (Optionnel)

### 1. Installation de Nginx
```bash
sudo apt install nginx -y
```

### 2. Configuration Nginx
```bash
sudo nano /etc/nginx/sites-available/aegislan
```

Contenu :
```nginx
server {
    listen 80;
    server_name aegislan.local;  # ou votre domaine

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. Activer la configuration
```bash
sudo ln -s /etc/nginx/sites-available/aegislan /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Accès et URLs

### Accès local
- Direct : `http://localhost:8501`
- Via Nginx : `http://localhost` ou `http://aegislan.local`

### Accès réseau
- Direct : `http://[IP_DE_VOTRE_PC]:8501`
- Via Nginx : `http://[IP_DE_VOTRE_PC]`

### Trouver l'IP de votre machine
```bash
hostname -I | awk '{print $1}'
```

## Scripts utiles

### Script de démarrage rapide
```bash
# Créer ~/start_aegislan.sh
#!/bin/bash
cd ~/aegislan
source aegislan_env/bin/activate
streamlit run app.py --server.address 0.0.0.0
```

```bash
chmod +x ~/start_aegislan.sh
```

### Script de sauvegarde
```bash
# Créer ~/backup_aegislan.sh
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf ~/aegislan_backup_$DATE.tar.gz -C /opt aegislan
echo "Sauvegarde créée : ~/aegislan_backup_$DATE.tar.gz"
```

## Dépannage

### Problèmes courants

**Port déjà utilisé :**
```bash
# Tuer le processus utilisant le port 8501
sudo fuser -k 8501/tcp
```

**Problème de permissions :**
```bash
sudo chown -R $USER:$USER ~/aegislan
chmod +x ~/aegislan/*.py
```

**Streamlit ne démarre pas :**
```bash
# Vérifier l'installation
python3 -c "import streamlit; print('Streamlit OK')"

# Réinstaller si nécessaire
pip install --upgrade streamlit
```

### Logs et monitoring
```bash
# Logs du service
sudo journalctl -u aegislan -n 50

# Logs Streamlit en temps réel
tail -f ~/.streamlit/logs/streamlit.log

# Utilisation des ressources
htop
```

## Sécurisation (Production)

### 1. Configuration firewall stricte
```bash
# Fermer tous les ports sauf SSH et AEGISLAN
sudo ufw --force reset
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 8501
sudo ufw enable
```

### 2. Authentification basique avec Nginx
```bash
# Installer apache2-utils pour htpasswd
sudo apt install apache2-utils -y

# Créer fichier de mots de passe
sudo htpasswd -c /etc/nginx/.htpasswd admin

# Ajouter dans la config Nginx
auth_basic "AEGISLAN Access";
auth_basic_user_file /etc/nginx/.htpasswd;
```

### 3. Monitoring automatique
```bash
# Ajouter dans crontab
crontab -e

# Vérifier toutes les 5 minutes que le service fonctionne
*/5 * * * * systemctl is-active --quiet aegislan || systemctl restart aegislan
```

L'application sera maintenant accessible de manière permanente sur votre réseau local à l'adresse `http://[IP_DE_VOTRE_PC]:8501`