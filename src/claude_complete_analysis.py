# %% [markdown]
# # BC Municipalities Decoupling Analysis - Tidy Data Version
#
# Research question: To what extent are municipalities able to achieve "green growth"
# (or post-growth?) in British Columbia, as measured by a decoupling of growth in
# wellbeing from growth in transportation and utility GHG emissions?

# %%
import os
import sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import seaborn as sns

# %% [markdown]
# ## 1. Define Constants and Helper Functions

# %%
# Define all the lists needed for filtering
BC_REGIONAL_DISTRICTS = [
    "Alberni-Clayoquot",
    "Bulkley-Nechako",
    "Capital",
    "Cariboo",
    "Central Coast",
    "Central Kootenay",
    "Central Okanagan",
    "Columbia-Shuswap",
    "Comox Valley",
    "Cowichan Valley",
    "East Kootenay",
    "Fraser Valley",
    "Fraser-Fort George",
    "Greater Vancouver",
    "Islands Trust",
    "Kitimat-Stikine",
    "Kootenay Boundary",
    "Metro-Vancouver",
    "Mount Waddington",
    "Nanaimo RD",
    "North Okanagan",
    "Northern Rockies RD",
    "Okanagan-Similkameen",
    "Peace River",
    "qathet",
    "Skeena-Queen Charlotte",
    "Squamish-Lillooet",
    "Stikine",
    "Sitkine",
    "Strathcona",
    "Sunshine Coast",
    "Thompson-Nicola",
]

UNINCORPORATED_AREAS = [
    f"{district} Unincorporated Areas"
    for district in [
        "Alberni-Clayoquot",
        "Bulkley-Nechako",
        "Capital",
        "Cariboo",
        "Central Coast",
        "Central Kootenay",
        "Central Okanagan",
        "Columbia-Shuswap",
        "Comox Valley",
        "Comox",
        "Cowichan Valley",
        "East Kootenay",
        "Fraser Valley",
        "Fraser-Fort George",
        "Greater Vancouver",
        "Islands Trust",
        "Kitimat-Stikine",
        "Kootenay Boundary",
        "Metro-Vancouver",
        "Mount Waddington",
        "Nanaimo",
        "Northern Rockies",
        "Skeena-Queen Charlotte",
        "North Okanagan",
        "Okanagan-Similkameen",
        "Peace River",
        "Powell River",
        "qathet",
        "Squamish-Lillooet",
        "Stikine",
        "Sitkine",
        "Sunshine Coast",
        "Strathcona",
        "Thompson-Nicola",
    ]
]

PROVINCE = ["British Columbia"]

# Name standardization mappings
NAME_CORRECTIONS = {
    "Greater Vancouver": "Metro Vancouver",
    "Sun Peaks Mountain": "Sun Peaks Mountain Resort",
    "Sechelt District Municipality": "Sechelt",
    "Sechelt Ind Gov Dist (Part-Powell River)": "Sechelt IGD",
    "Sechelt Ind Gov Dist": "Sechelt IGD",
    "Norther Rockies Regional Municipality": "Northern Rockies",
}

# BC CSD codes for disambiguation
BC_CSD_CODES = {
    "Victoria": 5917034,
    "Richmond": 5915015,
    "Armstrong": 5937028,
    "Nelson": 5903015,
    "Kent": 5909032,
    "Hope": 5909009,
    "Esquimalt": 5917040,
    "Alert Bay": 5943008,
    "Langford": 5917044,
}

# %% [markdown]
# ## 2. Data Loading and Cleaning Functions


# %%
def clean_emissions_data(df, emissions_col, org_col="ORG_NAME"):
    """Clean emissions data: remove regional districts, handle missing values, apply name corrections"""
    # Remove regional districts and unincorporated areas
    mask = ~df[org_col].isin(UNINCORPORATED_AREAS + BC_REGIONAL_DISTRICTS + PROVINCE)
    df_filtered = df[mask].copy()

    # Apply name corrections
    for old_name, new_name in NAME_CORRECTIONS.items():
        df_filtered[org_col] = df_filtered[org_col].str.replace(
            old_name, new_name, regex=False
        )

    # Clean emissions values
    if df_filtered[emissions_col].dtype == "object":
        df_filtered[emissions_col] = (
            df_filtered[emissions_col]
            .astype(str)
            .str.replace(",", "")
            .str.replace("W", "0")
        )
        df_filtered[emissions_col] = pd.to_numeric(
            df_filtered[emissions_col], errors="coerce"
        ).fillna(0)

    return df_filtered


def clean_cwb_data(cwb_df, year):
    """Clean CWB data: handle duplicates, apply name corrections, filter to BC"""
    df = cwb_df.copy()

    # Column name mapping for consistency
    year_cols = {
        f"CSD Name {year}": "Municipality_Name",
        f"CSD Code {year}": "CSD_Code",
        f"CWB {year}": "CWB",
        f"Income {year}": "Income",
        f"Education {year}": "Education",
        f"Housing {year}": "Housing",
        f"Labour Force Activity {year}": "Labour_Force",
        f"Census Population {year}": "Population",
    }

    # Handle 2006 special case
    if year == 2006:
        df.rename(
            columns={
                "CSD Name 2006": f"CSD Name {year}",
                "CSD Code SDR 2006": f"CSD Code {year}",
            },
            inplace=True,
        )

    # Apply CSD-based name corrections
    df.loc[df[f"CSD Code {year}"] == 5915046, f"CSD Name {year}"] = (
        "North Vancouver District"
    )
    df.loc[df[f"CSD Code {year}"] == 5915051, f"CSD Name {year}"] = (
        "North Vancouver City"
    )
    df.loc[df[f"CSD Code {year}"] == 5915001, f"CSD Name {year}"] = "Langley Township"
    df.loc[df[f"CSD Code {year}"] == 5915002, f"CSD Name {year}"] = "Langley City"
    df.loc[df[f"CSD Code {year}"] == 5929803, f"CSD Name {year}"] = "Sechelt IGD"

    # Apply general name corrections
    df[f"CSD Name {year}"] = df[f"CSD Name {year}"].replace(NAME_CORRECTIONS)
    df[f"CSD Name {year}"] = df[f"CSD Name {year}"].replace(
        "Sun Peaks Mountain", "Sun Peaks Mountain Resort"
    )

    # Remove non-BC duplicates using CSD codes
    for city_name, correct_code in BC_CSD_CODES.items():
        df = df[
            ~(
                (df[f"CSD Name {year}"] == city_name)
                & (df[f"CSD Code {year}"] != correct_code)
            )
        ]

    # Select and rename columns
    df = df[list(year_cols.keys())].rename(columns=year_cols)
    df["Year"] = year

    return df


# %% [markdown]
# ## 3. Load and Process Data into Tidy Format

# %%
# Load raw data
utility_emissions_raw = pd.read_csv("data/raw/utilities_new.csv")
transportation_emissions_raw = pd.read_csv(
    "data/raw/bc_on_road_transportation_data_at_the_community_level.csv"
)

# Clean emissions data
utility_df = clean_emissions_data(
    utility_emissions_raw, "EMISSIONS NET IMPORTS (TCO2e)"
)
transportation_df = clean_emissions_data(
    transportation_emissions_raw, "Emissions tCO2e"
)

# Aggregate emissions by year and municipality
utility_emissions = (
    utility_df.groupby(["YEAR", "ORG_NAME"])["EMISSIONS NET IMPORTS (TCO2e)"]
    .sum()
    .reset_index()
    .rename(
        columns={
            "ORG_NAME": "Municipality_Name",
            "YEAR": "Year",
            "EMISSIONS NET IMPORTS (TCO2e)": "Value",
        }
    )
)
utility_emissions["Metric"] = "Utility_Emissions"
utility_emissions["Unit"] = "tCO2e"

transportation_emissions = (
    transportation_df.groupby(["Year", "ORG_NAME"])["Emissions tCO2e"]
    .sum()
    .reset_index()
    .rename(columns={"ORG_NAME": "Municipality_Name", "Emissions tCO2e": "Value"})
)
transportation_emissions["Metric"] = "Transportation_Emissions"
transportation_emissions["Unit"] = "tCO2e"

# %% [markdown]
# ## 4. Load and Process CWB Data - Filter to BC Only

# %%
# Get list of BC municipalities from emissions datasets
bc_municipalities_transport = set(
    transportation_emissions["Municipality_Name"].unique()
)
bc_municipalities_utility = set(utility_emissions["Municipality_Name"].unique())
bc_municipalities = bc_municipalities_transport.union(bc_municipalities_utility)

print(f"BC municipalities from transportation data: {len(bc_municipalities_transport)}")
print(f"BC municipalities from utility data: {len(bc_municipalities_utility)}")
print(f"Total unique BC municipalities: {len(bc_municipalities)}")

# Load CWB data for all years
cwb_years = [
    2006,
    2011,
    2021,
]  # removed 2016 because it's crashing if I keep if for some unknown reason
cwb_data_list = []

for year in cwb_years:
    cwb_raw = pd.read_csv(f"data/raw/CWB_{year}.csv", encoding="latin-1")
    cwb_clean = clean_cwb_data(cwb_raw, year)
    cwb_data_list.append(cwb_clean)

# Combine all CWB data
cwb_combined = pd.concat(cwb_data_list, ignore_index=True)

# CRITICAL: Filter CWB data to only BC municipalities
cwb_combined = cwb_combined[
    cwb_combined["Municipality_Name"].isin(bc_municipalities)
].copy()

print(f"\nAfter filtering to BC municipalities:")
print(
    f"Unique municipalities in CWB data: {cwb_combined['Municipality_Name'].nunique()}"
)

# Find exact matches across all years for consistent analysis
cwb_2021_munis = set(cwb_combined[cwb_combined["Year"] == 2021]["Municipality_Name"])
cwb_2016_munis = set(cwb_combined[cwb_combined["Year"] == 2016]["Municipality_Name"])
cwb_2011_munis = set(cwb_combined[cwb_combined["Year"] == 2011]["Municipality_Name"])
cwb_2006_munis = set(cwb_combined[cwb_combined["Year"] == 2006]["Municipality_Name"])

# Find municipalities with data in all CWB years
consistent_cwb_munis = (
    cwb_2021_munis.intersection(cwb_2016_munis)
    .intersection(cwb_2011_munis)
    .intersection(cwb_2006_munis)
)
print(
    f"Municipalities with CWB data in all years (2006, 2011, 2016, 2021): {len(consistent_cwb_munis)}"
)

# Find municipalities with both emissions and CWB data
final_municipalities = consistent_cwb_munis.intersection(bc_municipalities)
print(
    f"Final municipalities with both emissions and CWB data: {len(final_municipalities)}"
)

# Filter to final set
cwb_combined = cwb_combined[
    cwb_combined["Municipality_Name"].isin(final_municipalities)
].copy()

# Convert CWB to long format
cwb_metrics = ["CWB", "Income", "Education", "Housing", "Labour_Force", "Population"]
cwb_long_list = []

for metric in cwb_metrics:
    temp_df = cwb_combined[["Municipality_Name", "Year", metric]].copy()
    temp_df.rename(columns={metric: "Value"}, inplace=True)
    temp_df["Metric"] = metric
    temp_df["Unit"] = "index" if metric != "Population" else "count"
    cwb_long_list.append(temp_df)

cwb_long = pd.concat(cwb_long_list, ignore_index=True)

# %% [markdown]
# ## 5. Align Emissions Data with CWB Municipalities

# %%
# Filter emissions data to only include municipalities with CWB data
utility_emissions_filtered = utility_emissions[
    utility_emissions["Municipality_Name"].isin(final_municipalities)
].copy()
transportation_emissions_filtered = transportation_emissions[
    transportation_emissions["Municipality_Name"].isin(final_municipalities)
].copy()

print(f"\nEmissions data after filtering to municipalities with CWB data:")
print(
    f"Utility emissions municipalities: {utility_emissions_filtered['Municipality_Name'].nunique()}"
)
print(
    f"Transportation emissions municipalities: {transportation_emissions_filtered['Municipality_Name'].nunique()}"
)

# Check for any municipalities missing emissions data
missing_utility = final_municipalities - set(
    utility_emissions_filtered["Municipality_Name"].unique()
)
missing_transport = final_municipalities - set(
    transportation_emissions_filtered["Municipality_Name"].unique()
)

if missing_utility:
    print(f"\nMunicipalities with CWB but no utility emissions data: {missing_utility}")
if missing_transport:
    print(
        f"\nMunicipalities with CWB but no transportation emissions data: {missing_transport}"
    )

# %% [markdown]
# ## 6. Combine All Data into Single Tidy DataFrame

# %%
# Combine all metrics into one tidy dataframe
all_metrics = pd.concat(
    [utility_emissions_filtered, transportation_emissions_filtered, cwb_long],
    ignore_index=True,
)

# Sort for better organization
all_metrics = all_metrics.sort_values(
    ["Municipality_Name", "Year", "Metric"]
).reset_index(drop=True)

print("Tidy data structure created!")
print(f"Shape: {all_metrics.shape}")
print(f"Unique municipalities: {all_metrics['Municipality_Name'].nunique()}")
print(f"Unique metrics: {all_metrics['Metric'].nunique()}")
print(f"Years covered: {sorted(all_metrics['Year'].unique())}")
print("\nFirst few rows:")
print(all_metrics.head(10))

# Save tidy data
all_metrics.to_csv("../data/processed/tidy_all_metrics.csv", index=False)

# %% [markdown]
# ## 6. Calculate Derived Metrics (Percent Changes)


# %%
def calculate_percent_change(df, base_years, target_years, metric_name):
    """Calculate percent change between two periods"""
    # Filter data
    metric_df = df[df["Metric"] == metric_name].copy()

    # Calculate period averages
    base_avg = (
        metric_df[metric_df["Year"].isin(base_years)]
        .groupby("Municipality_Name")["Value"]
        .mean()
        .reset_index()
        .rename(columns={"Value": "base_value"})
    )

    target_avg = (
        metric_df[metric_df["Year"].isin(target_years)]
        .groupby("Municipality_Name")["Value"]
        .mean()
        .reset_index()
        .rename(columns={"Value": "target_value"})
    )

    # Merge and calculate percent change
    changes = pd.merge(base_avg, target_avg, on="Municipality_Name", how="inner")
    changes["percent_change"] = (
        (changes["target_value"] - changes["base_value"]) / changes["base_value"]
    ) * 100
    changes["Metric"] = f"{metric_name}_percent_change"
    changes["base_period"] = f"{min(base_years)}-{max(base_years)}"
    changes["target_period"] = f"{min(target_years)}-{max(target_years)}"

    return changes[
        [
            "Municipality_Name",
            "Metric",
            "percent_change",
            "base_period",
            "target_period",
        ]
    ]


# Calculate percent changes for emissions (2007-2010 to 2017-2020)
utility_changes = calculate_percent_change(
    all_metrics, [2007, 2010], [2017, 2018, 2019, 2020], "Utility_Emissions"
)
transport_changes = calculate_percent_change(
    all_metrics, [2007, 2010], [2017, 2018, 2019, 2020], "Transportation_Emissions"
)

# Calculate percent changes for wellbeing metrics (2011 to 2021)
wellbeing_metrics = [
    "CWB",
    "Income",
    "Education",
    "Housing",
    "Labour_Force",
    "Population",
]
wellbeing_changes_list = []

for metric in wellbeing_metrics:
    changes = calculate_percent_change(all_metrics, [2011], [2021], metric)
    wellbeing_changes_list.append(changes)

# Combine all percent changes
all_changes = pd.concat(
    [utility_changes, transport_changes] + wellbeing_changes_list, ignore_index=True
)

# %% [markdown]
# ## 7. Create Analysis-Ready Dataset

# %%
# Pivot changes to wide format for analysis
analysis_data = all_changes.pivot(
    index="Municipality_Name", columns="Metric", values="percent_change"
).reset_index()


# Add decoupling categories
def categorize_decoupling(emissions_change, wellbeing_change):
    if emissions_change < -0.5 and wellbeing_change > 0.5:
        return "Strong_Decoupling"
    elif (
        emissions_change > 0.5
        and wellbeing_change > 0.5
        and wellbeing_change > emissions_change
    ):
        return "Weak_Decoupling"
    elif emissions_change > 0.5 and wellbeing_change < -0.5:
        return "Worst_Case"
    else:
        return "Other"


analysis_data["transport_decoupling"] = analysis_data.apply(
    lambda x: categorize_decoupling(
        x["Transportation_Emissions_percent_change"], x["CWB_percent_change"]
    ),
    axis=1,
)
analysis_data["utility_decoupling"] = analysis_data.apply(
    lambda x: categorize_decoupling(
        x["Utility_Emissions_percent_change"], x["CWB_percent_change"]
    ),
    axis=1,
)

# Save analysis-ready data
analysis_data.to_csv("../data/processed/analysis_ready_data.csv", index=False)

print("\nAnalysis-ready dataset created!")
print(f"Shape: {analysis_data.shape}")
print("\nColumns available for regression:")
print(analysis_data.columns.tolist())

# %% [markdown]
# ## 8. Example Statistical Analysis

# %%
# Example: Simple regression analysis
from scipy import stats

# Remove NaN values
clean_data = analysis_data.dropna(
    subset=["Transportation_Emissions_percent_change", "CWB_percent_change"]
)

# Correlation analysis
corr, p_value = stats.pearsonr(
    clean_data["Transportation_Emissions_percent_change"],
    clean_data["CWB_percent_change"],
)

print(f"\nCorrelation between Transportation Emissions and Wellbeing changes:")
print(f"Correlation coefficient: {corr:.3f}")
print(f"P-value: {p_value:.4f}")

# Example: Multiple regression using the tidy format
# You can now easily select any combination of metrics for regression
from sklearn.linear_model import LinearRegression

# Prepare data for regression
X = clean_data[
    ["Transportation_Emissions_percent_change", "Utility_Emissions_percent_change"]
]
y = clean_data["CWB_percent_change"]

# Remove any remaining NaN
mask = ~(X.isna().any(axis=1) | y.isna())
X_clean = X[mask]
y_clean = y[mask]

# Fit model
model = LinearRegression()
model.fit(X_clean, y_clean)

print(f"\nMultiple Regression Results:")
print(f"R-squared: {model.score(X_clean, y_clean):.3f}")
print(f"Coefficients:")
for i, col in enumerate(X_clean.columns):
    print(f"  {col}: {model.coef_[i]:.4f}")

# %% [markdown]
# ## 9. Demonstration: Working with Tidy Data


# %%
# Example: Filter and analyze specific metrics over time
def analyze_metric_trends(tidy_df, municipality, metrics_list):
    """Analyze trends for specific metrics in a municipality"""
    filtered = tidy_df[
        (tidy_df["Municipality_Name"] == municipality)
        & (tidy_df["Metric"].isin(metrics_list))
    ]

    # Pivot for visualization
    pivot = filtered.pivot(index="Year", columns="Metric", values="Value")

    # Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    for col in pivot.columns:
        ax.plot(pivot.index, pivot[col], marker="o", label=col)

    ax.set_title(f"Metrics over time: {municipality}")
    ax.set_xlabel("Year")
    ax.set_ylabel("Value")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.show()

    return pivot


# Example usage
example_municipality = analysis_data["Municipality_Name"].iloc[0]
print(f"Example analysis for: {example_municipality}")

metrics_to_analyze = ["Transportation_Emissions", "Utility_Emissions", "CWB"]
trends = analyze_metric_trends(all_metrics, example_municipality, metrics_to_analyze)

print("\nThe tidy format makes it easy to:")
print("1. Filter by any combination of municipalities, years, or metrics")
print("2. Aggregate data flexibly (e.g., by region, time period)")
print("3. Run statistical analyses without reshaping")
print("4. Add new metrics without changing the structure")
print("5. Create visualizations dynamically")
