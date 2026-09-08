"""Détection de dérive — PSI, KS, Chi² (SQUELETTE À COMPLÉTER).

Trois méthodes complémentaires. Mini-cours : `01_PSI_KS_Chi2_essentiel.md`.
N'inventez pas vos métriques : PSI (formule ci-dessous), KS et Chi² sont dans
scipy.stats.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, ks_2samp

PSI_STABLE = 0.10
PSI_DRIFT = 0.25


def population_stability_index(reference: pd.Series, current: pd.Series, n_bins: int = 10) -> float:
    """PSI entre référence et courant.

    PSI = Σ (p_cur - p_ref) * ln(p_cur / p_ref), bornes des bins = quantiles de
    la référence. ⚠️ pensez au lissage anti-zéro (sinon ln(0) / division par 0).
    """
    eps = 1e-6
    edges = np.unique(np.quantile(reference, np.linspace(0, 1, n_bins + 1)))
    edges[0], edges[-1] = -np.inf, np.inf
    p_ref = np.histogram(reference, edges)[0] / len(reference)
    p_cur = np.histogram(current, edges)[0] / len(current)
    p_ref, p_cur = p_ref + eps, p_cur + eps
    p_ref, p_cur = p_ref / p_ref.sum(), p_cur / p_cur.sum()
    return float(np.sum((p_cur - p_ref) * np.log(p_cur / p_ref)))


def psi_verdict(psi: float) -> str:
    """Traduit un PSI en verdict (stable / suspect / dérive)."""
    if psi < PSI_STABLE:
        return "stable"
    if psi < PSI_DRIFT:
        return "suspect"
    return "dérive"


def ks_pvalue(reference: pd.Series, current: pd.Series) -> float:
    """p-value du test de Kolmogorov-Smirnov (2 échantillons)."""
    return float(ks_2samp(reference, current).pvalue)


def chi2_pvalue(reference: pd.Series, current: pd.Series) -> float:
    """p-value du Chi² sur les fréquences de modalités (aligner les modalités)."""
    categories = sorted(set(reference.dropna().unique()) | set(current.dropna().unique()))
    ref_counts = reference.value_counts().reindex(categories, fill_value=0) + 1
    cur_counts = current.value_counts().reindex(categories, fill_value=0) + 1
    table = np.vstack([ref_counts.to_numpy(), cur_counts.to_numpy()])
    return float(chi2_contingency(table)[1])


def drift_report(
    reference: pd.DataFrame, current: pd.DataFrame,
    numeric_cols: list[str], categorical_cols: list[str],
) -> pd.DataFrame:
    """Tableau de synthèse : feature / type / psi / ks_pvalue / chi2_pvalue / verdict."""
    rows = []
    for col in numeric_cols:
        psi = population_stability_index(reference[col].dropna(), current[col].dropna())
        rows.append(
            {
                "feature": col,
                "type": "numerique",
                "psi": psi,
                "ks_pvalue": ks_pvalue(reference[col].dropna(), current[col].dropna()),
                "chi2_pvalue": np.nan,
                "verdict": psi_verdict(psi),
            }
        )
    for col in categorical_cols:
        p = chi2_pvalue(reference[col], current[col])
        rows.append(
            {
                "feature": col,
                "type": "categorielle",
                "psi": np.nan,
                "ks_pvalue": np.nan,
                "chi2_pvalue": p,
                "verdict": "dérive" if p < 0.05 else "stable",
            }
        )
    report = pd.DataFrame(rows)
    severity = {"dérive": 0, "suspect": 1, "stable": 2}
    report["_ord"] = report["verdict"].map(severity)
    report = report.sort_values(["_ord", "psi"], ascending=[True, False]).drop(columns="_ord")
    return report.reset_index(drop=True)
