# Note de recommandation — Dérive `pyrenex_risk_v2`

**Pour :** Sophie Léger (Lead Data, Pyrenex)
**De :** FastIA — Franck & Julien Clavier
**Date :** 2026-09-08
**Périmètre analysé :** 3 mois de production (2026-03-02 → 2026-05-24), 3000 dossiers, comparés au jeu de référence du modèle (`data/reference_set.csv`).

## Constat (chiffré)

Le modèle `pyrenex_risk_v2` continue de fonctionner, mais **deux signaux concrets méritent une action** :

**1. Le profil des emprunteurs a changé depuis la mise en référence du modèle.**
- Le taux d'intérêt moyen des dossiers est passé de 12.6 % à 15.5 %.
- La part de bons profils (grade B) a reculé de 30.5 % à 25.5 %, au profit de profils plus risqués (grades D/E, de 21.4 % à 27.1 % cumulés).
- Le taux d'utilisation du crédit renouvelable moyen est passé de 50.6 % à 59.0 %.
- Ces trois évolutions vont dans le même sens : la clientèle qui arrive aujourd'hui est **structurellement plus risquée** que celle sur laquelle le modèle a été calé. Vérification statistique à l'appui (tests PSI/KS/Chi², détail dans `drift_summary.md`) : ces écarts ne sont pas du bruit, ils sont réels.
- En comparaison, le taux réel de défaut observé bouge peu (17.5 % → 19.1 %) : la situation ne s'est pas encore franchement dégradée sur le terrain, mais les entrées du modèle, elles, ont bougé.

**2. Le modèle sur-estime le risque, et de plus en plus.**
- Sur l'ensemble des 3 derniers mois, quand le modèle annonce « 50 % de risque de défaut », le taux réel de défaut observé n'est que d'environ 20 %. Le modèle **exagère systématiquement le risque annoncé**, quel que soit le niveau de score.
- Cet écart entre le risque annoncé et le risque réel **s'est creusé sur la période** : il a augmenté d'environ 30 % entre le début et la fin des 3 mois (mesure ECE : 0.240 → 0.315 — plus ce chiffre est bas, mieux le modèle est calé). Le taux réel de défaut, lui, est resté stable entre ces deux périodes (20.2 % puis 20.1 %) : ce n'est donc pas la réalité terrain qui bouge, c'est bien la fiabilité des probabilités du modèle.

**Point rassurant :** le modèle sait toujours **classer correctement** les bons et mauvais dossiers les uns par rapport aux autres (indicateur AUC stable à ~0.74 sur toute la période, sans dégradation ni rupture). Le problème n'est donc pas que le modèle « se trompe de client », mais qu'il **communique un niveau de risque exagéré**.

## Diagnostic

Le croisement de ces trois observations (profils qui dérivent, capacité de tri intacte, fiabilité des probabilités qui se dégrade) correspond à un cas connu et documenté : un **changement du profil de la clientèle entrante** (« data drift »), sans remise en cause de la logique de risque du modèle. Concrètement : le modèle sait toujours reconnaître qu'un profil est plus risqué qu'un autre, mais comme les profils qui arrivent aujourd'hui sont globalement différents (plus risqués) de ceux sur lesquels il a été calibré, ses estimations de probabilité ne sont plus justes.

Rien dans les données n'indique un problème plus profond (pas de rupture brutale, pas de baisse du pouvoir de discrimination du modèle) : l'hypothèse d'un changement de comportement plus fondamental des emprunteurs (« concept drift ») n'est pas retenue à ce stade.

## Recommandation

**Recalibrer le modèle sur des données récentes**, sans réentraînement complet ni remise en cause du modèle actuel.

Pourquoi ce choix plutôt qu'un réentraînement complet, plus lourd :
- Le modèle **discrimine toujours correctement** les profils à risque — un réentraînement complet serait disproportionné par rapport au problème observé.
- Un réentraînement complet nécessite le retour de tous les vrais résultats des prêts (plusieurs mois de délai en crédit) et remet en jeu tout l'historique de validation du modèle.
- Un simple recalage des probabilités sur les 3 derniers mois de données peut corriger la sur-estimation du risque à moindre coût, en gardant la même logique de scoring.

Pourquoi ce n'est pas non plus un simple « on surveille » :
- L'écart entre risque annoncé et risque réel **continue de se creuser** (pas de stabilisation observée sur la période) : sans action, l'écart va vraisemblablement continuer à grandir.
- Cette sur-estimation impacte directement les décisions d'octroi et de tarification qui s'appuient sur le niveau de risque annoncé par le modèle.

## Coût estimé

- **Temps :** recalage technique + validation, de l'ordre de quelques jours à 1-2 semaines (hors délais de validation métier/gouvernance).
- **Risque prod :** faible si le déploiement se fait progressivement (voir fenêtre d'intervention ci-dessous) ; le modèle actuel reste en place en parallèle jusqu'à validation du recalage.
- **Fenêtre d'intervention proposée :** déployer le modèle recalé sur un échantillon contrôlé du trafic (10-20 %) avant généralisation, afin de vérifier sur des dossiers non utilisés pour le recalage que la fiabilité des probabilités et la capacité de tri sont bien meilleures.
- **Ce qui manquerait pour une certitude totale** (à documenter dans le suivi) : quelques semaines supplémentaires de recul pour confirmer que la dégradation observée est bien une tendance durable, et le résultat du test en parallèle avant généralisation complète.

## Décision suggérée

> Le modèle reste fiable pour trier les dossiers, mais son estimation du niveau de risque devient de moins en moins juste face à une clientèle qui évolue vers des profils plus risqués : nous recommandons un **recalage du modèle sur données récentes, à déployer d'abord sur un échantillon test**, sans réentraînement complet ni urgence de blocage de la production actuelle.
