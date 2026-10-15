"""Export model-ready tables for Power BI (and Tableau).

    python -m bi.build_bi

Writes bi/data/*.csv and bi/kpis.json (the headline numbers your dashboard should show,
so you can check a Power BI build against this repo and the existing Tableau workbook).
Uses the same cleaning and bands as the live report, so every figure matches it.
"""

import json
from pathlib import Path

import pandas as pd

from analysis import data as d

OUT = Path(__file__).resolve().parent

SAT_COLS = ["Environment Satisfaction", "Job Satisfaction", "Relationship Satisfaction", "Work Life Balance", "Job Involvement"]


def tables(df: pd.DataFrame) -> dict:
    keep = [
        "Employee Number", "Attrition", "left", "Department", "Job Role", "Job Level", "Education Field",
        "Education", "Gender", "Marital Status", "Age", "age_band", "Business Travel", "travel",
        "Over Time", "Distance From Home", "Monthly Income", "income_band", "Percent Salary Hike",
        "Stock Option Level", "Performance Rating", "Training Times Last Year", "Total Working Years",
        "Num Companies Worked", "Years At Company", "tenure_band", "Years In Current Role",
        "Years Since Last Promotion", "Years With Curr Manager",
    ] + SAT_COLS
    fact = df[keep].copy()
    fact.columns = [c.lower().replace(" ", "_") for c in fact.columns]
    fact = fact.rename(columns={"left": "left_company", "travel": "travel_frequency"})
    for c in SAT_COLS:
        col = c.lower().replace(" ", "_")
        fact[col + "_label"] = fact[col].map(d.SATISFACTION)
    # Sort keys so bands show in the right order in Power BI ("Sort by column") and Tableau.
    fact["age_band_order"] = fact["age_band"].cat.codes + 1
    fact["income_band_order"] = fact["income_band"].cat.codes + 1
    fact["tenure_band_order"] = fact["tenure_band"].cat.codes + 1
    return {"fact_employee": fact}


def kpis(df: pd.DataFrame) -> dict:
    dept = d.rates(df, "Department").sort_values("rate", ascending=False).iloc[0]
    ot = d.rates(df, "Over Time").set_index("Over Time")["rate"]
    return {
        "Employees": int(len(df)),
        "Employees who left": int(df["left"].sum()),
        "Attrition rate": round(float(df["left"].mean()), 4),
        "Active employees": int((df["left"] == 0).sum()),
        "Average age": round(float(df["Age"].mean()), 1),
        "Average monthly income": round(float(df["Monthly Income"].mean()), 0),
        "Highest-attrition department": f"{dept['Department']} ({dept['rate']:.1%})",
        "Attrition with overtime": round(float(ot["Yes"]), 4),
        "Attrition without overtime": round(float(ot["No"]), 4),
        "Estimated replacement cost (half a year's salary)": round(d.replacement_cost(df), 0),
    }


def build(out: Path = OUT) -> dict:
    df = d.load()
    t = tables(df)
    (out / "data").mkdir(parents=True, exist_ok=True)
    for name, frame in t.items():
        frame.to_csv(out / "data" / f"{name}.csv", index=False)
    k = kpis(df)
    (out / "kpis.json").write_text(json.dumps(k, indent=2) + "\n")
    return {"tables": t, "kpis": k}


if __name__ == "__main__":
    res = build()
    for name, frame in res["tables"].items():
        print(f"{name}: {len(frame):,} rows")
    print(json.dumps(res["kpis"], indent=2))
