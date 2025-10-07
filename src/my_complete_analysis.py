# %% [markdown]
# Research question
#
# To what extent are municipalities able to achieve “green growth” (or post-growth?) in British Columbia, as measured by a decoupling of growth in wellbeing from the growth in transportation and utility GHG emissions?
#
# What inequities exist in the access of solar energy across B.C.? Do these inequities correlate with lower housing wellbeing index?
#
# Scope
#
# Timeframe: 2012 – 2021
#
# Emissions scope: CO2e for utilities of residential and small and medium indistry, on-road transportation

# %%
# import libraries
import os
import sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# %%
# load the community emissions dataset as csv file
utility_emissions = pd.read_csv("../data/raw/utilities_new.csv")

# replace W's from emissions in wood with 0
utility_emissions["EMISSIONS NET IMPORTS (TCO2e)"] = utility_emissions[
    "EMISSIONS NET IMPORTS (TCO2e)"
].replace("W", 0)

# Display the first few rows of the utility emissions dataset
utility_emissions.head()

# %%
# load the transportation emissions dataset as csv file
transportation_emissions = pd.read_csv(
    "../data/raw/bc_on_road_transportation_data_at_the_community_level.csv"
)
transportation_emissions.head()


# %% [markdown]
# To add industrial emissions:
# 1. convert lat and lon of each industry to points that can fall within the area of the municipal boundaries
# 2. assign the municipality name to each industry in the industries dataset (creating a new column to hold the municipality names in the industry dataset)
# 3. sum up the emissions of all industries within each municipality area and assign total emissions to that municipality in a new dataset
# 4. change the naming of municipalities in the shape file to match the naming of the other emissions datasets, so that we can aggregate these emissions

# %%
# list of regional districts including typos in datasets
bc_regional_districts = [
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
# list of unincorporated areas
list_of_unincorporated_areas = [
    "Alberni-Clayoquot Unincorporated Areas",
    "Bulkley-Nechako Unincorporated Areas",
    "Capital Unincorporated Areas",
    "Cariboo Unincorporated Areas",
    "Central Coast Unincorporated Areas",
    "Central Kootenay Unincorporated Areas",
    "Central Okanagan Unincorporated Areas",
    "Columbia-Shuswap Unincorporated Areas",
    "Comox Valley Unincorporated Areas",
    "Comox Unincorporated Areas",
    "Cowichan Valley Unincorporated Areas",
    "East Kootenay Unincorporated Areas",
    "Fraser Valley Unincorporated Areas",
    "Fraser-Fort George Unincorporated Areas",
    "Greater Vancouver Unincorporated Areas",
    "Islands Trust Unincorporated Areas",
    "Kitimat-Stikine Unincorporated Areas",
    "Kootenay Boundary Unincorporated Areas",
    "Metro-Vancouver Unincorporated Areas",
    "Mount Waddington Unincorporated Areas",
    "Nanaimo Unincorporated Areas",
    "Northern Rockies Unincorporated Areas",  # check if there are variations to this, like Northern Rockies Regional Municipality Unincorporated Areas
    "Skeena-Queen Charlotte Unincorporated Areas",
    "North Okanagan Unincorporated Areas",
    "Okanagan-Similkameen Unincorporated Areas",
    "Peace River Unincorporated Areas",
    "Powell River Unincorporated Areas",
    "qathet Unincorporated Areas",
    "Squamish-Lillooet Unincorporated Areas",
    "Stikine Unincorporated Areas",
    "Sitkine Unincorporated Areas",
    "Sunshine Coast Unincorporated Areas",
    "Strathcona Unincorporated Areas",
    "Thompson-Nicola Unincorporated Areas",
]
province = ["British Columbia"]

Indigenous = ["Sechelt IGD", "Sechelt Ind Gov Dist (Part-Powell River)"]

outliers = [
    "Northern Rockies Regional Municipality",
    "Northern Rockies RD",
    "Northern Rockies",
]

# list of years
years_transportation_co2 = [
    2007,
    2008,
    2009,
    2010,
    2011,
    2012,
    2013,
    2014,
    2015,
    2016,
    2017,
    2018,
    2019,
    2020,
    2021,
    2022,
]
years_buildings_co2 = [
    2007,
    2010,
    2012,
    2013,
    2014,
    2015,
    2016,
    2017,
    2018,
    2019,
    2020,
    2021,
    2022,
]
years_waste_co2 = [
    2007,
    2010,
    2012,
    2013,
    2014,
    2015,
    2016,
    2017,
    2018,
    2019,
    2020,
    2021,
    2022,
]

# %%
# select municipalities from the utility emissions dataset (by excluding regional districts and unincorporated areas)
mask = ~utility_emissions["ORG_NAME"].isin(
    list_of_unincorporated_areas + bc_regional_districts + province
)
utility_df = utility_emissions[mask]
print(utility_df["ORG_NAME"].unique())
# save the utility_df to a csv file in the data/processed folder
utility_df.to_csv(
    os.path.join("..", "data", "processed", "municipalities_utility_emissions.csv"),
    index=False,
)
utility_df.head()

# %%
# select municipalities from the transportation emissions dataset (by excluding regional districts and unincorporated areas)
mask = ~transportation_emissions["ORG_NAME"].isin(
    list_of_unincorporated_areas + bc_regional_districts + province
)
transportation_df = transportation_emissions[mask]

# change names of communities to match the utility_df
# Greater Vancouver -> Metro Vancouver
# Sun Peaks Mountain -> Sun Peaks Mountain Resort
# Sechelt District Municipality -> Sechelt

transportation_df["ORG_NAME"] = transportation_df["ORG_NAME"].replace(
    {
        "Greater Vancouver": "Metro Vancouver",
        "Sun Peaks Mountain": "Sun Peaks Mountain Resort",
        "Sechelt District Municipality": "Sechelt",
        "Sechelt Ind Gov Dist (Part-Powell River)": "Sechelt IGD",
        "Sechelt Ind Gov Dist": "Sechelt IGD",
    }
)
transportation_df.to_csv(
    os.path.join(
        "..", "data", "processed", "municipalities_transportation_emissions.csv"
    ),
    index=False,
)
transportation_df.head()
# print(transportation_df['ORG_NAME'].unique())

# %%
# Remove commas from the values, then convert to numeric
utility_df["EMISSIONS NET IMPORTS (TCO2e)"] = (
    utility_df["EMISSIONS NET IMPORTS (TCO2e)"].astype(str).str.replace(",", "")
)
# remove 'W' from the values and convert to numeric, filling NaN with 0
utility_df["EMISSIONS NET IMPORTS (TCO2e)"] = pd.to_numeric(
    utility_df["EMISSIONS NET IMPORTS (TCO2e)"], errors="coerce"
).fillna(0)

# correct norther rockies to northern rockies
utility_df["ORG_NAME"] = utility_df["ORG_NAME"].str.replace(
    "Norther Rockies Regional Municipality", "Northern Rockies"
)

# Group by YEAR and ORG_NAME, summing the emissions
total_utility_emissions_combined = utility_df.groupby(
    ["YEAR", "ORG_NAME"], as_index=False
)["EMISSIONS NET IMPORTS (TCO2e)"].sum()


print("\nAfter combining:")
northern_rockies_combined = total_utility_emissions_combined[
    total_utility_emissions_combined["ORG_NAME"].str.contains(
        "northern rockies", case=False, na=False
    )
]
print(northern_rockies_combined)

total_utility_emissions = total_utility_emissions_combined

# save to csv file in the data/processed folder
total_utility_emissions.to_csv(
    os.path.join("..", "data", "processed", "total_utility_emissions.csv"), index=False
)
total_utility_emissions.tail()


# %%
# print all unique org-names in the utilties dataframe
print("Unique organizations in utility emissions:")
print(total_utility_emissions["ORG_NAME"].unique())

# %%
print("\nTotal utility emissions for each community:")
# Display the total utility emissions for each community
print(total_utility_emissions)

# %%
# for each year and each community, calculate the total emissions for that community by summing the emissions for values in all vehicle fuel categories

# Group by 'YEAR' and 'ORG_NAME' and sum the emissions
total_transportation_emissions = (
    transportation_df.groupby(["Year", "ORG_NAME"])["Emissions tCO2e"]
    .sum()
    .reset_index()
)

# save to csv file in the data/processed folder
total_transportation_emissions.to_csv(
    os.path.join("..", "data", "processed", "total_transportation_emissions.csv"),
    index=False,
)

# %%
print("Unique organizations in total_emissions:")
print(total_transportation_emissions["ORG_NAME"].unique())

# %%
print("\nTotal transportation emissions for each community:")
# Display the total transportation emissions for each community
# total_emissions.head()
print(total_transportation_emissions)

# %%
print("\nTotal utility emissions for each community:")
# Display the total transportation emissions for each community
# total_emissions.head()
print(total_utility_emissions)

# %%
transportation_emissions_communities_list = set(
    total_transportation_emissions["ORG_NAME"]
)
utility_emissions_communities_list = set(total_utility_emissions["ORG_NAME"])
# Find communities that are in transportation emissions but not in utility emissions
missing_communities = (
    transportation_emissions_communities_list - utility_emissions_communities_list
)
print("\nCommunities in transportation emissions but not in utility emissions:")
print(missing_communities)
# Find communities that are in utility emissions but not in transportation emissions
missing_communities = (
    utility_emissions_communities_list - transportation_emissions_communities_list
)
print("\nCommunities in utility emissions but not in transportation emissions:")
print(missing_communities)

# %%
total_transportation_emissions.rename(columns={"Year": "YEAR"}, inplace=True)


# %%
tidy_utility = total_utility_emissions.copy()
tidy_utility["Metric"] = "Utility_Emissions"
tidy_transport = total_transportation_emissions.copy()
tidy_transport["Metric"] = "Transport_Emissions"

# %%
tidy_utility.head()

# %%
transportation_emissions_pivot = total_transportation_emissions.pivot(
    index="ORG_NAME", columns="YEAR", values="Emissions tCO2e"
)

utility_emissions_pivot = total_utility_emissions.pivot(
    index="ORG_NAME", columns="YEAR", values="EMISSIONS NET IMPORTS (TCO2e)"
)


# %%
# try to aggregate based on subsector instead of org_name
# test_utility_emissions_pivot = total_utility_emissions.pivot(index='SUB_SECTOR', columns='YEAR', values='EMISSIONS NET IMPORTS (TCO2e)')


# %%
utility_emissions_pivot.head()

# %%
transportation_emissions_pivot.head()

# %%
# Create the relative emissions DataFrame
# This divides every value in each row by that row's 2007 value.
relative_utility_emissions = utility_emissions_pivot.div(
    utility_emissions_pivot[2007], axis=0
)
relative_transportation_emissions = transportation_emissions_pivot.div(
    transportation_emissions_pivot[2007], axis=0
)
# Let's look at the result
print("Relative utility emissions \n", relative_utility_emissions.head(), "\n")
print("Relative transportation emissions \n", relative_transportation_emissions.head())

# %%
relative_utility_emissions.index.values
# this shows that northern rockies has two entries: ['Northern Rockies', 'Northern Rockies Regional Municipality']

# %%
# open CWB_2021 and CWB_2011 from the data folder/raw
# Load the dataset
cwb_2021 = pd.read_csv(
    os.path.join("..", "data", "raw", "CWB_2021.csv"), encoding="latin-1"
)
cwb_2016 = pd.read_csv(os.path.join("..", "data", "raw", "CWB_2016.csv"))
cwb_2011 = pd.read_csv(
    os.path.join("..", "data", "raw", "CWB_2011.csv"), encoding="latin-1"
)
cwb_2006 = pd.read_csv(
    os.path.join("..", "data", "raw", "CWB_2006.csv"), encoding="latin-1"
)
# Display the first few rows of each dataset
print("CWB_2021 dataset:")
print(cwb_2021.head())

print("\n CWB_2016_dataset:")
print(cwb_2016.head())

print("\n CWB_2011_dataset:")
print(cwb_2011.head())

print("\n CWB_2006_dataset:")
print(cwb_2006.head())

# %%
# replace the csd name "north vancouver" that has a csd code 5915046 in column one, to "north vancouver district municipality"
# replace the csd name "north vancouver" that has a csd code 5915051 in column one, to "north vancouver city"

# Replace North Vancouver entries based on CSD codes
cwb_2021.loc[cwb_2021["CSD Code 2021"] == 5915046, "CSD Name 2021"] = (
    "North Vancouver District"
)
cwb_2021.loc[cwb_2021["CSD Code 2021"] == 5915051, "CSD Name 2021"] = (
    "North Vancouver City"
)

# Replace North Vancouver entries based on CSD codes (adjust column names as needed)
cwb_2016.loc[cwb_2016["CSD Code 2016"] == 5915046, "CSD Name 2016"] = (
    "North Vancouver District"
)
cwb_2016.loc[cwb_2016["CSD Code 2016"] == 5915051, "CSD Name 2016"] = (
    "North Vancouver City"
)

# Replace North Vancouver entries based on CSD codes (adjust column names as needed)
cwb_2011.loc[cwb_2011["CSD Code 2011"] == 5915046, "CSD Name 2011"] = (
    "North Vancouver District"
)
cwb_2011.loc[cwb_2011["CSD Code 2011"] == 5915051, "CSD Name 2011"] = (
    "North Vancouver City"
)

# Replace North Vancouver entries based on CSD codes (adjust column names as needed)
cwb_2006.loc[cwb_2006["CSD Code 2006"] == 5915046, "CSD Name 2006"] = (
    "North Vancouver District"
)
cwb_2006.loc[cwb_2006["CSD Code 2006"] == 5915051, "CSD Name 2006"] = (
    "North Vancouver City"
)


# rename sun peaks mountain to sun peaks mountain resort in the cwb data
cwb_2021["CSD Name 2021"] = cwb_2021["CSD Name 2021"].replace(
    "Sun Peaks Mountain", "Sun Peaks Mountain Resort"
)
cwb_2016["CSD Name 2016"] = cwb_2016["CSD Name 2016"].replace(
    "Sun Peaks Mountain", "Sun Peaks Mountain Resort"
)
cwb_2011["CSD Name 2011"] = cwb_2011["CSD Name 2011"].replace(
    "Sun Peaks Mountain", "Sun Peaks Mountain Resort"
)
cwb_2006["CSD Name 2006"] = cwb_2006["CSD Name 2006"].replace(
    "Sun Peaks Mountain", "Sun Peaks Mountain Resort"
)


# replace the csd name "langley" that has a csd code 5915001 in column one, to "langley township"
cwb_2021.loc[cwb_2021["CSD Code 2021"] == 5915001, "CSD Name 2021"] = "Langley Township"
cwb_2016.loc[cwb_2016["CSD Code 2016"] == 5915001, "CSD Name 2016"] = "Langley Township"
cwb_2011.loc[cwb_2011["CSD Code 2011"] == 5915001, "CSD Name 2011"] = "Langley Township"
cwb_2006.loc[cwb_2006["CSD Code 2006"] == 5915001, "CSD Name 2006"] = "Langley Township"


# replace the csd name "langley" that has a csd code 5915002 in column one, to "langley city"
cwb_2021.loc[cwb_2021["CSD Code 2021"] == 5915002, "CSD Name 2021"] = "Langley City"
cwb_2016.loc[cwb_2016["CSD Code 2016"] == 5915002, "CSD Name 2016"] = "Langley City"
cwb_2011.loc[cwb_2011["CSD Code 2011"] == 5915002, "CSD Name 2011"] = "Langley City"
cwb_2006.loc[cwb_2006["CSD Code 2006"] == 5915002, "CSD Name 2006"] = "Langley City"


# Replace Sechelt (Part) entries based on CSD codes
cwb_2021.loc[cwb_2021["CSD Code 2021"] == 5929803, "CSD Name 2021"] = "Sechelt IGD"
cwb_2016.loc[cwb_2016["CSD Code 2016"] == 5929803, "CSD Name 2016"] = "Sechelt IGD"
cwb_2011.loc[cwb_2011["CSD Code 2011"] == 5929803, "CSD Name 2011"] = "Sechelt IGD"
cwb_2006.loc[cwb_2006["CSD Code 2006"] == 5929803, "CSD Name 2006"] = "Sechelt IGD"

# rename CSD Name / Nom de la SDR 2006 to CSD Name 2006
cwb_2006.rename(columns={"CSD Name 2006": "CSD Name 2006"}, inplace=True)
# rename CSD Code / Code de la SDR 2006 to CSD Code 2006
cwb_2006.rename(columns={"CSD Code SDR 2006": "CSD Code 2006"}, inplace=True)

# %%
# remove cities with the same name in the wellbeing dataset that are not from BC

# Define the correct BC CSD codes
bc_csd_codes = {
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

# Remove duplicates by keeping only the BC CSD codes
for city_name, correct_code in bc_csd_codes.items():
    # Remove all rows with this city name that don't have the correct code
    cwb_2021 = cwb_2021[
        ~(
            (cwb_2021["CSD Name 2021"] == city_name)
            & (cwb_2021["CSD Code 2021"] != correct_code)
        )
    ]

print("Removed duplicate cities from 2021 dataset")

# Remove duplicates from 2016 dataset (adjust column names)
for city_name, correct_code in bc_csd_codes.items():
    # Remove all rows with this city name that don't have the correct code
    cwb_2016 = cwb_2016[
        ~(
            (cwb_2016["CSD Name 2016"] == city_name)
            & (cwb_2016["CSD Code 2016"] != correct_code)
        )
    ]

print("Removed duplicate cities from 2016 dataset")

# Remove duplicates from 2011 dataset (adjust column names)
for city_name, correct_code in bc_csd_codes.items():
    # Remove all rows with this city name that don't have the correct code
    cwb_2011 = cwb_2011[
        ~(
            (cwb_2011["CSD Name 2011"] == city_name)
            & (cwb_2011["CSD Code 2011"] != correct_code)
        )
    ]

print("Removed duplicate cities from 2006 dataset")

# Remove duplicates from 2006 dataset (adjust column names)
for city_name, correct_code in bc_csd_codes.items():
    # Remove all rows with this city name that don't have the correct code
    cwb_2006 = cwb_2006[
        ~(
            (cwb_2006["CSD Name 2006"] == city_name)
            & (cwb_2006["CSD Code 2006"] != correct_code)
        )
    ]

print("Removed duplicate cities from 2006 dataset")

# %%
# Get unique community names from each dataset as a list
transportation_emissions_communities = set(relative_transportation_emissions.index)
wellbeing_2021_communities = set(cwb_2021["CSD Name 2021"].dropna())
wellbeing_2016_communities = set(cwb_2016["CSD Name 2016"].dropna())
wellbeing_2011_communities = set(cwb_2011["CSD Name 2011"].dropna())
wellbeing_2006_communities = set(cwb_2006["CSD Name 2006"].dropna())

# Find exact matches (as a list)
exact_matches_2021 = transportation_emissions_communities.intersection(
    wellbeing_2021_communities
)
exact_matches_2016 = transportation_emissions_communities.intersection(
    wellbeing_2016_communities
)
exact_matches_2011 = transportation_emissions_communities.intersection(
    wellbeing_2011_communities
)
exact_matches_2006 = transportation_emissions_communities.intersection(
    wellbeing_2006_communities
)
exact_matches_2021_2016_2011 = exact_matches_2021.intersection(
    exact_matches_2016
).intersection(exact_matches_2011)

print(f"Exact matches with 2021 wellbeing: {len(exact_matches_2021)}")
print(f"Exact matches with 2016 wellbeing: {len(exact_matches_2016)}")
print(f"Exact matches with 2011 wellbeing: {len(exact_matches_2011)}")
print(f"Exact matches with 2006 wellbeing: {len(exact_matches_2006)}")
print(
    f"Exact matches with 2021, 2016, and 2011 wellbeing: {len(exact_matches_2021_2016_2011)}"
)
# print(f"Exact matches with both years: {len(exact_matches_both)}")

# Get unmatched communities by subtracting lists
unmatched_emissions = transportation_emissions_communities - exact_matches_2006

print(f"Total unmatched emissions communities: {len(unmatched_emissions)}")
print("\nAll unmatched emissions communities:")
for community in sorted(list(unmatched_emissions)):
    print(f"  {community}")

# %%
print(
    transportation_emissions_communities
)  # these unmatched communities are all in the transportation emissions dataset, so maybe not in the wellbeing dataset

# %%
# Create new dataframes: Filter wellbeing datasets to only include matched communities in the list of exact matches
matched_cwb_2021 = cwb_2021[
    cwb_2021["CSD Name 2021"].isin(exact_matches_2021_2016_2011)
].copy()
matched_cwb_2016 = cwb_2016[
    cwb_2016["CSD Name 2016"].isin(exact_matches_2021_2016_2011)
].copy()
matched_cwb_2011 = cwb_2011[
    cwb_2011["CSD Name 2011"].isin(exact_matches_2021_2016_2011)
].copy()
matched_cwb_2006 = cwb_2006[
    cwb_2006["CSD Name 2006"].isin(exact_matches_2021_2016_2011)
].copy()

print(f"Filtered wellbeing data:")
print(f"  2021: {len(matched_cwb_2021)} communities")
print(f"  2016: {len(matched_cwb_2016)} communities")
print(f"  2011: {len(matched_cwb_2011)} communities")
print(f"  2006: {len(matched_cwb_2006)} communities")

# Also filter emissions data to matched communities
matched_transportation_emissions = relative_transportation_emissions[
    relative_transportation_emissions.index.isin(exact_matches_2021_2016_2011)
].copy()
print(
    f"  Transportation Emissions: {len(matched_transportation_emissions)} communities"
)

# Also filter emissions data to matched communities
matched_utility_emissions = relative_utility_emissions[
    relative_utility_emissions.index.isin(exact_matches_2021_2016_2011)
].copy()
print(f"  Utility Emissions: {len(matched_utility_emissions)} communities")

# %%
# Check for duplicate community names in wellbeing data
print("Duplicate community names in 2021 wellbeing data:")
duplicates_2021 = matched_cwb_2021[cwb_2021.duplicated("CSD Name 2021", keep=False)][
    "CSD Name 2021"
].value_counts()
print(duplicates_2021)

print("\nDuplicate community names in 2011 wellbeing data:")
duplicates_2016 = matched_cwb_2016[cwb_2016.duplicated("CSD Name 2016", keep=False)][
    "CSD Name 2016"
].value_counts()
print(duplicates_2016)

print("\nDuplicate community names in 2011 wellbeing data:")
duplicates_2011 = matched_cwb_2011[cwb_2011.duplicated("CSD Name 2011", keep=False)][
    "CSD Name 2011"
].value_counts()
print(duplicates_2011)

print("\nDuplicate community names in 2006 wellbeing data:")
duplicates_2006 = matched_cwb_2006[cwb_2006.duplicated("CSD Name 2006", keep=False)][
    "CSD Name 2006"
].value_counts()
print(duplicates_2006)


# %%
# save mathed dataframes to csv files in the data/processed folder
matched_cwb_2021.to_csv(
    os.path.join("..", "data", "processed", "matched_cwb_2021.csv"), index=False
)
matched_cwb_2016.to_csv(
    os.path.join("..", "data", "processed", "matched_cwb_2016.csv"), index=False
)
matched_cwb_2011.to_csv(
    os.path.join("..", "data", "processed", "matched_cwb_2011.csv"), index=False
)
matched_cwb_2006.to_csv(
    os.path.join("..", "data", "processed", "matched_cwb_2006.csv"), index=False
)

# %%
# merge matched_cwb_2021 with matched_cwb_2016 and matched_emissions on community name
# Clean up the wellbeing data and merge 2016 and 2021
wellbeing_2006_clean = matched_cwb_2006[
    [
        "CSD Name 2006",
        "CWB 2006",
        "Income 2006",
        "Education 2006",
        "Housing 2006",
        "Labour Force Activity 2006",
        "Census Population 2006",
    ]
].copy()
wellbeing_2011_clean = matched_cwb_2011[
    [
        "CSD Name 2011",
        "CWB 2011",
        "Income 2011",
        "Education 2011",
        "Housing 2011",
        "Labour Force Activity 2011",
        "Census Population 2011",
    ]
].copy()
wellbeing_2016_clean = matched_cwb_2016[
    [
        "CSD Name 2016",
        "CWB 2016",
        "Income 2016",
        "Education 2016",
        "Housing 2016",
        "Labour Force Activity 2016",
        "Census Population 2016",
    ]
].copy()
wellbeing_2021_clean = matched_cwb_2021[
    [
        "CSD Name 2021",
        "CWB 2021",
        "Income 2021",
        "Education 2021",
        "Housing 2021",
        "Labour Force Activity 2021",
        "Census Population 2021",
    ]
].copy()

# Rename for consistent merging
wellbeing_2006_clean = wellbeing_2006_clean.rename(
    columns={"CSD Name 2006": "Municipality_Name"}
)
wellbeing_2011_clean = wellbeing_2011_clean.rename(
    columns={"CSD Name 2011": "Municipality_Name"}
)
wellbeing_2016_clean = wellbeing_2016_clean.rename(
    columns={"CSD Name 2016": "Municipality_Name"}
)
wellbeing_2021_clean = wellbeing_2021_clean.rename(
    columns={"CSD Name 2021": "Municipality_Name"}
)

# Merge wellbeing data across years
wellbeing_combined = pd.merge(
    wellbeing_2021_clean, wellbeing_2016_clean, on="Municipality_Name", how="inner"
)
wellbeing_combined = pd.merge(
    wellbeing_combined, wellbeing_2011_clean, on="Municipality_Name", how="inner"
)
wellbeing_combined_2006 = pd.merge(
    wellbeing_combined, wellbeing_2006_clean, on="Municipality_Name", how="inner"
)

print(f"Wellbeing data merged: {len(wellbeing_combined)} communities")


# %%
print(wellbeing_combined)

# %%
# Calculate wellbeing changes
wellbeing_combined["cwb_percent_change"] = (
    (wellbeing_combined["CWB 2021"] - wellbeing_combined["CWB 2011"])
    / wellbeing_combined["CWB 2011"]
    * 100
)
wellbeing_combined["income_percent_change"] = (
    (wellbeing_combined["Income 2021"] - wellbeing_combined["Income 2011"])
    / wellbeing_combined["Income 2011"]
    * 100
)
wellbeing_combined["education_percent_change"] = (
    (wellbeing_combined["Education 2021"] - wellbeing_combined["Education 2011"])
    / wellbeing_combined["Education 2011"]
    * 100
)
wellbeing_combined["housing_percent_change"] = (
    (wellbeing_combined["Housing 2021"] - wellbeing_combined["Housing 2011"])
    / wellbeing_combined["Housing 2011"]
    * 100
)
wellbeing_combined["labour_percent_change"] = (
    (
        wellbeing_combined["Labour Force Activity 2021"]
        - wellbeing_combined["Labour Force Activity 2011"]
    )
    / wellbeing_combined["Labour Force Activity 2011"]
    * 100
)

print("Wellbeing percent changes calculated")

# %%
# there are no utility emissions for 2008, 2009 or 2011, only for 2007 and 2010, so we will calculate the percent change between 2007-2010 and 2017-2020

# Step 1: Calculate mean emissions between 2007-2010 for each municipality
utility_emissions_2007_2010 = (
    total_utility_emissions[
        (total_utility_emissions["YEAR"] == 2007)
        | (total_utility_emissions["YEAR"] == 2010)
    ]
    .groupby("ORG_NAME")["EMISSIONS NET IMPORTS (TCO2e)"]
    .mean()
    .reset_index()
)
utility_emissions_2007_2010.columns = [
    "Municipality_Name",
    "avg_utility_emissions_2007_2010",
]

# Step 2: Calculate mean emissions between 2017-2020 for each municipality
utility_emissions_2017_2020 = (
    total_utility_emissions[
        (total_utility_emissions["YEAR"] >= 2017)
        & (total_utility_emissions["YEAR"] <= 2020)
    ]
    .groupby("ORG_NAME")["EMISSIONS NET IMPORTS (TCO2e)"]
    .mean()
    .reset_index()
)
utility_emissions_2017_2020.columns = [
    "Municipality_Name",
    "avg_utility_emissions_2017_2020",
]

# Step 3: Merge the two periods and calculate percent change
utility_emissions_change = pd.merge(
    utility_emissions_2007_2010,
    utility_emissions_2017_2020,
    on="Municipality_Name",
    how="outer",
)

# Calculate percent change: ((new - old) / old) * 100
utility_emissions_change["utility_emissions_percent_change"] = (
    (
        utility_emissions_change["avg_utility_emissions_2017_2020"]
        - utility_emissions_change["avg_utility_emissions_2007_2010"]
    )
    / utility_emissions_change["avg_utility_emissions_2007_2010"]
) * 100

# Optional: Handle cases where 2007-2010 data is 0 or missing
utility_emissions_change["utility_emissions_percent_change"] = utility_emissions_change[
    "utility_emissions_percent_change"
].replace([np.inf, -np.inf], np.nan)

print("Emissions change summary:")
print(utility_emissions_change.head())
print(f"\nDataset shape: {utility_emissions_change.shape}")
print(
    f"Municipalities with data for both periods: {utility_emissions_change.dropna().shape[0]}"
)

# Step 4: Merge with wellbeing dataset
final_analysis_data = pd.merge(
    utility_emissions_change, wellbeing_combined, on="Municipality_Name", how="inner"
)

print(f"\nFinal merged dataset shape: {final_analysis_data.shape}")
print("\nFinal dataset columns:")
print(final_analysis_data.columns.tolist())

# Optional: Display some summary statistics
print("\nUtility emissions change statistics:")
print(final_analysis_data["utility_emissions_percent_change"].describe())

# %%
# Step 1: Calculate mean emissions between 2007-2010 for each municipality
transportation_emissions_2007_2010 = (
    total_transportation_emissions[
        (total_transportation_emissions["YEAR"] == 2007)
        | (total_transportation_emissions["YEAR"] == 2010)
    ]
    .groupby("ORG_NAME")["Emissions tCO2e"]
    .mean()
    .reset_index()
)
transportation_emissions_2007_2010.columns = [
    "Municipality_Name",
    "avg_transportation_emissions_2007_2010",
]

# Step 2: Calculate mean emissions between 2017-2020 for each municipality
transportation_emissions_2017_2020 = (
    total_transportation_emissions[
        (total_transportation_emissions["YEAR"] >= 2017)
        & (total_transportation_emissions["YEAR"] <= 2020)
    ]
    .groupby("ORG_NAME")["Emissions tCO2e"]
    .mean()
    .reset_index()
)
transportation_emissions_2017_2020.columns = [
    "Municipality_Name",
    "avg_transportation_emissions_2017_2020",
]

# Step 3: Merge the two periods and calculate percent change
transportation_emissions_change = pd.merge(
    transportation_emissions_2007_2010,
    transportation_emissions_2017_2020,
    on="Municipality_Name",
    how="outer",
)

# Calculate percent change: ((new - old) / old) * 100
transportation_emissions_change["transportation_emissions_percent_change"] = (
    (
        transportation_emissions_change["avg_transportation_emissions_2017_2020"]
        - transportation_emissions_change["avg_transportation_emissions_2007_2010"]
    )
    / transportation_emissions_change["avg_transportation_emissions_2007_2010"]
) * 100

# Optional: Handle cases where 2007-2010 data is 0 or missing
transportation_emissions_change["transportation_emissions_percent_change"] = (
    transportation_emissions_change["transportation_emissions_percent_change"].replace(
        [np.inf, -np.inf], np.nan
    )
)

print("Emissions change summary:")
print(transportation_emissions_change.head())
print(f"\nDataset shape: {transportation_emissions_change.shape}")
print(
    f"Municipalities with data for both periods: {transportation_emissions_change.dropna().shape[0]}"
)

# Step 4: Merge with wellbeing dataset
final_analysis_data = pd.merge(
    transportation_emissions_change,
    final_analysis_data,
    on="Municipality_Name",
    how="inner",
)

print(f"\nFinal merged dataset shape: {final_analysis_data.shape}")
print("\nFinal dataset columns:")
print(final_analysis_data.columns.tolist())

# Optional: Display some summary statistics
print("\nEmissions change statistics:")
print(final_analysis_data["transportation_emissions_percent_change"].describe())

# %%
# Calculate per capita emissions
# final_analysis_data['2012_total_emissions_per_capita'] = final_analysis_data['2012 total emissions tCO2e'] / final_analysis_data['Census Population 2011']
# final_analysis_data['2021_total_emissions_per_capita'] = final_analysis_data['2021 total emissions tCO2e'] / final_analysis_data['Census Population 2021']
# final_analysis_data['total_emissions_per_capita_change'] = ((final_analysis_data['2021_total_emissions_per_capita'] - final_analysis_data['2012_total_emissions_per_capita']) / final_analysis_data['2012_total_emissions_per_capita'] * 100)
final_analysis_data["population_percent_change"] = (
    (
        final_analysis_data["Census Population 2021"]
        - final_analysis_data["Census Population 2011"]
    )
    / final_analysis_data["Census Population 2011"]
    * 100
)

final_analysis_data.head()

# %%
# Set a larger figure size for better readability
plt.figure(figsize=(14, 8))

# Transpose (.T) the DataFrame so years are on the x-axis and plot
ax = relative_utility_emissions.T.plot(figsize=(14, 8), legend=False)

# Add a horizontal line at 1.0 to clearly show the 2007 baseline
ax.axhline(y=1.0, color="red", linestyle="--", label="2007 Baseline")

# Add labels and a title to make the plot understandable
ax.set_title("Change in Utility Emissions Relative to 2007")
ax.set_xlabel("Year")
ax.set_ylabel("Utility Emissions Relative to 2007")
# ax.legend()
plt.grid(True, linestyle="--", alpha=0.6)
plt.show()

# %%
# Set a larger figure size for better readability
plt.figure(figsize=(14, 8))

# Transpose (.T) the DataFrame so years are on the x-axis and plot
ax = relative_transportation_emissions.T.plot(figsize=(14, 8), legend=False)

# Add a horizontal line at 1.0 to clearly show the 2007 baseline
ax.axhline(y=1.0, color="red", linestyle="--", label="2007 Baseline")

# Add labels and a title to make the plot understandable
ax.set_title("Change in Transportation Emissions Relative to 2007")
ax.set_xlabel("Year")
ax.set_ylabel("Transportation Emissions Relative to 2007")
# ax.legend()
plt.grid(True, linestyle="--", alpha=0.6)
plt.show()


# %%
# Define decoupling function
def categorize_decoupling(emissions_change, wellbeing_change):
    if emissions_change < -0.5 and wellbeing_change > 0.5:
        return "em<0, wel>0"  # Best case: emissions down, wellbeing up
    elif (
        emissions_change > 0.5
        and wellbeing_change > 0.5
        and wellbeing_change > emissions_change
    ):
        return "em>0, wel>0, wel>em"  # Good: wellbeing growing faster than emissions
    elif (
        emissions_change < -0.5
        and wellbeing_change < -0.5
        and abs(wellbeing_change) < abs(emissions_change)
    ):
        return (
            "em<0, wel<0, abs(wel)<abs(em)"  # Emissions falling faster than wellbeing
        )
    elif (
        emissions_change > 0.5 and wellbeing_change > 0.5
    ) and wellbeing_change < emissions_change:
        return "em>0, wel>0, wel<em"  # Moving up but emissions growing faster than wellbeing
    elif (
        emissions_change < -0.5
        and wellbeing_change < -0.5
        and abs(wellbeing_change) > abs(emissions_change)
    ):
        return "em<0, wel<0, abs(wel)>abs(em)"  # Both down, but wellbeing falling faster than emissions
    elif (
        emissions_change < -0.5
        and wellbeing_change < -0.5
        and abs(emissions_change) > abs(wellbeing_change)
    ):
        return "em<0, wel<0, abs(em)>abs(wel)"  # Both down, but wellbeing falling faster than emissions
    elif emissions_change > 0.5 and wellbeing_change < -0.5:
        return "em>0, wel<0"  # Worst case: emissions up, wellbeing down
    else:
        return "Other"


# Apply decoupling categorization
# final_analysis_data['total_emissions_decoupling_type'] = final_analysis_data.apply(
#    lambda row: categorize_decoupling(row['Emissions_Percent_Change'], row['cwb_percent_change']), axis=1
# )

# final_analysis_data['total_emissions_per_capita_decoupling_type'] = final_analysis_data.apply(
#    lambda row: categorize_decoupling(row['total_emissions_per_capita_change'], row['cwb_percent_change']), axis=1
# )

# Repeat the decoupling categorization for transportation, utility and industrial emissions

final_analysis_data["transportation_emissions_decoupling_type"] = (
    final_analysis_data.apply(
        lambda row: categorize_decoupling(
            row["transportation_emissions_percent_change"], row["cwb_percent_change"]
        ),
        axis=1,
    )
)

final_analysis_data["utility_emissions_decoupling_type"] = final_analysis_data.apply(
    lambda row: categorize_decoupling(
        row["utility_emissions_percent_change"], row["cwb_percent_change"]
    ),
    axis=1,
)


# %% [markdown]
# average of two datapoints (2017 and 2020)
# em<0, wel>0                      78
# em>0, wel>0, wel<em              48
#
# average of four datapoints 2017, 2018, 2019, 2020
# em<0, wel>0                      82
# em>0, wel>0, wel<em              43
#

# %%
# Summary statistics for transportation emissions
print("=== DECOUPLING ANALYSIS SUMMARY ===")
print("\nTransportation Emissions vs Wellbeing:")
print(final_analysis_data["transportation_emissions_decoupling_type"].value_counts())

print(
    f"\nAverage transportation emissions change: {final_analysis_data['transportation_emissions_percent_change'].mean():.2f}%"
)
print(
    f"Average wellbeing change: {final_analysis_data['cwb_percent_change'].mean():.2f}%"
)

# Preview the merged data
print("\n=== SAMPLE OF MERGED DATA ===")
print(
    final_analysis_data[
        [
            "Municipality_Name",
            "transportation_emissions_percent_change",
            "cwb_percent_change",
            "transportation_emissions_decoupling_type",
        ]
    ].head(10)
)

# %%

# Summary statistics for utility emissions
print("=== DECOUPLING ANALYSIS SUMMARY ===")
print("\nUtility Emissions vs Wellbeing:")
print(final_analysis_data["utility_emissions_decoupling_type"].value_counts())

print(
    f"\nMean utility emissions change: {final_analysis_data['utility_emissions_percent_change'].mean():.2f}% and std: {final_analysis_data['utility_emissions_percent_change'].std():.2f}"
)
print(
    f"\nMean transportation emissions change: {final_analysis_data['transportation_emissions_percent_change'].mean():.2f}% and std: {final_analysis_data['transportation_emissions_percent_change'].std():.2f}"
)
print(
    f"\nMean population percent change: {final_analysis_data['population_percent_change'].mean():.2f}% and std: {final_analysis_data['population_percent_change'].std():.2f}"
)
print(
    f"\nMean Education percent change: {final_analysis_data['education_percent_change'].mean():.2f}% and std: {final_analysis_data['education_percent_change'].std():.2f}"
)
print(
    f"\nMean Income percent change: {final_analysis_data['income_percent_change'].mean():.2f}% and std: {final_analysis_data['income_percent_change'].std():.2f}"
)
print(
    f"\nMean Housing adequacy percent change: {final_analysis_data['housing_percent_change'].mean():.2f}% and std: {final_analysis_data['housing_percent_change'].std():.2f}"
)
print(
    f"\nMean Labour force participation percent change: {final_analysis_data['labour_percent_change'].mean():.2f}% and std: {final_analysis_data['labour_percent_change'].std():.2f}"
)
print(
    f"\nMean Wellbeing percent change: {final_analysis_data['cwb_percent_change'].mean():.2f}% and std: {final_analysis_data['cwb_percent_change'].std():.2f}"
)

# Preview the merged data
print("\n=== SAMPLE OF MERGED DATA ===")
print(
    final_analysis_data[
        [
            "Municipality_Name",
            "utility_emissions_percent_change",
            "cwb_percent_change",
            "utility_emissions_decoupling_type",
        ]
    ].head(10)
)

# %%
# Save for further analysis
final_analysis_data.to_csv(
    os.path.join(
        "..", "data", "processed", "emissions_wellbeing_decoupling_analysis.csv"
    ),
    index=False,
)
print("\nFinal dataset saved!")

# %%
# Create relative values (to 2011) for each metric
wellbeing_combined_2006["CWB_rel"] = (
    wellbeing_combined_2006["CWB 2021"] / wellbeing_combined_2006["CWB 2006"]
)
wellbeing_combined_2006["Income_rel"] = (
    wellbeing_combined_2006["Income 2021"] / wellbeing_combined_2006["Income 2006"]
)
wellbeing_combined_2006["Education_rel"] = (
    wellbeing_combined_2006["Education 2021"]
    / wellbeing_combined_2006["Education 2006"]
)
wellbeing_combined_2006["Housing_rel"] = (
    wellbeing_combined_2006["Housing 2021"] / wellbeing_combined_2006["Housing 2006"]
)
wellbeing_combined_2006["Labour_rel"] = (
    wellbeing_combined_2006["Labour Force Activity 2021"]
    / wellbeing_combined_2006["Labour Force Activity 2006"]
)
wellbeing_combined_2006["Population_rel"] = (
    wellbeing_combined_2006["Census Population 2021"]
    / wellbeing_combined_2006["Census Population 2006"]
)

# Plot for each community
for org_name in relative_transportation_emissions.index:
    fig, ax = plt.subplots(figsize=(10, 6))

    transportation_data = relative_transportation_emissions.loc[org_name]
    utility_data = relative_utility_emissions.loc[org_name]

    # Get relative wellbeing and subcategories
    rel_row = wellbeing_combined_2006[
        wellbeing_combined_2006["Municipality_Name"] == org_name
    ]
    if rel_row.empty:
        continue  # skip if not found

    ax.plot(
        transportation_data.index,
        transportation_data.values,
        label="Transportation Emissions",
        marker="x",
    )
    ax.plot(
        utility_data.index,
        utility_data.values,
        label="Utility Emissions",
        marker="o",
        color="green",
    )
    ax.plot(
        [2006, 2011, 2016, 2021],
        [
            1,
            rel_row["CWB 2011"].values[0] / rel_row["CWB 2006"].values[0],
            rel_row["CWB 2016"].values[0] / rel_row["CWB 2006"].values[0],
            rel_row["CWB_rel"].values[0],
        ],
        label="Wellbeing Index",
        marker="s",
        color="blue",
    )
    ax.plot(
        [2006, 2011, 2016, 2021],
        [
            1,
            rel_row["Income 2011"].values[0] / rel_row["Income 2006"].values[0],
            rel_row["Income 2016"].values[0] / rel_row["Income 2006"].values[0],
            rel_row["Income_rel"].values[0],
        ],
        label="Income",
        marker="^",
        color="orange",
    )
    ax.plot(
        [2006, 2011, 2016, 2021],
        [
            1,
            rel_row["Education 2011"].values[0] / rel_row["Education 2006"].values[0],
            rel_row["Education 2016"].values[0] / rel_row["Education 2006"].values[0],
            rel_row["Education_rel"].values[0],
        ],
        label="Education",
        marker="v",
        color="purple",
    )
    ax.plot(
        [2006, 2011, 2016, 2021],
        [
            1,
            rel_row["Labour Force Activity 2011"].values[0]
            / rel_row["Labour Force Activity 2006"].values[0],
            rel_row["Labour Force Activity 2016"].values[0]
            / rel_row["Labour Force Activity 2006"].values[0],
            rel_row["Labour_rel"].values[0],
        ],
        label="Labour Force",
        marker="d",
        color="brown",
    )
    ax.plot(
        [2006, 2011, 2016, 2021],
        [
            1,
            rel_row["Housing 2011"].values[0] / rel_row["Housing 2006"].values[0],
            rel_row["Housing 2016"].values[0] / rel_row["Housing 2006"].values[0],
            rel_row["Housing_rel"].values[0],
        ],
        label="Housing",
        marker="*",
        color="pink",
    )
    ax.plot(
        [2006, 2011, 2016, 2021],
        [
            1,
            rel_row["Census Population 2011"].values[0]
            / rel_row["Census Population 2006"].values[0],
            rel_row["Census Population 2016"].values[0]
            / rel_row["Census Population 2006"].values[0],
            rel_row["Population_rel"].values[0],
        ],
        label="Population",
        marker=".",
        color="grey",
    )

    ax.axhline(y=1.0, color="red", linestyle="--")
    ax.set_title(org_name)
    ax.set_xlabel("Year")
    ax.set_ylabel("Relative Value (to 2011)")
    ax.legend(loc="upper left", bbox_to_anchor=(1, 1))
    ax.set_ylim(bottom=0)
    ax.set_ylim(top=3)
    plt.tight_layout()
    plt.show()

# %%
import seaborn as sns

# plot population level in 2021 vs whether the community is decoupling or not
plt.figure(figsize=(12, 6))
sns.boxplot(
    x="transportation_emissions_decoupling_type",
    y="Census Population 2021",
    data=final_analysis_data,
)
plt.title(
    "Population Level in 2021 by Decoupling Type (total transportation emissions change (2012 - 2021) vs. wellbeing change, 2011-2021)"
)
plt.xlabel("Decoupling Type")
plt.ylabel("Population Level (2021)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# %%

# plot population level in 2021 vs whether the community is decoupling or not
plt.figure(figsize=(12, 6))
sns.boxplot(
    x="utility_emissions_decoupling_type",
    y="Census Population 2021",
    data=final_analysis_data,
)
plt.title(
    "Population Level in 2021 by Decoupling Type (total utility emissions change (2012-2021) vs. wellbeing change (2011-2021))"
)
plt.xlabel("Decoupling Type")
plt.ylabel("Population Level (2021)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# %%
# get coordinates of each city in the bc-gazetteer-2024-06-13.csv file in the raw data folder
gazeteer = pd.read_csv(os.path.join("..", "data", "raw", "bc-gazetteer-2024-06-13.csv"))
# Filter for communities in the final analysis data
gazeteer_filtered = gazeteer[
    gazeteer["Official Name"].isin(final_analysis_data["Municipality_Name"])
    & gazeteer["Feature Type"].isin(
        [
            "City",
            "Town",
            "District Municipality",
            "District Municipality (1)",
            "Village (1)",
            "Resort Municipality",
            "Mountain Resort Municipality",
        ]
    )
]


# %%
# print all unique official names in the gazeteer_filtered dataframe
print("Unique official names in gazeteer_filtered:")
print(gazeteer_filtered["Official Name"].unique())
# count unique official names
print(
    f"Total unique official names in gazeteer_filtered: {gazeteer_filtered['Official Name'].nunique()}"
)
# figure out which communities are missing coordinates
missing_coordinates = final_analysis_data[
    ~final_analysis_data["Municipality_Name"].isin(gazeteer_filtered["Official Name"])
]
print(f"Communities missing coordinates: {len(missing_coordinates)}")
print("Missing communities:")
for community in missing_coordinates["Municipality_Name"].unique():
    print(f"  {community}")

# %%
# Manual mapping for missing communities using both name and feature type
name_featuretype_corrections = {
    "Langley City": ("Langley", "City"),
    "Langley Township": ("Langley", "District Municipality (1)"),
    "North Vancouver City": ("North Vancouver", "City"),
    "North Vancouver District": ("North Vancouver", "District Municipality (1)"),
    "One Hundred Mile House": ("100 Mile House", "District Municipality (1)"),
    "Sun Peaks Mountain Resort": ("Sun Peaks", "Mountain Resort Municipality"),
    "West Kelowna": ("West Kelowna, City of", "City"),
    "Queen Charlotte": ("Queen Charlotte", "Post Office"),
    "Sechelt IGD": ("Sechelt Indian Government District", "Indian Government District"),
    "Northern Rockies": (
        "Northern Rockies Regional Municipality",
        "District Municipality (1)",
    ),
}

missing_coords = []
for community, (gaz_name, feature_type) in name_featuretype_corrections.items():
    if feature_type:
        match = gazeteer[
            (gazeteer["Official Name"].str.lower() == gaz_name.lower())
            & (gazeteer["Feature Type"].str.lower() == feature_type.lower())
        ]
    else:
        match = gazeteer[gazeteer["Official Name"].str.lower() == gaz_name.lower()]
    if not match.empty:
        feature_type = match.iloc[0]["Feature Type"]
        lat = match.iloc[0]["LatDD"]
        lon = match.iloc[0]["LongDD"]
        datum = match.iloc[0]["Datum"]
        missing_coords.append(
            {
                "Official Name": community,
                "Feature Type": feature_type,
                "Datum": datum,
                "LatDD": lat,
                "LongDD": lon,
            }
        )
    else:
        print(f"Not found in gazeteer: {community} -> {gaz_name} ({feature_type})")

missing_coords_df = pd.DataFrame(missing_coords)
print(missing_coords_df)

# %%
# add missing communities to gazeteer_filtered
gazeteer_filtered = pd.concat([gazeteer_filtered, missing_coords_df]).reset_index(
    drop=True
)
gazeteer_filtered.head()
# gazeteer_filtered.tail(20)

# %%
gazeteer_filtered.tail(2)

# %%
# check if the gazeteer_filtered dataframe has all the communities from final_analysis_data
print(
    f"Total communities in final_analysis_data: {len(final_analysis_data['Municipality_Name'].unique())}"
)
print(
    f"Total communities in gazeteer_filtered: {len(gazeteer_filtered['Official Name'].unique())}"
)
missing_communities = set(gazeteer_filtered["Official Name"].unique()) - set(
    final_analysis_data["Municipality_Name"].unique()
)
print(f"Missing communities in gazeteer_filtered: {len(missing_communities)}")
if missing_communities:
    print("Missing communities:")
    for community in missing_communities:
        print(f"  {community}")

# %%
# find duplicates
duplicates = gazeteer_filtered[
    gazeteer_filtered.duplicated(subset=["Official Name"], keep=False)
]
print(f"Total duplicates found: {len(duplicates)}")
if not duplicates.empty:
    print("Duplicate entries:")
    for index, row in duplicates.iterrows():
        print(f"  {row['Official Name']} (Index: {index})")


# %%
# extract official name, feature type, datum, latitude and longitude from gazeteer_filtered
gazeteer_final = gazeteer_filtered[
    ["Official Name", "Feature Type", "Datum", "LatDD", "LongDD"]
].copy()
gazeteer_final.rename(
    columns={
        "Official Name": "Municipality_Name",
        "Feature Type": "Feature_Type",
        "Datum": "Datum",
        "LatDD": "Latitude",
        "LongDD": "Longitude",
    },
    inplace=True,
)
# Save the gazeteer_final dataframe to a CSV file in the processed data folder
gazeteer_final.to_csv(
    os.path.join("..", "data", "processed", "gazeteer_final.csv"), index=False
)

# %%
gazeteer_final.head(2)

# %%
# merge the gazeteer data with the final_analysis_data
final_analysis_data_with_coords = pd.merge(
    final_analysis_data, gazeteer_final, on="Municipality_Name"
)
# Save the final analysis data with coordinates to a CSV file in the processed data folder
final_analysis_data_with_coords.to_csv(
    os.path.join("..", "data", "processed", "final_analysis_data_with_coords.csv"),
    index=False,
)
# Display the final analysis data with coordinates
print("Final analysis data with coordinates:")
print(final_analysis_data_with_coords.head())

# %%
# plot the final analysis data with coordinates on a map of BC, with shapefile located in the raw dataset subfolder BC_Boundary as BC_Boundary.shp
import geopandas as gpd

# Load the shapefile for BC boundaries
bc_boundaries = gpd.read_file(
    os.path.join("..", "data", "raw", "BC_Boundary", "BC_Boundary.shp")
)
# Convert the final analysis data with coordinates to a GeoDataFrame
final_analysis_gdf = gpd.GeoDataFrame(
    final_analysis_data_with_coords,
    geometry=gpd.points_from_xy(
        final_analysis_data_with_coords["Longitude"],
        final_analysis_data_with_coords["Latitude"],
    ),
    crs="EPSG:4326",  # WGS84 coordinate system
)

decoupling_colors = {
    "em<0, wel>0": "green",
    "em>0, wel>0, wel>em": "blue",
    "em>0, wel>0, wel<em": "orange",
    "em<0, wel<0, abs(wel)<abs(em)": "purple",
    "em<0, wel<0, abs(wel)>abs(em)": "pink",
    "em>0, wel<0": "red",
    "Other": "black",  # Default color for any other cases
}


final_analysis_gdf["color"] = final_analysis_gdf[
    "utility_emissions_decoupling_type"
].map(decoupling_colors)

plt.figure(figsize=(12, 12))
bc_boundaries.plot(ax=plt.gca(), color="lightgrey", edgecolor="black")
# plot the map with legend showing each color based on decoupling type
final_analysis_gdf.plot(
    ax=plt.gca(),
    marker="o",
    color=final_analysis_gdf["color"],
    markersize=15,
    label="Communities",
)
# Create a custom legend
handles = [
    plt.Line2D(
        [0],
        [0],
        marker="o",
        color="w",
        markerfacecolor=color,
        markersize=10,
        label=label,
    )
    for label, color in decoupling_colors.items()
]
plt.legend(handles=handles, title="Decoupling Type", loc="upper right")

plt.title(
    "Communities in BC with Decoupling Types (utility emissions change (2007-2010 to 2017-2020) vs. wellbeing change (2011-2021))"
)
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.grid()
plt.tight_layout()
plt.show()

# %%
final_analysis_gdf["color"] = final_analysis_gdf[
    "transportation_emissions_decoupling_type"
].map(decoupling_colors)

plt.figure(figsize=(12, 12))
bc_boundaries.plot(ax=plt.gca(), color="lightgrey", edgecolor="black")
# plot the map with legend showing each color based on decoupling type
final_analysis_gdf.plot(
    ax=plt.gca(),
    marker="o",
    color=final_analysis_gdf["color"],
    markersize=15,
    label="Communities",
)
# Create a custom legend
handles = [
    plt.Line2D(
        [0],
        [0],
        marker="o",
        color="w",
        markerfacecolor=color,
        markersize=10,
        label=label,
    )
    for label, color in decoupling_colors.items()
]
plt.legend(handles=handles, title="Decoupling Type", loc="upper right")

plt.title(
    "Communities in BC with Decoupling Types (transportation emissions change (2012-2021) vs. wellbeing change (2011-2021))"
)
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.grid()
plt.tight_layout()
plt.show()

# %%
# Find name of communities in the worse case scenario of transportation emissions decoupling
worse_case_communities = final_analysis_gdf[
    final_analysis_gdf["transportation_emissions_decoupling_type"] == "em>0, wel<0"
]
print(
    worse_case_communities["Municipality_Name"],
    worse_case_communities["transportation_emissions_percent_change"],
    worse_case_communities["cwb_percent_change"],
    worse_case_communities["Census Population 2011"],
)


# %%
# Find name of communities in the worse case scenario of utility emissions decoupling
worse_case_communities = final_analysis_gdf[
    final_analysis_gdf["utility_emissions_decoupling_type"] == "em>0, wel<0"
]
print(
    worse_case_communities["Municipality_Name"],
    worse_case_communities["utility_emissions_percent_change"],
    worse_case_communities["cwb_percent_change"],
    worse_case_communities["Census Population 2011"],
)


# %%

# Create figure with subplots
fig, axes = plt.subplots(2, 2, figsize=(16, 14))

# Calculate total emissions change (you might want to weight this differently)
# Option 1: Simple average
final_analysis_data["total_emissions_percent_change"] = (
    final_analysis_data["transportation_emissions_percent_change"]
    + final_analysis_data["utility_emissions_percent_change"]
) / 2

# Create population size categories for coloring
final_analysis_data["pop_category"] = pd.cut(
    final_analysis_data["Census Population 2021"],
    bins=[0, 2000, 10000, 50000, float("inf")],
    labels=["<2,000", "2,000-10,000", "10,000-50,000", ">50,000"],
)

# Color map for population categories
colors = {
    "<2,000": "red",
    "2,000-10,000": "orange",
    "10,000-50,000": "blue",
    ">50,000": "green",
}

# Normalize population for point sizes
pop_sizes = (
    final_analysis_data["Census Population 2021"]
    / final_analysis_data["Census Population 2021"].max()
) * 300 + 20

# ========== PLOT 1: Total Emissions vs CWB ==========
ax1 = axes[0, 0]

for category in final_analysis_data["pop_category"].unique():
    if pd.notna(category):
        mask = final_analysis_data["pop_category"] == category
        ax1.scatter(
            final_analysis_data.loc[mask, "total_emissions_percent_change"],
            final_analysis_data.loc[mask, "cwb_percent_change"],
            s=pop_sizes[mask],
            alpha=0.6,
            c=colors[category],
            label=f"{category} people",
            edgecolors="black",
            linewidth=0.5,
        )

# Add quadrant lines
ax1.axhline(y=0, color="black", linestyle="-", linewidth=0.8, alpha=0.5)
ax1.axvline(x=0, color="black", linestyle="-", linewidth=0.8, alpha=0.5)

# Add shaded quadrants
ax1.axhspan(
    0, ax1.get_ylim()[1], xmin=0, xmax=0.5, alpha=0.1, color="red"
)  # top left - best case
ax1.axhspan(
    ax1.get_ylim()[0], 0, xmin=0.5, xmax=1, alpha=0.1, color="darkred"
)  # bottom right - worst case

# Label outliers
threshold_emissions = 50  # Adjust based on your data
threshold_wellbeing = 10
for idx, row in final_analysis_data.iterrows():
    if (
        abs(row["total_emissions_percent_change"]) > threshold_emissions
        or abs(row["cwb_percent_change"]) > threshold_wellbeing
    ):
        ax1.annotate(
            row["Municipality_Name"],
            (row["total_emissions_percent_change"], row["cwb_percent_change"]),
            fontsize=7,
            alpha=0.7,
            xytext=(5, 5),
            textcoords="offset points",
        )

ax1.set_xlabel("Total Emissions Change (%)", fontsize=12)
ax1.set_ylabel("Community Wellbeing Change (%)", fontsize=12)
ax1.set_title("Total Emissions vs Wellbeing Changes", fontsize=14, fontweight="bold")
ax1.legend(title="Population Size", loc="best", framealpha=0.9)
ax1.grid(True, alpha=0.3)
ax1.set_xlim(-300, 300)
ax1.set_ylim(-300, 300)

# Add quadrant labels
ax1.text(
    0.02,
    0.98,
    "BEST:\nDecoupling",
    transform=ax1.transAxes,
    fontsize=9,
    verticalalignment="top",
    fontweight="bold",
    color="green",
)
ax1.text(
    0.98,
    0.02,
    "WORST:\nLosing on\nboth fronts",
    transform=ax1.transAxes,
    fontsize=9,
    ha="right",
    fontweight="bold",
    color="darkred",
)

# ========== PLOT 2: Transportation vs CWB ==========
ax2 = axes[0, 1]

scatter2 = ax2.scatter(
    final_analysis_data["transportation_emissions_percent_change"],
    final_analysis_data["cwb_percent_change"],
    s=pop_sizes,
    c=final_analysis_data["Census Population 2021"],
    cmap="viridis",
    alpha=0.6,
    edgecolors="black",
    linewidth=0.5,
)

ax2.axhline(y=0, color="black", linestyle="-", linewidth=0.8, alpha=0.5)
ax2.axvline(x=0, color="black", linestyle="-", linewidth=0.8, alpha=0.5)

ax2.set_xlabel("Transportation Emissions Change (%)", fontsize=12)
ax2.set_ylabel("Community Wellbeing Change (%)", fontsize=12)
ax2.set_title("Transportation Emissions vs Wellbeing", fontsize=14, fontweight="bold")
ax2.grid(True, alpha=0.3)
ax2.set_xlim(-300, 300)
ax2.set_ylim(-300, 300)

# Add colorbar for population
cbar2 = plt.colorbar(scatter2, ax=ax2)
cbar2.set_label("Population (2021)", fontsize=10)

# ========== PLOT 3: Utility vs CWB ==========
ax3 = axes[1, 0]

scatter3 = ax3.scatter(
    final_analysis_data["utility_emissions_percent_change"],
    final_analysis_data["cwb_percent_change"],
    s=pop_sizes,
    c=final_analysis_data["Census Population 2021"],
    cmap="plasma",
    alpha=0.6,
    edgecolors="black",
    linewidth=0.5,
)

ax3.axhline(y=0, color="black", linestyle="-", linewidth=0.8, alpha=0.5)
ax3.axvline(x=0, color="black", linestyle="-", linewidth=0.8, alpha=0.5)

ax3.set_xlabel("Utility Emissions Change (%)", fontsize=12)
ax3.set_ylabel("Community Wellbeing Change (%)", fontsize=12)
ax3.set_title("Utility Emissions vs Wellbeing", fontsize=14, fontweight="bold")
ax3.grid(True, alpha=0.3)
ax3.set_xlim(-300, 300)
ax3.set_ylim(-300, 300)

# Add colorbar
cbar3 = plt.colorbar(scatter3, ax=ax3)
cbar3.set_label("Population (2021)", fontsize=10)

# ========== PLOT 4: Comparison Plot ==========
ax4 = axes[1, 1]

# Plot both types on same axes with different markers
ax4.scatter(
    final_analysis_data["transportation_emissions_percent_change"],
    final_analysis_data["cwb_percent_change"],
    s=30,
    alpha=0.5,
    c="blue",
    label="Transportation",
    marker="o",
)
ax4.scatter(
    final_analysis_data["utility_emissions_percent_change"],
    final_analysis_data["cwb_percent_change"],
    s=30,
    alpha=0.5,
    c="green",
    label="Utility",
    marker="^",
)

ax4.axhline(y=0, color="black", linestyle="-", linewidth=0.8, alpha=0.5)
ax4.axvline(x=0, color="black", linestyle="-", linewidth=0.8, alpha=0.5)

ax4.set_xlabel("Emissions Change (%)", fontsize=12)
ax4.set_ylabel("Community Wellbeing Change (%)", fontsize=12)
ax4.set_title(
    "Transportation vs Utility Emissions Comparison", fontsize=14, fontweight="bold"
)
ax4.legend(loc="best")
ax4.grid(True, alpha=0.3)
ax4.set_xlim(-300, 300)
ax4.set_ylim(-300, 300)

plt.suptitle(
    "B.C. Municipalities: Emissions-Wellbeing Decoupling Analysis (2007-10 to 2017-20)",
    fontsize=16,
    fontweight="bold",
    y=1.02,
)
plt.tight_layout()
plt.show()

# ========== PRINT ANALYSIS ==========
print("\n" + "=" * 60)
print("DECOUPLING ANALYSIS SUMMARY")
print("=" * 60)

# Remove NaN values for analysis
clean_data = final_analysis_data.dropna(
    subset=["total_emissions_percent_change", "cwb_percent_change"]
)
print(f"\nTotal municipalities analyzed: {len(clean_data)}")

# Calculate quadrants
strong_decoupling = clean_data[
    (clean_data["total_emissions_percent_change"] < 0)
    & (clean_data["cwb_percent_change"] > 0)
]
growth_coupled = clean_data[
    (clean_data["total_emissions_percent_change"] > 0)
    & (clean_data["cwb_percent_change"] > 0)
]
decline_coupled = clean_data[
    (clean_data["total_emissions_percent_change"] < 0)
    & (clean_data["cwb_percent_change"] < 0)
]
worst_case = clean_data[
    (clean_data["total_emissions_percent_change"] > 0)
    & (clean_data["cwb_percent_change"] < 0)
]

print(f"\n{'Quadrant':<30} {'Count':>10} {'Percentage':>10}")
print("-" * 50)
print(
    f"{'Strong Decoupling (↓E, ↑W)':<30} {len(strong_decoupling):>10} {len(strong_decoupling) / len(clean_data) * 100:>9.1f}%"
)
print(
    f"{'Growth Coupled (↑E, ↑W)':<30} {len(growth_coupled):>10} {len(growth_coupled) / len(clean_data) * 100:>9.1f}%"
)
print(
    f"{'Decline Coupled (↓E, ↓W)':<30} {len(decline_coupled):>10} {len(decline_coupled) / len(clean_data) * 100:>9.1f}%"
)
print(
    f"{'Worst Case (↑E, ↓W)':<30} {len(worst_case):>10} {len(worst_case) / len(clean_data) * 100:>9.1f}%"
)

# Statistics by emissions type
print("\n" + "-" * 50)
print("EMISSIONS CHANGE STATISTICS")
print("-" * 50)
print(f"\n{'Metric':<25} {'Mean':>10} {'Median':>10} {'Std Dev':>10}")
print("-" * 50)
print(
    f"{'Total Emissions':<25} {clean_data['total_emissions_percent_change'].mean():>10.1f}% {clean_data['total_emissions_percent_change'].median():>10.1f}% {clean_data['total_emissions_percent_change'].std():>10.1f}%"
)
print(
    f"{'Transportation':<25} {clean_data['transportation_emissions_percent_change'].mean():>10.1f}% {clean_data['transportation_emissions_percent_change'].median():>10.1f}% {clean_data['transportation_emissions_percent_change'].std():>10.1f}%"
)
print(
    f"{'Utility':<25} {clean_data['utility_emissions_percent_change'].mean():>10.1f}% {clean_data['utility_emissions_percent_change'].median():>10.1f}% {clean_data['utility_emissions_percent_change'].std():>10.1f}%"
)
print(
    f"{'Wellbeing (CWB)':<25} {clean_data['cwb_percent_change'].mean():>10.1f}% {clean_data['cwb_percent_change'].median():>10.1f}% {clean_data['cwb_percent_change'].std():>10.1f}%"
)

# Correlation analysis
print("\n" + "-" * 50)
print("CORRELATION ANALYSIS")
print("-" * 50)
corr_total = clean_data["total_emissions_percent_change"].corr(
    clean_data["cwb_percent_change"]
)
corr_transport = clean_data["transportation_emissions_percent_change"].corr(
    clean_data["cwb_percent_change"]
)
corr_utility = clean_data["utility_emissions_percent_change"].corr(
    clean_data["cwb_percent_change"]
)

print(f"Total Emissions vs Wellbeing:         {corr_total:.3f}")
print(f"Transportation Emissions vs Wellbeing: {corr_transport:.3f}")
print(f"Utility Emissions vs Wellbeing:        {corr_utility:.3f}")

# Worst performers detail
if len(worst_case) > 0:
    print("\n" + "-" * 50)
    print("MUNICIPALITIES IN WORST CASE QUADRANT")
    print("-" * 50)
    worst_sorted = worst_case.sort_values("cwb_percent_change")
    for _, row in worst_sorted.iterrows():
        print(f"\n{row['Municipality_Name']}:")
        print(f"  Population: {row['Census Population 2021']:,.0f}")
        print(f"  Wellbeing Change: {row['cwb_percent_change']:.1f}%")
        print(f"  Total Emissions Change: {row['total_emissions_percent_change']:.1f}%")
        print(
            f"  (Transport: {row['transportation_emissions_percent_change']:.1f}%, Utility: {row['utility_emissions_percent_change']:.1f}%)"
        )

# Best performers
if len(strong_decoupling) > 0:
    print("\n" + "-" * 50)
    print("TOP 5 STRONG DECOUPLING MUNICIPALITIES")
    print("-" * 50)
    # Sort by combination of wellbeing increase and emissions decrease
    strong_decoupling["decoupling_score"] = (
        strong_decoupling["cwb_percent_change"]
        - strong_decoupling["total_emissions_percent_change"]
    )
    best_sorted = strong_decoupling.nlargest(5, "decoupling_score")
    for _, row in best_sorted.iterrows():
        print(f"\n{row['Municipality_Name']}:")
        print(f"  Population: {row['Census Population 2021']:,.0f}")
        print(f"  Wellbeing Change: {row['cwb_percent_change']:.1f}%")
        print(f"  Total Emissions Change: {row['total_emissions_percent_change']:.1f}%")
