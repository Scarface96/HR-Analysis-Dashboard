"""Which factors still matter once the others are held constant?

Single-factor charts can mislead: young people are more often junior, single and
low-paid, so each of those looks risky on its own. A logistic regression estimates
each factor's effect with the others held fixed, reported as odds ratios with 95%
confidence intervals.
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

# (column in the design matrix, readable label, how it's built)
FEATURES = {
    "overtime": ("Works overtime", lambda d: (d["Over Time"] == "Yes").astype(float)),
    "travel_frequently": ("Travels frequently (vs rarely or never)", lambda d: (d["Business Travel"] == "Travel_Frequently").astype(float)),
    "single": ("Single (vs married or divorced)", lambda d: (d["Marital Status"] == "Single").astype(float)),
    "no_stock": ("No stock options", lambda d: (d["Stock Option Level"] == 0).astype(float)),
    "job_level_1": ("Entry-level role (job level 1)", lambda d: (d["Job Level"] == 1).astype(float)),
    "sales": ("Works in Sales (vs R&D)", lambda d: (d["Department"] == "Sales").astype(float)),
    "low_job_sat": ("Low job satisfaction (1 of 4)", lambda d: (d["Job Satisfaction"] == 1).astype(float)),
    "low_env_sat": ("Low environment satisfaction (1 of 4)", lambda d: (d["Environment Satisfaction"] == 1).astype(float)),
    "poor_balance": ("Poor work-life balance (1 of 4)", lambda d: (d["Work Life Balance"] == 1).astype(float)),
    "age_10": ("Each 10 years older", lambda d: d["Age"] / 10),
    "income_1k": ("Each extra $1,000 monthly income", lambda d: d["Monthly Income"] / 1000),
    "distance_10": ("Each extra 10 km from home", lambda d: d["Distance From Home"] / 10),
    "companies": ("Each previous employer", lambda d: d["Num Companies Worked"].astype(float)),
    "since_promo": ("Each year since last promotion", lambda d: d["Years Since Last Promotion"].astype(float)),
}


def design(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({k: f(df) for k, (_, f) in FEATURES.items()}, index=df.index)


def odds_ratios(df: pd.DataFrame) -> pd.DataFrame:
    X = sm.add_constant(design(df))
    fit = sm.Logit(df["left"], X).fit(disp=False)
    ci = fit.conf_int()
    t = pd.DataFrame({
        "feature": [k for k in FEATURES],
        "label": [FEATURES[k][0] for k in FEATURES],
        "odds_ratio": np.exp(fit.params[list(FEATURES)]).values,
        "low": np.exp(ci.loc[list(FEATURES), 0]).values,
        "high": np.exp(ci.loc[list(FEATURES), 1]).values,
        "p_value": fit.pvalues[list(FEATURES)].values,
    })
    t["significant"] = (t["low"] > 1) | (t["high"] < 1)
    t.attrs["pseudo_r2"] = float(fit.prsquared)
    return t.sort_values("odds_ratio").reset_index(drop=True)


def cv_auc(df: pd.DataFrame, folds: int = 5) -> float:
    """How well these factors rank who will leave, on employees the model hasn't seen."""
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
    cv = StratifiedKFold(folds, shuffle=True, random_state=42)
    return float(cross_val_score(model, design(df), df["left"], cv=cv, scoring="roc_auc").mean())
