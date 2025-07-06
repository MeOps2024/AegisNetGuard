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

Ce qui se passe :
Le système simule un réseau d'entreprise réaliste avec différents types d'appareils : ordinateurs, serveurs, imprimantes, téléphones. Chaque appareil a son propre comportement normal. Une simulation de 24 heures avec 20 appareils permet de générer un trafic varié et crédible pour la démonstration.

Étape 2 : Entraînement du modèle

Ce que vous faites :

    Laissez "Contamination" à 0.1 (valeur optimale)

    Cliquez sur "Entraîner le Modèle"

    Montrez la barre de progression et les messages

Ce qui se passe :
L'intelligence artificielle apprend les comportements normaux de chaque appareil. L'algorithme utilisé s'appelle Isolation Forest – une méthode avancée qui détecte les anomalies sans avoir besoin d'exemples d'attaques. Le système analyse les données générées pour établir une base de référence.

Étape 3 : Détection des anomalies

Ce que vous faites :

    Cliquez sur "Détecter les Anomalies"

    Montrez la barre de progression

    Pointez vers les résultats affichés

Ce qui se passe :
Le modèle entraîné examine toutes les données pour identifier les comportements inhabituels. Les anomalies détectées sont affichées, classées par niveau de criticité (critique, élevé, moyen, faible).

Comment interpréter les résultats

Section "État du système"

Montrez :

    Statut réseau : "Actif"

    Modèle IA : "Opérationnel"

    Alertes critiques : Nombre affiché

    Appareils surveillés : Nombre total

Ce qui se passe :
Le tableau de bord affiche l'état global du système. Il permet de vérifier rapidement si le modèle est actif et s’il y a des problèmes nécessitant une attention immédiate.

Section "Métriques réseau"

Montrez :

    Total connexions, anomalies détectées, appareils actifs, volume total, ports utilisés

Ce qui se passe :
Ces métriques donnent une vue d’ensemble de l’activité réseau. Un nombre inhabituel d’anomalies ou une utilisation excessive de la bande passante peut révéler un problème de sécurité.

Section "Alertes en temps réel"

Montrez :

    Alertes par couleur (Rouge = Critique, Orange = Élevé, etc.)

    Détails de chaque alerte

Ce qui se passe :
Les anomalies sont automatiquement catégorisées selon leur gravité. Les alertes critiques doivent être traitées rapidement, tandis que les alertes faibles sont à surveiller.

Démonstration des graphiques

Graphique "Évolution du trafic"

Montrez :

    Courbe du volume de données

    Barres des connexions

    Points d'anomalies

Ce qui se passe :
Ce graphique permet de visualiser les volumes de données au fil du temps. Les pics soudains ou les activités en dehors des heures habituelles sont des signes potentiels d’attaque. Les points d’anomalies y sont visibles.

Graphique "Activité par appareil"

Montrez :

    Barres colorées par type d'appareil

    Top 10 des plus actifs

Ce qui se passe :
On voit ici quels appareils génèrent le plus d’activité. Si un appareil peu actif (comme une imprimante) devient soudainement très actif, cela peut signaler une anomalie.

Graphique "Analyse des ports"

Montrez :

    Barres bleues (normales) vs oranges (avec anomalies)

Ce qui se passe :
Le graphique montre les ports réseau les plus utilisés. Des ports peu communs ou suspects peuvent indiquer une tentative d’accès non autorisé.

Questions / Réponses courantes

Q : Comment savez-vous que c'est précis ?
R : Le système affiche ses propres métriques de performance. Dans notre test, il a correctement identifié X% des vraies anomalies avec très peu de faux positifs. De plus, chaque alerte indique un niveau de confiance.

Q : Que faire en cas d'alerte critique ?
R : Le système vous donne toutes les informations : quel appareil, quelle activité, quand. Vous pouvez ensuite isoler l'appareil suspect et investiguer plus en détail. Dans un environnement réel, cela se connecterait à votre infrastructure de sécurité existante.

Q : Ça marche avec nos vrais équipements ?
R : Absolument. Ce que vous voyez utilise des données simulées pour la démonstration, mais le système peut s'adapter à n'importe quel environnement réseau réel. Il suffit de le connecter à vos sources de données réseau existantes.

Détails techniques (si demandé)

Architecture :

    Frontend : Streamlit (Python) pour l'interface web

    Backend : Scikit-learn pour l'IA, Pandas pour les données

    Algorithme : Isolation Forest (apprentissage non supervisé)

    Visualisation : Plotly pour les graphiques interactifs

Avantages techniques :

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

Détection d'intrusion :
Si un attaquant compromet un poste de travail, il va probablement commencer à scanner le réseau pour trouver d'autres cibles. AEGISLAN détectera immédiatement ce comportement anormal.

Malware :
Un malware qui exfiltre des données créera un pic de trafic inhabituel. Le système l'identifiera même si c'est la première fois qu'il voit ce type d'attaque.

Utilisateur compromis :
Si les identifiants d'un employé sont volés et utilisés en dehors des heures normales, AEGISLAN alertera sur cette activité suspecte.

Conseils pour une démonstration réussie

    Préparez vos données avant la présentation

    Montrez d'abord les résultats, puis expliquez comment on y arrive

    Utilisez des termes business, pas seulement techniques

    Montrez la valeur, pas juste les fonctionnalités

    Préparez des réponses aux objections courantes

    Terminez par les prochaines étapes concrètes
