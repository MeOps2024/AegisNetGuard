Documentation Développeur AEGISLAN
Guide complet pour présenter et utiliser le système

Vue d'ensemble du système
AEGISLAN est un système de détection d'anomalies réseau utilisant l'intelligence artificielle. Le système analyse le comportement des appareils sur un réseau pour identifier des activités suspectes.

Comment présenter l'application

1. Introduction (ce que vous dites au client)
"AEGISLAN est un système de cybersécurité avancé que j'ai développé. Il utilise l'intelligence artificielle pour surveiller votre réseau en temps réel et détecter automatiquement les comportements suspects qui pourraient indiquer une cyberattaque ou une violation de sécurité."

2. Avantages clés à mettre en avant

    Détection automatique : Pas besoin de surveillance humaine 24/7

    Apprentissage adaptatif : S'améliore avec le temps

    Interface intuitive : Accessible aux non-techniques

    Alertes intelligentes : Classées par niveau de criticité

    Tableau de bord complet : Vue d'ensemble en temps réel

Guide d'utilisation étape par étape

Étape 1 : Génération des données

Ce que vous faites :

    Dans le panneau gauche, ajustez les paramètres :

        Nombre d'appareils : 20 (bon équilibre pour la démo)

        Heures de données : 24 (une journée complète)

        Taux d'anomalies : 10% (assez pour voir des résultats)

    Cliquez sur "Générer Nouvelles Données"

Ce que vous expliquez :
"Le système simule un réseau d'entreprise réaliste avec différents types d'appareils : ordinateurs, serveurs, imprimantes, téléphones. Chaque appareil a son propre comportement normal. J'ai configuré une simulation de 24 heures avec 20 appareils pour la démonstration."

Étape 2 : Entraînement du modèle

Ce que vous faites :

    Laissez "Contamination" à 0.1 (valeur optimale)

    Cliquez sur "Entraîner le Modèle"

    Montrez la barre de progression et les messages

Ce que vous expliquez :
"Maintenant, l'intelligence artificielle va apprendre les comportements normaux de chaque appareil. L'algorithme utilisé s'appelle Isolation Forest - c'est une technique avancée qui peut détecter les anomalies sans avoir besoin d'exemples d'attaques préalables. Le processus prend quelques secondes car le système analyse [X] échantillons de données."

Étape 3 : Détection des anomalies

Ce que vous faites :

    Cliquez sur "Détecter les Anomalies"

    Montrez la barre de progression

    Pointez vers les résultats affichés

Ce que vous expliquez :
"Le modèle entraîné examine maintenant toutes les données pour identifier les comportements anormaux. Regardez - il a détecté [X] anomalies classées par niveau de criticité."

Comment interpréter les résultats

Section "État du système"

Montrez :

    Statut réseau : "Actif"

    Modèle IA : "Opérationnel"

    Alertes critiques : Nombre affiché

    Appareils surveillés : Nombre total

Expliquez :
"Ce tableau de bord vous donne l'état de santé global de votre réseau en un coup d'œil. Vous voyez immédiatement s'il y a des problèmes critiques qui nécessitent une attention immédiate."

Section "Métriques réseau"

Montrez :

    Total connexions, anomalies détectées, appareils actifs, volume total, ports utilisés

Expliquez :
"Ces métriques vous donnent une vue quantitative de l'activité réseau. Un taux d'anomalies supérieur à 5% peut indiquer un problème de sécurité."

Section "Alertes en temps réel"

Montrez :

    Alertes par couleur (Rouge = Critique, Orange = Élevé, etc.)

    Détails de chaque alerte

Expliquez :
"Le système classe automatiquement les anomalies par niveau de danger. Les alertes critiques nécessitent une action immédiate, tandis que les alertes faibles sont juste informatives."

Démonstration des graphiques

Graphique "Évolution du trafic"

Montrez :

    Courbe du volume de données

    Barres des connexions

    Points d'anomalies

Expliquez :
"Ce graphique montre l'évolution temporelle du trafic. Les pics anormaux ou les activités en dehors des heures ouvrables peuvent indiquer des problèmes. Les points orange marquent les anomalies détectées."

Graphique "Activité par appareil"

Montrez :

    Barres colorées par type d'appareil

    Top 10 des plus actifs

Expliquez :
"Ici, vous voyez quels appareils consomment le plus de bande passante. Si un appareil habituellement silencieux (comme une imprimante) apparaît soudainement en haut de cette liste, c'est suspect."

Graphique "Analyse des ports"

Montrez :

    Barres bleues (normales) vs oranges (avec anomalies)

Expliquez :
"Les ports sont comme des portes d'entrée sur les appareils. Les barres oranges indiquent des ports où des anomalies ont été détectées - cela peut signaler des tentatives d'intrusion."

Questions / Réponses courantes

Q : Comment savez-vous que c'est précis ?
R : Le système affiche ses propres métriques de performance. Dans notre test, il a correctement identifié X% des vraies anomalies avec très peu de faux positifs. De plus, chaque alerte indique un niveau de confiance.

Q : Que faire en cas d'alerte critique ?
R : Le système vous donne toutes les informations : quel appareil, quelle activité, quand. Vous pouvez ensuite isoler l'appareil suspect et investiguer plus en détail. Dans un environnement réel, cela se connecterait à votre infrastructure de sécurité existante.

Q : Ça marche avec nos vrais équipements ?
R : Absolument. Ce que vous voyez utilise des données simulées pour la démonstration, mais le système peut s'adapter à n'importe quel environnement réseau réel. Il suffit de le connecter à vos sources de données réseau existantes.

Détails techniques (si demandé)

Architecture

    Frontend : Streamlit (Python) pour l'interface web

    Backend : Scikit-learn pour l'IA, Pandas pour les données

    Algorithme : Isolation Forest (apprentissage non supervisé)

    Visualisation : Plotly pour les graphiques interactifs

Avantages techniques

    Scalable : Peut gérer des milliers d'appareils

    Modulaire : Facile à étendre et personnaliser

    Standard : Utilise des technologies éprouvées

    Open Source : Pas de dépendance à des solutions propriétaires

Points de vente clés

    ROI immédiat : Détecte les menaces avant qu'elles causent des dégâts

    Coût réduit : Remplace la surveillance manuelle 24/7

    Expertise intégrée : L'IA incorpore les meilleures pratiques de cybersécurité

    Évolutif : S'adapte à la croissance de l'entreprise

    Compliance : Aide à respecter les réglementations de sécurité

Scénarios d'usage

Détection d'intrusion
Si un attaquant compromet un poste de travail, il va probablement commencer à scanner le réseau pour trouver d'autres cibles. AEGISLAN détectera immédiatement ce comportement anormal.

Malware
Un malware qui exfiltre des données créera un pic de trafic inhabituel. Le système l'identifiera même si c'est la première fois qu'il voit ce type d'attaque.

Utilisateur compromis
Si les identifiants d'un employé sont volés et utilisés en dehors des heures normales, AEGISLAN alertera sur cette activité suspecte.

Conseils pour une démonstration réussie

    Préparez vos données avant la présentation

    Montrez d'abord les résultats, puis expliquez comment on y arrive

    Utilisez des termes business, pas seulement techniques

    Montrez la valeur, pas juste les fonctionnalités

    Préparez des réponses aux objections courantes

    Terminez par les prochaines étapes concrètes
