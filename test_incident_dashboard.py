"""
Unit tests for the incident_dashboard module.

These tests exercise the high-level functions used by the dashboard script.
They ensure that input validation occurs and that summary tables are
generated correctly.
"""
from pathlib import Path
import pandas as pd
import pytest

import incident_dashboard as dash



def test_load_events_missing_file(tmp_path: Path) -> None:
    """Loading a non-existent file should raise FileNotFoundError."""
    nonexistent = tmp_path / "nope.csv"
    with pytest.raises(FileNotFoundError):
        dash.load_events(nonexistent)


def test_load_events_missing_columns(tmp_path: Path) -> None:
    """Missing required columns should raise ValueError."""
    bad_csv = tmp_path / "bad.csv"
    bad_df = pd.DataFrame({"timestamp": ["2025-01-01T00:00:00"], "event_type": ["Test"]})
    bad_df.to_csv(bad_csv, index=False)
    with pytest.raises(ValueError):
        dash.load_events(bad_csv)


def test_generate_summary_counts() -> None:
    """Verify that summary counts match the expected values for the sample dataset."""
    df = pd.read_csv(Path(__file__).with_name("sample_logs.csv"))
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    summary = dash.generate_summary(df)
    # Ensure the summary contains the expected rows and columns
    assert set(summary.index) == {"Failed Login", "Phishing URL", "Port Scan", "Threat Intel", "Vulnerability"}
    assert list(summary.columns) == ["low", "medium", "high"]
    # Check a few expected counts
    assert summary.loc["Failed Login", "high"] == 1
    assert summary.loc["Phishing URL", "medium"] == 1
    assert summary.loc["Port Scan", "low"] == 1
