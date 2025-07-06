Ce Que J'ai Utilisé Pour la Simulation Réseau
Voici exactement ce que j'ai développé pour créer cette simulation réaliste :

1. Bibliothèques Python Utilisées
import pandas as pd          # Pour manipuler les données
import numpy as np           # Pour les calculs numériques
import random               # Pour la génération aléatoire
from datetime import datetime, timedelta  # Pour les horodatages
2. Types d'Appareils Simulés
J'ai défini 6 types d'appareils basés sur de vrais environnements d'entreprise :

device_types = ['workstation', 'server', 'printer', 'phone', 'tablet', 'iot_device']
3. Ports Réseau Réalistes
Les ports les plus utilisés dans les entreprises :

common_ports = [22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 3389, 5432, 3306]
Signification :

22 : SSH (administration à distance)
80/443 : HTTP/HTTPS (navigation web)
25 : SMTP (email)
3389 : RDP (bureau à distance Windows)
3306/5432 : MySQL/PostgreSQL (bases de données)
4. Profils Comportementaux Réalistes
Chaque type d'appareil a ses patterns d'utilisation :

Workstation (Poste de travail) :

Heures d'activité : 8h-18h (heures de bureau)
Ports préférés : 80, 443, 22, 3389
Fréquence : Élevée
Volume de données : 100-5000 MB
Serveur :

Heures d'activité : 24/7 (toujours actif)
Ports préférés : 22, 80, 443, 3306, 5432
Fréquence : Très élevée
Volume de données : 1000-50000 MB
Imprimante :

Heures d'activité : 7h-19h
Ports préférés : 9100, 631, 80
Fréquence : Faible
Volume de données : 1-100 MB
5. Génération d'Adresses Réseau
Adresses MAC (identifiants uniques) :

def _generate_mac_address(self):
    return ":".join([f"{random.randint(0, 255):02x}" for _ in range(6)])
Génère : "aa:bb:cc:dd:ee:ff"

Adresses IP :

def _generate_ip_address(self, subnet="192.168.1"):
    return f"{subnet}.{random.randint(10, 254)}"
Génère : "192.168.1.123"

6. Algorithme de Simulation
Processus de génération :

Création des profils d'appareils avec comportements spécifiques

Génération temporelle par tranches de 10 minutes

Décision d'activité basée sur :

L'heure actuelle
Le type d'appareil
La probabilité d'activité
Injection d'anomalies selon le pourcentage défini

7. Types d'Anomalies Simulées
J'ai programmé 5 types d'anomalies réalistes :

Port inhabituel : Utilisation de ports jamais vus (1024-65535)
Heure inhabituelle : Activité en dehors des heures normales
Volume élevé : 5-20x le volume normal
Protocole inhabituel : Protocoles non standards
Scan de ports : Tentative d'exploration réseau
8. Processus de Génération Complète
def generate_network_data(self, num_devices=20, hours=24, anomaly_percentage=5):
Étapes :

Créer 20 profils d'appareils différents
Générer des données toutes les 10 minutes pendant 24h
Pour chaque appareil et chaque moment :
Décider s'il est actif (basé sur son profil)
Choisir port/protocole/volume selon ses habitudes
Injecter des anomalies selon le pourcentage
Calculer des statistiques (moyennes, écarts-types)
Retourner un DataFrame avec toutes les données
9. Données de Sortie
Le système génère environ 1400-1600 échantillons avec :

Horodatage précis
Identifiants d'appareils
Adresses IP/MAC
Ports et protocoles utilisés
Volumes de données
Classification normale/anormale
Statistiques par appareil
Ce Que Vous Pouvez Dire en Présentation
"Pour créer cette simulation, j'ai analysé les patterns typiques d'un réseau d'entreprise. J'ai programmé 6 types d'appareils avec leurs comportements réels : les ordinateurs sont actifs en journée, les serveurs 24/7, les imprimantes seulement pendant les heures de bureau. Chaque type a ses ports préférés, ses volumes de données habituels. Le système génère des adresses IP et MAC réalistes, et injecte des anomalies représentatives de vraies cyberattaques."

Points techniques à retenir :

Basé sur de vraies observations de réseaux d'entreprise
Algorithmes probabilistes pour le réalisme
Patterns temporels fidèles à la réalité
Anomalies représentatives de vraies menaces
Cette simulation est suffisamment réaliste pour démontrer les capacités du système sur de vraies données d'entreprise.


Pour les graphiques, j'ai utilisé :

Plotly : Bibliothèque de visualisation interactive
make_subplots() : Pour créer des graphiques à plusieurs panneaux
go.Scatter() : Pour les courbes temporelles
go.Bar() : Pour les graphiques en barres
px.bar(), px.pie() : Pour les graphiques simples
st.plotly_chart() : Pour afficher dans Streamlit

Intégration des Graphiques
J'ai utilisé Plotly pour créer tous les graphiques interactifs :

Technologies utilisées :

plotly.graph_objects (go.Scatter, go.Bar) pour les graphiques personnalisés
plotly.express (px.bar, px.pie) pour les graphiques rapides
plotly.subplots.make_subplots pour combiner plusieurs graphiques
st.plotly_chart() pour l'affichage dans Streamlit
Exemple concret :

# Graphique temporel avec anomalies
fig = make_subplots(rows=2, cols=1)
fig.add_trace(go.Scatter(x=dates, y=volumes, name='Volume'))
fig.add_trace(go.Bar(x=dates, y=connexions, name='Connexions'))
st.plotly_chart(fig, use_container_width=True)
