# Guide d'Utilisation AEGISLAN
## Système de Détection d'Anomalies Réseau

### 📋 Table des Matières
1. [Qu'est-ce qu'AEGISLAN ?](#quest-ce-quaegislan)
2. [Comment ça fonctionne ?](#comment-ça-fonctionne)
3. [Guide d'utilisation pas à pas](#guide-dutilisation-pas-à-pas)
4. [Comprendre les résultats](#comprendre-les-résultats)
5. [Questions fréquentes](#questions-fréquentes)

---

## Qu'est-ce qu'AEGISLAN ?

AEGISLAN est un système intelligent qui surveille votre réseau informatique pour détecter des comportements anormaux. C'est comme un système de sécurité pour votre réseau qui apprend ce qui est normal et vous alerte quand quelque chose de suspect se produit.

### À quoi ça sert ?
- **Détecter les intrusions** : Repérer si quelqu'un accède à votre réseau sans autorisation
- **Surveiller les appareils** : Vérifier que vos ordinateurs, imprimantes, téléphones ne font rien d'anormal
- **Prévenir les attaques** : Alerter avant qu'un problème de sécurité ne devienne grave
- **Analyser le trafic** : Comprendre comment votre réseau est utilisé

### Pourquoi c'est important ?
Dans une entreprise, si un appareil commence soudainement à :
- Se connecter à des heures inhabituelles
- Utiliser des ports réseau jamais utilisés avant
- Transférer beaucoup plus de données que d'habitude
- Communiquer avec des services inconnus

C'est peut-être le signe d'une cyberattaque ou d'un problème de sécurité.

---

## Comment ça fonctionne ?

### 1. Les Données Réseau
Le système observe tout ce qui se passe sur votre réseau :
- **Qui** se connecte (adresses IP, MAC des appareils)
- **Quand** ils se connectent (horodatage)
- **Comment** ils se connectent (ports, protocoles)
- **Combien** de données ils échangent

### 2. L'Intelligence Artificielle
AEGISLAN utilise un algorithme appelé "Isolation Forest" qui :
- **Apprend** automatiquement les habitudes normales de chaque appareil
- **Compare** chaque nouvelle activité à ce qui est habituel
- **Détecte** les comportements qui sortent de l'ordinaire
- **Classe** les anomalies par niveau de dangerosité

### 3. Les Alertes
Quand quelque chose d'anormal est détecté, le système :
- **Alerte** immédiatement avec un niveau de criticité
- **Explique** quel type d'anomalie a été trouvé
- **Localise** sur quel appareil
- **Fournit** des détails techniques pour l'investigation

---

## Guide d'utilisation pas à pas

### Étape 1 : Accès au système
1. Ouvrez votre navigateur web
2. Allez à l'adresse de votre installation AEGISLAN
3. Vous verrez le tableau de bord principal

### Étape 2 : Génération des données (pour la démonstration)
**Dans le panneau de gauche "Simulation des Données" :**

1. **Nombre d'appareils** : Choisissez combien d'appareils simuler (5-50)
   - 5-10 : Petit réseau (bureau, domicile)
   - 20-30 : Réseau moyen (PME)
   - 40-50 : Grand réseau (entreprise)

2. **Heures de données** : Période à analyser (1-72 heures)
   - 1-6 heures : Analyse rapide
   - 24 heures : Journée complète
   - 72 heures : Analyse sur 3 jours

3. **Taux d'anomalies** : Pourcentage d'activités suspectes (1-20%)
   - 1-5% : Réseau très sain
   - 5-10% : Réseau normal avec quelques incidents
   - 10-20% : Réseau avec beaucoup d'activité suspecte

4. **Cliquez sur "Générer Nouvelles Données"**

### Étape 3 : Entraînement du modèle IA
**Dans le panneau "Entraînement du Modèle" :**

1. **Contamination** : Ajustez le curseur (0.01-0.3)
   - 0.01-0.05 : Très sensible (détecte plus d'anomalies)
   - 0.1 : Équilibré (recommandé)
   - 0.2-0.3 : Moins sensible (moins d'alertes)

2. **Cliquez sur "Entraîner le Modèle"**
3. Attendez que l'IA apprenne les comportements normaux

### Étape 4 : Détection des anomalies
1. **Cliquez sur "Détecter les Anomalies"**
2. Le système analyse toutes les données et identifie les comportements suspects
3. Les résultats apparaissent dans le tableau de bord

### Étape 5 : Analyse des résultats
Le tableau de bord vous montre :

**État du Système :**
- Statut réseau (actif/inactif)
- État du modèle IA (opérationnel/non entraîné)
- Nombre d'alertes critiques
- Nombre d'appareils surveillés

**Métriques Réseau :**
- Total des connexions
- Nombre d'anomalies détectées
- Appareils actifs
- Volume de données
- Ports utilisés

---

## Comprendre les résultats

### Niveaux de Criticité des Alertes

**🔴 Critique** : Danger immédiat
- Action requise immédiatement
- Possible attaque en cours
- Exemple : Transfert de données énorme la nuit

**🟠 Élevé** : Attention nécessaire
- À investiguer rapidement
- Comportement très inhabituel
- Exemple : Utilisation de ports jamais vus

**🟡 Moyen** : Surveillance
- Comportement suspect mais pas urgent
- À vérifier quand possible
- Exemple : Activité légèrement inhabituelle

**🟢 Faible** : Information
- Légère déviation de la normale
- Surveillance passive
- Exemple : Petit pic de trafic

### Types d'Anomalies Détectées

1. **Port inhabituel** : L'appareil utilise un port jamais utilisé avant
2. **Heure inhabituelle** : Activité en dehors des heures normales
3. **Volume élevé** : Transfert de données beaucoup plus important que d'habitude
4. **Protocole inhabituel** : Utilisation d'un protocole réseau inhabituel
5. **Scan de ports** : Tentative d'exploration des ports ouverts

### Graphiques et Visualisations

**Évolution du Trafic :**
- Montre l'activité réseau dans le temps
- Les pics peuvent indiquer des problèmes
- Les anomalies sont marquées spécialement

**Activité par Appareil :**
- Classement des appareils les plus actifs
- Permet d'identifier les gros consommateurs
- Aide à repérer les appareils suspects

**Analyse des Ports :**
- Ports les plus utilisés
- Ports avec anomalies en orange
- Ports normaux en bleu

---

## Questions fréquentes

### Q : Que faire quand une alerte critique apparaît ?
**R :** 
1. Notez l'appareil concerné et l'heure
2. Vérifiez si c'est une activité autorisée
3. Si c'est suspect, déconnectez l'appareil du réseau
4. Contactez votre service informatique ou sécurité

### Q : Combien de temps faut-il pour entraîner le modèle ?
**R :** 
- Quelques secondes à quelques minutes selon la quantité de données
- Plus vous avez de données, plus le modèle sera précis
- Recommandé : au moins 24 heures de données

### Q : Le système peut-il se tromper ?
**R :** 
- Oui, comme tout système intelligent, il peut y avoir des faux positifs
- C'est pourquoi il y a des niveaux de criticité
- Avec le temps et l'ajustement, la précision s'améliore

### Q : Faut-il être un expert en informatique pour l'utiliser ?
**R :** 
- Non, l'interface est conçue pour être simple
- Les alertes sont expliquées en langage clair
- Pour les actions correctives, consultez votre service IT

### Q : À quelle fréquence surveiller le système ?
**R :** 
- Vérifiez les alertes critiques immédiatement
- Consultez le tableau de bord 2-3 fois par jour
- Analysez les tendances une fois par semaine

### Q : Comment améliorer la précision du système ?
**R :** 
- Alimentez-le avec plus de données historiques
- Ajustez le niveau de contamination selon vos besoins
- Validez les alertes pour affiner le modèle

---

## Support et Assistance

Si vous avez des questions ou des problèmes :
1. Consultez d'abord ce guide
2. Vérifiez les logs dans l'onglet "Analyse Détaillée"
3. Contactez votre administrateur système
4. Documentez les anomalies pour améliorer le système

**Rappel de Sécurité :** En cas d'alerte critique, mieux vaut pécher par excès de prudence et investiguer immédiatement.