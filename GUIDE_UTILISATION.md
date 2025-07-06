Guide d'Utilisation AEGISLAN
Système de Détection d'Anomalies Réseau

Table des Matières

    Qu'est-ce qu'AEGISLAN ?

    Comment ça fonctionne ?

    Guide d'utilisation pas à pas

    Comprendre les résultats

    Questions fréquentes

Qu'est-ce qu'AEGISLAN ?

AEGISLAN est un système intelligent qui surveille votre réseau informatique pour détecter des comportements anormaux. C'est comme un système de sécurité pour votre réseau qui apprend ce qui est normal et vous alerte quand quelque chose de suspect se produit.

À quoi ça sert ?

    Détecter les intrusions : repérer si quelqu'un accède à votre réseau sans autorisation

    Surveiller les appareils : vérifier que vos ordinateurs, imprimantes, téléphones ne font rien d'anormal

    Prévenir les attaques : alerter avant qu'un problème de sécurité ne devienne grave

    Analyser le trafic : comprendre comment votre réseau est utilisé

Pourquoi c'est important ?
Dans une entreprise, si un appareil commence soudainement à :

    Se connecter à des heures inhabituelles

    Utiliser des ports réseau jamais utilisés auparavant

    Transférer beaucoup plus de données que d'habitude

    Communiquer avec des services inconnus

C'est peut-être le signe d'une cyberattaque ou d'un problème de sécurité.

Comment ça fonctionne ?

1. Les Données Réseau
Le système observe tout ce qui se passe sur votre réseau :

    Qui se connecte (adresses IP, MAC des appareils)

    Quand ils se connectent (horodatage)

    Comment ils se connectent (ports, protocoles)

    Combien de données ils échangent

2. L'Intelligence Artificielle
AEGISLAN utilise un algorithme appelé "Isolation Forest" qui :

    Apprend automatiquement les habitudes normales de chaque appareil

    Compare chaque nouvelle activité à ce qui est habituel

    Détecte les comportements qui sortent de l'ordinaire

    Classe les anomalies par niveau de dangerosité

3. Les Alertes
Quand quelque chose d'anormal est détecté, le système :

    Alerte immédiatement avec un niveau de criticité

    Explique quel type d'anomalie a été trouvé

    Localise sur quel appareil

    Fournit des détails techniques pour l'investigation

Guide d'utilisation pas à pas

Étape 1 : Accès au système

    Ouvrez votre navigateur web

    Allez à l'adresse de votre installation AEGISLAN

    Vous verrez le tableau de bord principal

Étape 2 : Génération des données (pour la démonstration)
Dans le panneau de gauche "Simulation des Données" :

    Nombre d'appareils : choisissez combien d'appareils simuler (5-50)

        5-10 : petit réseau (bureau, domicile)

        20-30 : réseau moyen (PME)

        40-50 : grand réseau (entreprise)

    Heures de données : période à analyser (1-72 heures)

        1-6 heures : analyse rapide

        24 heures : journée complète

        72 heures : analyse sur 3 jours

    Taux d'anomalies : pourcentage d'activités suspectes (1-20 %)

        1-5 % : réseau très sain

        5-10 % : réseau normal avec quelques incidents

        10-20 % : réseau avec beaucoup d'activité suspecte

    Cliquez sur "Générer Nouvelles Données"

Étape 3 : Entraînement du modèle IA
Dans le panneau "Entraînement du Modèle" :

    Contamination : ajustez le curseur (0.01-0.3)

        0.01-0.05 : très sensible (détecte plus d'anomalies)

        0.1 : équilibré (recommandé)

        0.2-0.3 : moins sensible (moins d'alertes)

    Cliquez sur "Entraîner le Modèle"

    Attendez que l'IA apprenne les comportements normaux

Étape 4 : Détection des anomalies

    Cliquez sur "Détecter les Anomalies"

    Le système analyse toutes les données et identifie les comportements suspects

    Les résultats apparaissent dans le tableau de bord

Étape 5 : Analyse des résultats
Le tableau de bord vous montre :

État du Système :

    Statut réseau (actif / inactif)

    État du modèle IA (opérationnel / non entraîné)

    Nombre d'alertes critiques

    Nombre d'appareils surveillés

Métriques Réseau :

    Total des connexions

    Nombre d'anomalies détectées

    Appareils actifs

    Volume de données

    Ports utilisés

Comprendre les résultats

Niveaux de Criticité des Alertes

Critique : Danger immédiat

    Action requise immédiatement

    Possible attaque en cours

    Exemple : transfert de données énorme la nuit

Élevé : Attention nécessaire

    À investiguer rapidement

    Comportement très inhabituel

    Exemple : utilisation de ports jamais vus

Moyen : Surveillance

    Comportement suspect mais pas urgent

    À vérifier quand possible

    Exemple : activité légèrement inhabituelle

Faible : Information

    Légère déviation de la normale

    Surveillance passive

    Exemple : petit pic de trafic

Types d'Anomalies Détectées

    Port inhabituel : l'appareil utilise un port jamais utilisé avant

    Heure inhabituelle : activité en dehors des heures normales

    Volume élevé : transfert de données beaucoup plus important que d'habitude

    Protocole inhabituel : utilisation d'un protocole réseau inhabituel

    Scan de ports : tentative d'exploration des ports ouverts

Graphiques et Visualisations

Évolution du Trafic :

    Montre l'activité réseau dans le temps

    Les pics peuvent indiquer des problèmes

    Les anomalies sont marquées spécialement

Activité par Appareil :

    Classement des appareils les plus actifs

    Permet d'identifier les gros consommateurs

    Aide à repérer les appareils suspects

Analyse des Ports :

    Ports les plus utilisés

    Ports avec anomalies en orange

    Ports normaux en bleu

Questions fréquentes

Que faire quand une alerte critique apparaît ?

    Notez l'appareil concerné et l'heure

    Vérifiez si c'est une activité autorisée

    Si c'est suspect, déconnectez l'appareil du réseau

    Contactez votre service informatique ou sécurité

Combien de temps faut-il pour entraîner le modèle ?

    Quelques secondes à quelques minutes selon la quantité de données

    Plus vous avez de données, plus le modèle sera précis

    Recommandé : au moins 24 heures de données

Le système peut-il se tromper ?

    Oui, comme tout système intelligent, il peut y avoir des faux positifs

    C'est pourquoi il y a des niveaux de criticité

    Avec le temps et l'ajustement, la précision s'améliore

Faut-il être un expert en informatique pour l'utiliser ?

    Non, l'interface est conçue pour être simple

    Les alertes sont expliquées en langage clair

    Pour les actions correctives, consultez votre service IT

À quelle fréquence surveiller le système ?

    Vérifiez les alertes critiques immédiatement

    Consultez le tableau de bord 2 à 3 fois par jour

    Analysez les tendances une fois par semaine

Comment améliorer la précision du système ?

    Alimentez-le avec plus de données historiques

    Ajustez le niveau de contamination selon vos besoins

    Validez les alertes pour affiner le modèle

Support et Assistance

Si vous avez des questions ou des problèmes :

    Consultez d'abord ce guide

    Vérifiez les logs dans l'onglet "Analyse Détaillée"

    Contactez votre administrateur système

    Documentez les anomalies pour améliorer le système

Rappel de Sécurité :
En cas d'alerte critique, mieux vaut pécher par excès de prudence et investiguer immédiatement.
