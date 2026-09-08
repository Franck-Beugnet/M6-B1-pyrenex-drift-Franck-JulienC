"""Logique de recommandation de remédiation (SQUELETTE À COMPLÉTER).

La remédiation doit être **proportionnée** au diagnostic : réentraîner coûte
cher, on ne le propose que quand ça vaut le coup. Mini-cours :
`02_Data_drift_vs_concept_drift_essentiel.md` (matrice features × AUC).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DriftDiagnosis:
    """Synthèse du diagnostic pour décider de la remédiation."""

    n_features_drift: int  # nb de features en "dérive" (PSI > 0.25)
    auc_stable: bool  # le pouvoir discriminant tient-il ?
    calibration_degraded: bool  # la confiance a-t-elle dérivé ?
    f1_drop: float  # baisse de F1 macro (early → late)


def diagnose_drift_type(d: DriftDiagnosis) -> str:
    """Oriente vers "data drift" / "concept drift" / "mixte".

    ⚠️ Heuristique d'orientation, pas une preuve : elle formalise la matrice
    du mini-cours 02 (features × AUC) pour produire une hypothèse principale.
    Le verdict final se construit en croisant features, AUC, calibration et
    temporalité — et doit énoncer ce qui manquerait pour trancher.
    """
    if d.n_features_drift == 0 and d.auc_stable:
        return "pas de signal significatif"
    if d.n_features_drift > 0 and d.auc_stable:
        return "data drift"
    if d.n_features_drift == 0 and not d.auc_stable:
        return "concept drift"
    return "mixte"


def recommend(d: DriftDiagnosis) -> dict[str, str]:
    """Recommande une action proportionnée au diagnostic.

    Returns:
        dict avec les clés : action / justification / urgence / drift_type.
    """
    drift_type = diagnose_drift_type(d)

    if drift_type == "pas de signal significatif":
        return {
            "drift_type": drift_type,
            "action": "surveiller",
            "urgence": "faible",
            "justification": (
                f"Aucune feature en dérive forte ({d.n_features_drift}) et AUC stable : "
                "pas de signal exploitable, poursuivre la surveillance courante."
            ),
        }

    if drift_type == "data drift":
        if d.calibration_degraded:
            return {
                "drift_type": drift_type,
                "action": "ajuster / recalibrer sur donnees recentes",
                "urgence": "moyenne",
                "justification": (
                    f"{d.n_features_drift} feature(s) en dérive et AUC stable : le pouvoir de tri "
                    "tient, mais la calibration s'est dégradée. Un recalage (recalibration ou "
                    "réentraînement léger sur données récentes) suffit, sans remettre en cause "
                    "le modèle."
                ),
            }
        return {
            "drift_type": drift_type,
            "action": "surveiller de pres",
            "urgence": "faible",
            "justification": (
                f"{d.n_features_drift} feature(s) en dérive mais AUC stable et calibration saine : "
                "le modèle reste fiable, renforcer la surveillance des features concernées."
            ),
        }

    if drift_type == "concept drift":
        return {
            "drift_type": drift_type,
            "action": "reentrainer en urgence + investiguer la cause",
            "urgence": "haute",
            "justification": (
                f"Features stables mais AUC dégradée (baisse F1 = {d.f1_drop:.2f}) : la relation "
                "features → cible a changé, un simple recalage ne suffira pas."
            ),
        }

    return {
        "drift_type": drift_type,
        "action": "reentrainer + investiguer en priorite",
        "urgence": "haute",
        "justification": (
            f"{d.n_features_drift} feature(s) en dérive ET AUC dégradée (baisse F1 = {d.f1_drop:.2f}) : "
            "signal mixte, à traiter comme un concept drift potentiel tant que la cause n'est "
            "pas isolée."
        ),
    }
