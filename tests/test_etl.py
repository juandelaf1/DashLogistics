import pandas as pd
import pytest
from pathlib import Path

import src.etl.etl as etl


def test_clean_data_removes_invalid_rows():
    df = pd.DataFrame([
        {"rank": 1, "state": "California", "postal": "CA", "population": 100},
        {"rank": 0, "state": "", "postal": "XX", "population": -1},  # invalid
        {"rank": 2, "state": " Texas ", "postal": "TX", "population": 200},
        {"rank": 3, "state": "NY", "postal": "NYX", "population": 300},  # postal invalid
    ])

    df_clean = etl.clean_data(df)

    assert len(df_clean) == 2
    assert set(df_clean['state'].tolist()) == {"CALIFORNIA", "TEXAS"}
    assert 'population_per_rank' in df_clean.columns


def test_save_and_load_data(tmp_path, monkeypatch):
    # Prepare a temp raw csv and set RAW_PATH
    tmp_raw = tmp_path / 'raw' / 'sample.csv'
    tmp_raw.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([{"rank": 1, "state": "CA", "postal": "CA", "population": 100}]).to_csv(tmp_raw, index=False)

    monkeypatch.setattr(etl, 'RAW_PATH', tmp_raw)

    df = etl.load_data()
    assert len(df) == 1

    # Test save_data writes the clean CSV
    tmp_clean = tmp_path / 'clean' / 'out.csv'
    monkeypatch.setattr(etl, 'CLEAN_PATH', tmp_clean)
    etl.save_data(df)
    assert tmp_clean.exists()
