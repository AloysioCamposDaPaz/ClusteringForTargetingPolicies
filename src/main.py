# In your main script/notebook
import pandas as pd
import data_loader
import processing

# 1. Load all raw data
transport_raw = data_loader.load_transport_emissions(
    "data/raw/bc_on_road_transportation_data_at_the_community_level.csv"
)
utility_raw = data_loader.load_utility_emissions("data/raw/utilities_new.csv")
cwb_2006_raw = data_loader.load_cwb_data("data/raw/CWB_2006.csv")
cwb_2011_raw = data_loader.load_cwb_data("data/raw/CWB_2011.csv")
cwb_2016_raw = data_loader.load_cwb_data("data/raw/CWB_2016.csv")
cwb_2021_raw = data_loader.load_cwb_data("data/raw/CWB_2021.csv")

# 2. Process each raw dataframe into a tidy format
tidy_transport = processing.process_transport_emissions(transport_raw)
tidy_utility = processing.process_utility_emissions(utility_raw)
tidy_cwb_2006 = processing.process_cwb_data(cwb_2006_raw, 2006)
tidy_cwb_2011 = processing.process_cwb_data(cwb_2011_raw, 2011)
tidy_cwb_2016 = processing.process_cwb_data(cwb_2016_raw, 2016)
tidy_cwb_2021 = processing.process_cwb_data(cwb_2021_raw, 2021)

# 3. Concatenate all tidy dataframes into the master file
master_df = pd.concat(
    [
        tidy_transport,
        tidy_utility,
        tidy_cwb_2006,
        tidy_cwb_2011,
        tidy_cwb_2016,
        tidy_cwb_2021,
    ],
    ignore_index=True,
)

# 4. Perform final global cleaning (e.g., standardizing municipality names)
# name_map = {'Burnaby City': 'Burnaby', ...}
# master_df['Municipality'] = master_df['Municipality'].replace(name_map)
# master_df.dropna(subset=['Value'], inplace=True) # Drop rows where conversion to numeric failed

# 5. Save the final, precious tidy dataframe
master_df.to_csv("data/processed/master_timeseries_data.csv", index=False)

print("Master tidy dataframe created successfully!")
print(master_df.head())
