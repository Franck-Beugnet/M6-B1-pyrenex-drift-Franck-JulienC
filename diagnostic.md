# Diagnostic — Data drift vs concept drift : `pyrenex_risk_v2`

Date : 2026-09-08
Périmètre : 3 mois de production (`prod_3months.csv`, `predictions_log.csv`, 2026-03-02 → 2026-05-24) vs `data/reference_set.csv`.
Analyse complète : `notebooks/M6-B1_template.ipynb`.

## 1. Constat chiffré

### 1.1 Dérive des features (PSI · KS · Chi², détail dans `drift_summary.md`)

La dérive n'est **pas généralisée**, elle est concentrée sur les variables liées au risque de crédit :

| Feature | Type | Calcul | Verdict |
|---|---|---|---|
| `int_rate` (taux d'intérêt) | numérique | PSI = 0.444, KS p ≈ 5·10⁻⁶⁵ | **dérive forte** |
| `grade` (catégorie de risque) | catégorielle | Chi² p ≈ 3.7·10⁻⁷ | **dérive** |
| `revol_util` (utilisation crédit renouvelable) | numérique | PSI = 0.187, KS significatif | à investiguer |
| `annual_inc` | numérique | PSI = 0.067 (KS significatif mais ampleur faible) | stable |
| 9 autres features (`loan_amnt`, `dti`, `installment`, `fico_range_low`, `term`, `emp_length`, `home_ownership`, `verification_status`, `purpose`) | — | PSI < 0.10 et/ou Chi² non significatif | stable |

Le mix `grade` se dégrade de façon cohérente avec la hausse d'`int_rate` : moins de profils B (30.5 % → 25.5 %), plus de D/E (13.9 % → 17.6 % et 7.5 % → 9.5 %). La cible réelle (`loan_status`) reste quasi stable (17.5 % → 19.1 % de défauts), ce n'est pas elle qui explique la dérive.

### 1.2 Pouvoir de tri — AUC (partie 4 du notebook)

- AUC semaines 1-4 : **0.742** — AUC semaines 9-12 : **0.746** — ΔAUC = **+0.004**, très en-dessous du seuil de 0.03 → **AUC stable**.
- La vue hebdomadaire (S1 à S12) confirme : oscillation entre 0.71 et 0.80, sans tendance de fond ni rupture brutale — cohérent avec du bruit d'échantillonnage (~250 dossiers/semaine).

### 1.3 Calibration (partie 3 du notebook)

- Le modèle est **systématiquement sur-confiant** : à toutes les tranches de score, le taux réel observé est inférieur à la probabilité annoncée (ex. proba ≈ 0.5 → taux réel observé ≈ 14–24 %).
- Sur l'ensemble de la période : `proba_default` moyenne = 0.476 pour un taux réel de défaut de 19.1 %.
- La sur-confiance **s'aggrave dans le temps** : ECE = **0.240** (semaines 1-4) → **0.315** (semaines 9-12), alors que le taux réel de défaut reste stable entre les deux fenêtres (20.2 % vs 20.1 %).

## 2. Triangulation (mini-cours 02)

| Axe | Observation |
|---|---|
| Features | Dérivent (2 en dérive forte, 1 à investiguer) |
| AUC | Stable (Δ = +0.004) |
| Calibration | Dégradée, tendance progressive (pas de saut) |
| Temporalité | Glissement continu sur 12 semaines, aucune rupture brutale identifiée |

Ce croisement correspond exactement à la case **« features dérivent + AUC stable → data drift plausible »** de la matrice du mini-cours 02, avec en complément un **impact avéré sur la calibration**. Un modèle qui *ordonne toujours correctement* les profils (AUC stable) mais dont les *probabilités deviennent de moins en moins fiables* est la signature typique d'un data drift : les entrées ont bougé (profils plus risqués), la logique de risque du modèle (« taux élevé ⇒ plus de risque ») tient toujours, mais le modèle **extrapole hors de sa zone de calage** d'origine.

Rien n'indique un changement de la relation features → cible (pas de baisse d'AUC, pas de rupture brutale) : l'hypothèse de **concept drift n'est pas retenue** à ce stade.

## 3. Diagnostic retenu

> **Data drift, avec impact avéré sur la calibration.**
> Dérive concentrée sur `int_rate`, `grade` (et `revol_util` en surveillance), AUC stable, calibration en dégradation progressive (ECE +31 % sur la période observée).

## 4. Ce qui manquerait pour trancher avec une certitude totale

- Un historique **post-S12** pour confirmer que la tendance de dégradation de la calibration se poursuit (ou se stabilise) au-delà de la fenêtre observée.
- Une comparaison à une **source externe** (autre segment, autre canal) pour écarter un biais propre à `predictions_log.csv`.
- Un test de **recalibration à blanc** sur un sous-échantillon récent, pour vérifier qu'un simple recalage suffit à corriger la calibration sans qu'un réentraînement complet soit nécessaire.

## 5. Remédiation proportionnée (voir `src/recommendations.py`)

- **Action recommandée :** ajuster / recalibrer le modèle sur données récentes — **pas** de réentraînement complet en urgence (le pouvoir de tri est intact), **pas** de simple surveillance passive non plus (la dégradation de calibration est réelle et continue de s'accentuer).
- **Urgence : moyenne.** À traiter avant que la sur-confiance ne s'aggrave davantage et n'impacte les décisions d'octroi qui s'appuient sur `proba_default`.
- Détail de la décision et du coût estimé : voir `note_recommandation_TEMPLATE.md`.
