# src/data_loader.py
import pandas as pd


def load_utility_emissions(filepath):
    """Loads and does initial light cleaning on utility emissions data."""
    df = pd.read_csv(filepath)
    df["EMISSIONS NET IMPORTS (TCO2e)"] = df["EMISSIONS NET IMPORTS (TCO2e)"].replace(
        "W", 0
    )
    return df


def load_transport_emissions(filepath):
    """Loads transportation emissions data."""
    # The DtypeWarning suggests mixed types, so we can specify dtype on load
    df = pd.read_csv(filepath, dtype={"Unnamed: 11": str})
    return df


def load_cwb_data(filepath):
    """Loads a single CWB dataset."""
    return pd.read_csv(filepath, encoding="latin-1")
