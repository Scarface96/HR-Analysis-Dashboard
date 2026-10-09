import numpy as np
import pandas as pd
import pytest

from analysis import data, drivers


@pytest.fixture(scope="module")
def df():
    return data.load()


def test_load_drops_constant_columns(df):
    assert len(df) == 1470
    for col in ["Standard Hours", "Employee Count", "Over18"]:
        assert col not in df.columns
    assert df["left"].sum() == 237


def test_rates_and_intervals(df):
    t = data.rates(df, "Over Time").set_index("Over Time")
    assert t.loc["Yes", "rate"] == pytest.approx(127 / 416)
    assert (t["low"] < t["rate"]).all() and (t["rate"] < t["high"]).all()


def test_wilson_narrows_with_more_data():
    lo1, hi1 = data.wilson(5, 10)
    lo2, hi2 = data.wilson(500, 1000)
    assert hi2 - lo2 < hi1 - lo1


def test_bands_cover_everyone(df):
    for col in ["age_band", "income_band", "tenure_band"]:
        assert df[col].notna().all()


def test_drivers_model(df):
    t = drivers.odds_ratios(df).set_index("feature")
    assert t.loc["overtime", "odds_ratio"] > 3 and t.loc["overtime", "significant"]
    assert (t["low"] <= t["odds_ratio"]).all() and (t["odds_ratio"] <= t["high"]).all()
    assert 0.7 < drivers.cv_auc(df) < 0.95


def test_replacement_cost_scales_with_assumption(df):
    assert data.replacement_cost(df, 1.0) == pytest.approx(2 * data.replacement_cost(df, 0.5))
