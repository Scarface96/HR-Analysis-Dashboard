"""Load and prepare the HR attrition data."""

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "HR Data.xlsx"
CONSTANT = ["Standard Hours", "Employee Count", "Over18", "emp no", "CF_current Employee", "CF_attrition label"]
AGE_ORDER = ["Under 25", "25 - 34", "35 - 44", "45 - 54", "Over 55"]
SATISFACTION = {1: "Low", 2: "Medium", 3: "High", 4: "Very high"}


def load(path: Path = DATA) -> pd.DataFrame:
    df = pd.read_excel(path)
    assert df["Employee Number"].is_unique, "duplicate employees"
    assert set(df["Attrition"]) == {"Yes", "No"}
    df = df.drop(columns=[c for c in CONSTANT if c in df.columns])
    df["left"] = (df["Attrition"] == "Yes").astype(int)
    df["age_band"] = pd.Categorical(df["CF_age band"], AGE_ORDER, ordered=True)
    df["income_band"] = pd.qcut(df["Monthly Income"], 4, labels=["Lowest 25%", "Second 25%", "Third 25%", "Top 25%"])
    df["tenure_band"] = pd.cut(df["Years At Company"], [-1, 0, 2, 5, 10, 50], labels=["Under 1 year", "1–2 years", "3–5 years", "6–10 years", "Over 10 years"])
    df["travel"] = df["Business Travel"].map({"Non-Travel": "Never", "Travel_Rarely": "Rarely", "Travel_Frequently": "Frequently"})
    return df


def wilson(successes, trials, z: float = 1.96):
    """95% Wilson score interval for a proportion."""
    k = np.asarray(successes, dtype=float)
    n = np.asarray(trials, dtype=float)
    p = k / n
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom
    half = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return centre - half, centre + half


def rates(df: pd.DataFrame, by) -> pd.DataFrame:
    g = df.groupby(by, observed=True)["left"].agg(employees="size", left="sum").reset_index()
    g["rate"] = g["left"] / g["employees"]
    g["low"], g["high"] = wilson(g["left"], g["employees"])
    return g


def replacement_cost(df: pd.DataFrame, share_of_salary: float = 0.5) -> float:
    """Rough cost of replacing everyone who left, as a share of their annual salary.

    Industry estimates for replacing an employee range from about a third to twice a
    year's salary depending on seniority; half a year is a deliberately cautious middle.
    """
    leavers = df[df["left"] == 1]
    return float((leavers["Monthly Income"] * 12 * share_of_salary).sum())
