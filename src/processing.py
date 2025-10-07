# src/processing.py
import pandas as pd
from src import config  # Import our new config file


def create_master_municipality_list(cwb_df_2021):
    """
    Uses the CWB 2021 data to create the canonical list of municipalities,
    incorporating all of your manual name and duplicate corrections.
    This is the authoritative source for all other cleaning.
    """
    df = cwb_df_2021.copy()

    # --- Start: Logic from your script ---
    # Rename North Vancouver based on CSD code
    df.loc[df["CSD Code 2021"] == 5915046, "CSD Name 2021"] = "North Vancouver District"
    df.loc[df["CSD Code 2021"] == 5915051, "CSD Name 2021"] = "North Vancouver City"

    # Rename Langley based on CSD code
    df.loc[df["CSD Code 2021"] == 5915001, "CSD Name 2021"] = "Langley Township"
    df.loc[df["CSD Code 2021"] == 5915002, "CSD Name 2021"] = "Langley City"

    # Rename other specific entities
    df["CSD Name 2021"] = df["CSD Name 2021"].replace(
        {
            "Sun Peaks Mountain": "Sun Peaks Mountain Resort",
        }
    )
    df.loc[df["CSD Code 2021"] == 5929803, "CSD Name 2021"] = "Sechelt IGD"

    # Remove duplicates by keeping only the correct BC CSD codes
    for city_name, correct_code in config.BC_CSD_CODES_FOR_DUPLICATES.items():
        df = df[
            ~(
                (df["CSD Name 2021"] == city_name)
                & (df["CSD Code 2021"] != correct_code)
            )
        ]
    # --- End: Logic from your script ---

    master_list = df[["CSD Name 2021"]].copy()
    master_list = master_list.rename(columns={"CSD Name 2021": "Municipality"})
    master_list.drop_duplicates(inplace=True)

    return master_list["Municipality"].tolist()


def process_and_tidy_emissions(
    df, name_col, year_col, value_col, metric_name, master_list
):
    """
    Generic function to clean, filter, aggregate, and tidy an emissions dataframe.
    """
    # 1. Filter out regional districts, etc.
    entities_to_remove = (
        config.BC_REGIONAL_DISTRICTS
        + config.LIST_OF_UNINCORPORATED_AREAS
        + config.PROVINCE
    )
    df = df[~df[name_col].isin(entities_to_remove)]

    # 2. Apply your manual name corrections
    df[name_col] = df[name_col].replace(config.EMISSIONS_NAME_MAP)

    # 3. CRITICAL: Filter to ONLY include municipalities from our master list
    df = df[df[name_col].isin(master_list)]

    # 4. Now it's safe to aggregate
    df[value_col] = pd.to_numeric(
        df[value_col].astype(str).replace("W", "0"), errors="coerce"
    )
    aggregated = df.groupby([year_col, name_col])[value_col].sum().reset_index()

    # 5. Standardize and Tidy
    aggregated = aggregated.rename(
        columns={year_col: "Year", name_col: "Municipality", value_col: "Value"}
    )
    aggregated["Metric"] = metric_name
    aggregated["Unit"] = "tCO2e"

    return aggregated[["Year", "Municipality", "Metric", "Value", "Unit"]]


def process_and_tidy_cwb(cwb_df, year, master_list):
    """
    Processes a single wide CWB file, applies name corrections, filters, and tidies.
    """
    # This function would contain all the CSD-based name corrections specific to this file's columns
    # (As done in the master list function, but repeated for each year's column names)
    # ... [code for CWB name corrections for the specific year] ...

    name_col = f"CSD Name {year}"
    df = cwb_df.rename(columns={name_col: "Municipality"})

    # Filter to master list
    df = df[df["Municipality"].isin(master_list)]

    # Melt the dataframe
    id_vars = ["Municipality"]
    value_vars = [
        col for col in df.columns if str(year) in col and "CSD Code" not in col
    ]
    df_long = pd.melt(
        df,
        id_vars=id_vars,
        value_vars=value_vars,
        var_name="Metric",
        value_name="Value",
    )

    # Clean up the new 'Metric' column
    df_long["Metric"] = df_long["Metric"].str.replace(f" {year}", "", regex=False)
    df_long["Year"] = year
    df_long["Unit"] = "Index_Score"

    return df_long[["Year", "Municipality", "Metric", "Value", "Unit"]]
