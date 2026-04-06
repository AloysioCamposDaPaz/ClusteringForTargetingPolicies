# %%
# import tidy all data csv file
import os
import pandas as pd
import numpy as np

tidy_all_data = pd.read_csv(
    os.path.join("..", "..", "data", "processed", "tidy_all_metrics.csv")
)


# %%
tidy_all_data[tidy_all_data["Year"] == 2007].tail()

# %%
# choose reference year and metric list (edit to taste)
REFERENCE_YEAR = 2021


all_key_features = [
    # Context
    "Remoteness",
    "Latitude",
    "Longitude",
    # Climate action
    "Climate_Action_N_Barriers",
    "Climate_Action_Score",
    # Socio-economic baseline
    "Log_Population",
    "Income",
    "Education",
    "Housing",
    "Labour_Force",  #'CWB',
    # Socio-economic trajectories
    "Income_Percent_Change",
    "Education_Percent_Change",
    "Housing_Percent_Change",
    "Labour_Percent_Change",
    "Log_Population_Change_2006_2021",
    # Low-emissions energy shares baseline
    "Utility_Residential_Electricity_Energy_Share",
    "Utility_CSMI_Electricity_Energy_Share",
    "Transportation_Low_Emission_Vehicle_km_Travelled_Share",
    # Economic structure baseline
    "Utility_CSMI_Total_Energy_Share",  # this is share on total utility enery, not including tranport
    # Energy transition trajectories
    "Residential_Electricity_Share_Percent_Change",
    "CSMI_Electricity_Share_Percent_Change",
    "Transport_Low_Emission_Share_Percent_Change",
    # Economic transition trajectories
    "CSMI_Total_Energy_Share_Percent_Change",
    # Per capita values for 2021
    "Log_Transportation_Low_Emission_Vehicle_km_Travelled_Per_Capita",
    "Log_Transportation_Polluting_Vehicle_km_Travelled_Per_Capita",
    "Log_Residential_Electricity_Per_Capita",
    "Log_Residential_Polluting_Per_Capita",
    "Log_CSMI_Electricity_Per_Capita",
    "Log_CSMI_Polluting_Per_Capita",
    # Per capita changes 2007-2021 (pop from 2006 as a proxy for 2007)
    "Log_Diff_Transportation_Low_Emission_Vehicle_km_Travelled_Per_Capita",
    "Log_Diff_Transportation_Polluting_Vehicle_km_Travelled_Per_Capita",
    "Log_Diff_Residential_Electricity_Per_Capita",
    "Log_Diff_Residential_Polluting_Per_Capita",
    "Log_Diff_CSMI_Electricity_Per_Capita",
    "Log_Diff_CSMI_Polluting_Per_Capita",
    # Emission factor end year levels
    #'Log_Utility_Residential_Electricity_Emissions_Factor', #-> everyone has the same emissions factor because everyone is connected to the same grid
    "Log_Utility_Residential_Polluting_Emissions_Factor",
    #'Log_Utility_CSMI_Electricity_Emissions_Factor', #-> everyone has the same emissions factor because everyone is connected to the same grid
    #'Log_Utility_CSMI_Polluting_Emissions_Factor', #-> not estimated due to zero divided by zero
    "Log_Transport_Low_Emission_Emissions_Factor",
    "Log_Transport_Polluting_Emissions_Factor",
    # Emission factor changes 2007-2021
    #'Log_Diff_Utility_Residential_Electricity_Emissions_Factor', #-> everyone has the same difference because everyone is connected to the same grid
    "Log_Diff_Utility_Residential_Polluting_Emissions_Factor",
    #'Log_Diff_Utility_CSMI_Electricity_Emissions_Factor', -> #everyone has the same difference because everyone is connected to the same grid
    #'Log_Diff_Utility_CSMI_Polluting_Emissions_Factor', -> not estimated due to zero divided by zero
    "Log_Diff_Transport_Low_Emission_Emissions_Factor",
    "Log_Diff_Transport_Polluting_Emissions_Factor",
]

low_emission_transport_policy = [
    "Remoteness",  # more remote communities may need to travel further distances and have more range anxiety with EVs (but hybrids have better milage though)
    "Income",  # income affects the ability to purchase EVs or hybrids since their upfront cost can be higher
    "Income_Percent_Change",  # incomes trends (e.g. declines) could lead people to prioritize purchasing other things instead of EVs/hybrids
    "Housing",  # housing quality and quantity affects one's ability to charge their EV (apartments have more difficulty installing chargers, and housing needing maintenance may not have proper infrastructure to install chargers either)
    "Housing_Percent_Change",  # housing quality/quantity trends
    "Log_Residential_Electricity_Per_Capita",  # home electrification level important as people often charge EVs at home
    "Log_Transportation_Low_Emission_Vehicle_km_Travelled_Per_Capita",  # current levels of EVs/hybrids -> social signaling of EVs/Hybrid vehicles could create cultures of acceptance of EV/hybrids
    # change to private polluting vehicle km travelled
    # 'Log_Transportation_Polluting_Vehicle_km_Travelled_Per_Capita', # current levels of polluting vehicles -> social signaling of polluting vehicles could create cultures of rejection of EV/hybrids. Furthermore, stock of polluting vehicles can get moved around as people sell second hand cars
    "Log_Diff_Transportation_Low_Emission_Vehicle_km_Travelled_Per_Capita",  # is the number of hybdrids/EVs already increasing in this place?
    # change to private polluting vehicle
    #'Log_Diff_Transportation_Polluting_Vehicle_km_Travelled_Per_Capita', # is the number of polluting vehicles increasing/decreasing?
    "Log_Transport_Low_Emission_Emissions_Factor",  # is the numher of EVs higher than hybrids?
    "Log_Transport_Polluting_Emissions_Factor",  # how polluting are the polluting vehicles?
    "Log_Diff_Transport_Low_Emission_Emissions_Factor",  # are EVs outpacing hybrids over time?
    # change to private polluting vehicle
    #'Log_Diff_Transport_Polluting_Emissions_Factor' # are very polluting vehicles outpacing midly polluting vehicles over time?
]

residential_electrification_policy = [
    "Latitude",  # proxy for different temperatures north/south
    "Income",  # income affects ability to purchase heatpumps
    "Housing",  # housing quality and availability affects ability to install heatpumps
    "Education",  # education may affect ability to navigate installing heatpumps and also signal more progressive communities that are more likely to adopt heatpumps
    "Labour_Force",  # labour force affects ability to do renovations to install heatpumps
    "Log_Population",
    "Remoteness",
    # Socio-economic trajectories
    "Income_Percent_Change",
    "Education_Percent_Change",
    "Housing_Percent_Change",
    "Labour_Percent_Change",
    "Log_Population_Change_2006_2021",
    # Climate action
    "Climate_Action_N_Barriers",
    "Climate_Action_Score",
    #'Log_Residential_Electricity_Per_Capita', # Electricity use at homes important as heatpumps are electric
    #'Log_Residential_Polluting_Per_Capita', # Polluting energy use at homes important to signal places needing to transition
    #'Log_Diff_Residential_Electricity_Per_Capita', # Electricity changes at homes important as heatpumps are electric
    #'Log_Diff_Residential_Polluting_Per_Capita',  # Polluting energy changes use at homes important to signal places already transitioning or starting to use even more polluting energy
    # If we want to use aggregate per capita energy and emissions
    "Log_Utility_Residential_Emissions_Factor",  # checked on tidy_all_data.csv that this is different across communities, varying from ~0.006 to ~0.017, so not sure why its the same value when calculating the means
    "Log_Residential_Total_Energy_Per_Capita",
    "Log_Diff_Utility_Residential_Emissions_Factor",
    "Log_Diff_Residential_Total_Energy_Per_Capita",
]


industrial_policy_features = [
    # Socio-economic baseline
    "Log_Population",
    "Income",
    "Education",
    "Housing",
    "Labour_Force",
    # Socio-economic trajectories
    "Income_Percent_Change",
    "Education_Percent_Change",
    "Housing_Percent_Change",
    "Labour_Percent_Change",
    "Log_Population_Change_2006_2021",
    "Utility_CSMI_Electricity_Energy_Share",
    "Utility_CSMI_Total_Energy_Share",  # this is share on total utility enery, not including tranport
    "CSMI_Electricity_Share_Percent_Change",
    "CSMI_Total_Energy_Share_Percent_Change",
    "Log_Diff_CSMI_Electricity_Per_Capita",
    "Log_Diff_CSMI_Polluting_Per_Capita",
    "Log_CSMI_Electricity_Per_Capita",
    "Log_CSMI_Polluting_Per_Capita",
    # if we want to use the aggregate per capita energy
    "Log_CSMI_Total_Energy_Per_Capita",
    "Log_Diff_CSMI_Total_Energy_Per_Capita",
    "Log_Utility_CSMI_Emissions_Factor",
    "Log_Diff_Utility_CSMI_Emissions_Factor",
]

non_unimodal_features = []


socio_economic_political_context = [
    # Climate action
    "Climate_Action_N_Barriers",
    "Climate_Action_Score",
    # Socio-economic baseline
    "Log_Population",
    "Income",
    "Education",
    "Housing",
    "Labour_Force",  #'CWB',
    # Socio-economic trajectories
    "Income_Percent_Change",
    "Education_Percent_Change",
    "Housing_Percent_Change",
    "Labour_Percent_Change",
    "Log_Population_Change_2006_2021",
]


wellbeing_features = [
    # Wellbeing baseline
    "Income",
    "Education",
    "Housing",
    "Labour_Force",  #'CWB',
    # Wellbeing trajectories
    "income_percent_change",
    "education_percent_change",
    "housing_percent_change",
    "labour_percent_change",
    "population_percent_change",
]

climate_action_summary_features = [
    # Climate action
    "Climate_Action_N_Barriers",
    "Climate_Action_Score",
]

# variables that won't change over time (remoteness could change over decades or centuries or with a large intervention, but lat,lon won't change)
structural = [
    "Remoteness",
    "Latitude",
    "Longitude",
]

features_visual_inspection = [
    "Remoteness",
    "Latitude",
    "Utility_Residential_Electricity_Energy_Share",
    "Log_CSMI_Polluting_Per_Capita",
]

features_to_use = residential_electrification_policy
# residential_electrification_policy
# low_emission_transport_policy


# build wide feature matrix for REFERENCE_YEAR
df_base_year = tidy_all_data.loc[
    tidy_all_data["Year"] == REFERENCE_YEAR, ["Municipality_Name", "Metric", "Value"]
].copy()
# Find duplicates
duplicates = df_base_year[
    df_base_year.duplicated(subset=["Municipality_Name", "Metric"], keep=False)
]
print(f"Found {len(duplicates)} duplicate rows:")
display(duplicates.sort_values(["Municipality_Name", "Metric"]))

df_wide_base_year = df_base_year.pivot(
    index="Municipality_Name", columns="Metric", values="Value"
)
# ensure chosen features are present, add missing as NaN
for f in features_to_use:
    if f not in df_wide_base_year.columns:
        df_wide_base_year[f] = np.nan

# select only desired columns and drop rows with no data at all
X = df_wide_base_year[features_to_use].copy()

# diagnostic: find missing values BEFORE scaling/PCA (PCA/Scaler do not accept NaN)
nan_counts = X.isna().sum()
if nan_counts.sum() > 0:
    print("Missing values present. Counts per feature:\n", nan_counts[nan_counts > 0])
    nan_rows = X[X.isna().any(axis=1)]
    print("\nCommunities with missing data (total {}):".format(len(nan_rows)))
    for idx, row in nan_rows.iterrows():
        missing_feats = row[row.isna()].index.tolist()
        print(f" - {idx}: missing {missing_feats}")
    # show some raw tidy rows for the first few affected communities to investigate source
    sample_comm = list(nan_rows.index)[:8]
    print("\nSample raw tidy_all_data rows for inspection:")
    display(
        tidy_all_data[tidy_all_data["Municipality_Name"].isin(sample_comm)]
        .sort_values(["Municipality_Name", "Year", "Metric"])
        .tail(100)
    )
else:
    print("No missing values found in X.")


# %%
df_base_year.head()

# %%
df_base_year[df_base_year["Metric"] == "Log_Utility_Residential_Emissions_Factor"]

# %%
# clustering municipalities based on PCA of selected metrics

# --- PCA + clustering pipeline (add / run in a new cell) ---
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

standardize = True
# select which X to use for clustering (scaled or original)
if standardize:
    # Standardize (use X for the pipeline)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_for_clustering = X_scaled.copy()
    # PCA: keep components that explain 80% variance for clustering, but compute 2D for plotting
    pca80 = PCA(n_components=0.80, svd_solver="full")
    X_pca_80 = pca80.fit_transform(X_for_clustering)
    print(f"PCA reduced to {X_pca_80.shape[1]} components to explain 80% variance")
else:
    X_for_clustering = X.copy()
    # PCA: keep components that explain 80% variance for clustering, but compute 2D for plotting
    pca80 = PCA(n_components=0.80, svd_solver="full")
    X_pca_80 = pca80.fit_transform(X_for_clustering)

    print(f"PCA reduced to {X_pca_80.shape[1]} components to explain 80% variance")

# %%

from diptest import diptest

multimodal_features = []
for col in X.columns:
    dip, p = diptest(X[col].values)
    if p < 0.1:
        multimodal_features.append(col)
        print(f"{col}: p={p:.4f} (non-normal)")


# %%
multimodal_features = []
num_features = X_scaled.shape[1]
for i in range(1, num_features):
    dip, p = diptest(X_scaled[:, i])
    if p < 0.1:
        multimodal_features.append(col)
        print(f"{col}: p={p:.4f} (non-normal)")

# %%
# Correlation matrix
corr_matrix = X.corr()  # .abs()

# Find pairs with correlation > 0.7
high_corr_pairs = []
for i in range(len(corr_matrix.columns)):
    for j in range(i + 1, len(corr_matrix.columns)):
        if corr_matrix.iloc[i, j] > 0.8 or corr_matrix.iloc[i, j] < -0.8:
            high_corr_pairs.append(
                (corr_matrix.columns[i], corr_matrix.columns[j], corr_matrix.iloc[i, j])
            )

print("Highly correlated pairs (keep one, drop other):")
for v1, v2, corr in high_corr_pairs:
    print(f"  {v1} <-> {v2}: {corr:.2f}")

# %%
from sklearn.neighbors import NearestNeighbors
import numpy as np


def hopkins_statistic(X, sample_size=0.5):
    n = len(X)
    m = int(n * sample_size)

    # Random points from data space
    X_uniform = np.random.uniform(X.min(axis=0), X.max(axis=0), (m, X.shape[1]))

    # Random sample from actual data
    random_indices = np.random.choice(n, m, replace=False)
    X_sample = X[random_indices]

    # Nearest neighbor distances
    nn = NearestNeighbors(n_neighbors=2)
    nn.fit(X)

    u_dist = nn.kneighbors(X_uniform, return_distance=True)[0][:, 1]
    w_dist = nn.kneighbors(X_sample, return_distance=True)[0][:, 1]

    H = u_dist.sum() / (u_dist.sum() + w_dist.sum())
    return H


H = hopkins_statistic(X_pca_80)  # (X_scaled)
print(f"Hopkins statistic: {H:.3f}")

# %%
from sklearn.cluster import KMeans
import numpy as np


def gap_statistic(X, k_range=range(1, 10), n_refs=10):
    gaps = []
    for k in k_range:
        # Your data's within-cluster dispersion
        if k == 1:
            Wk = np.sum((X - X.mean(axis=0)) ** 2)
        else:
            km = KMeans(n_clusters=k, random_state=42)
            km.fit(X)
            Wk = km.inertia_

        # Reference (random uniform) dispersion
        ref_disps = []
        for _ in range(n_refs):
            X_random = np.random.uniform(X.min(axis=0), X.max(axis=0), X.shape)
            if k == 1:
                ref_disps.append(np.sum((X_random - X_random.mean(axis=0)) ** 2))
            else:
                km_ref = KMeans(n_clusters=k, random_state=42)
                km_ref.fit(X_random)
                ref_disps.append(km_ref.inertia_)

        gap = np.mean(np.log(ref_disps)) - np.log(Wk)
        gaps.append(gap)

    return list(k_range), gaps


ks, gaps = gap_statistic(X_pca_80)
print("If gap peaks at k=1 or stays flat, no clustering may be justified.")
for k, gap in zip(ks, gaps):
    print(f"k={k}: gap={gap:.3f}")

# %%
# plot gap score vs k
import matplotlib.pyplot as plt
import seaborn as sns

plt.figure(figsize=(8, 5))
sns.lineplot(x=ks, y=gaps, marker="o")
plt.title("Gap Statistic by Number of Clusters (k)")
plt.xlabel("Number of Clusters (k)")
plt.ylabel("Gap Statistic")
plt.ylim(0.0, max(gaps) * 1.1)
plt.xticks(ks)
plt.grid()
plt.show()

# %%
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import mstats

# choose number of clusters with silhouette (k=2..8)
best_k, best_score = None, -1
scores = {}
all_labels = {}
for k in range(2, 10):
    km = KMeans(n_clusters=k, random_state=42, n_init=100)
    labels = km.fit_predict(X_pca_80)  # (X_for_clustering)
    all_labels[k] = labels
    score = silhouette_score(X_pca_80, labels)  # (X_for_clustering, labels)
    scores[k] = score
    if score > best_score:
        best_score = score
        best_k = k
print("Best k:", best_k, "score:", best_score)


print("Silhouette scores by k:", scores)

# Fit final KMeans on PCA space
kmeans_final = KMeans(n_clusters=best_k, random_state=42, n_init=100)
labels_final = kmeans_final.fit_predict(X_pca_80)  # (X_for_clustering)

# assemble results dataframe and save
clusters_df = pd.DataFrame(
    {"Municipality_Name": X.index, "Cluster": labels_final}
).set_index("Municipality_Name")

# merge back some original features for inspection
clustered = X.merge(clusters_df, left_index=True, right_index=True)

# save CSV
clustered.reset_index().to_csv(
    os.path.join(
        "..", "..", "data", "processed", "municipality_clusters_baseline2021.csv"
    ),
    index=False,
)

# %%
# plot silhouette score vs k
plt.figure(figsize=(8, 5))
sns.lineplot(x=list(scores.keys()), y=list(scores.values()), marker="o")
plt.title("Silhouette Score by Number of Clusters (k)")
plt.xlabel("Number of Clusters (k)")
plt.ylabel("Silhouette Score")
# make y axis start at 0.0 and end at 0.5
plt.ylim(0.0, 0.3)
plt.xticks(list(scores.keys()))
plt.grid()
plt.show()


# %%
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import mstats

manual_k = 7
# Fit final KMeans on PCA space
kmeans_final = KMeans(n_clusters=best_k, random_state=42, n_init=100)
labels_final = kmeans_final.fit_predict(X_pca_80)
labels_final = labels_final + 1  # Make cluster labels start from 1 instead of 0

# assemble results dataframe and save
clusters_df = pd.DataFrame(
    {"Municipality_Name": X.index, "Cluster": labels_final}
).set_index("Municipality_Name")

# merge back some original features for inspection
clustered = X.merge(clusters_df, left_index=True, right_index=True)

# save CSV
clustered.reset_index().to_csv(
    os.path.join(
        "..", "..", "data", "processed", "municipality_clusters_baseline2021.csv"
    ),
    index=False,
)

# %%
clustered["Latitude"]

# %%
x = X_pca_80[:, 0]
y = X_pca_80[:, 1]
dip, p = diptest(X_pca_80[:, 0])
print(f"diptest for PCA1 p={p:.4f}")
dip, p = diptest(X_pca_80[:, 1])
print(f"diptest for PCA2 p={p:.4f}")
dip, p = diptest(X_pca_80[:, 2])
print(f"PCA3 p={p:.4f}")
dip, p = diptest(X_for_clustering[:, 1])
print(f"diptest for original p={p:.4f}")

# %%
# Quick diagnostics: which input variables drive PCs and clusters
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from IPython.display import display

# PCA loadings (full PCA on standardized inputs)
pca_full = PCA().fit(X_for_clustering)
loadings = pd.DataFrame(
    pca_full.components_.T,
    index=X.columns,
    columns=[f"PC{i + 1}" for i in range(pca_full.components_.shape[0])],
)
explained = pd.Series(pca_full.explained_variance_ratio_, index=loadings.columns)

# Find variables with max absolute loading < 0.2 across PC1-PC4
max_loadings = loadings.iloc[:, :4].abs().max(axis=1)
low_contributors = max_loadings[max_loadings < 0.2].index.tolist()
print("Consider removing:", low_contributors)

print("Explained variance (first 6 PCs):")
print(explained.head(6).round(3))

print("\nTop contributors to PC1 (absolute loading):")
display(loadings["PC1"].abs().sort_values(ascending=False).head(10))

print("\nTop contributors to PC2 (absolute loading):")
display(loadings["PC2"].abs().sort_values(ascending=False).head(10))

print("\nTop contributors to PC3 (absolute loading):")
display(loadings["PC3"].abs().sort_values(ascending=False).head(10))


# %%
# Heatmap of loadings for first 4 PCs
import matplotlib.pyplot as plt
import seaborn as sns

plt.figure(figsize=(8, 10))
sns.heatmap(loadings.iloc[:, :4], cmap="RdBu_r", center=0, annot=False)
plt.title("PCA loadings (PC1..PC4)")
plt.tight_layout()
plt.show()

# %%
# Heatmap of loadings for PC's giving 80% of variance
import matplotlib.pyplot as plt
import seaborn as sns

plt.figure(figsize=(8, 10))
sns.heatmap(loadings.iloc[:, : X_pca_80.shape[1]], cmap="RdBu_r", center=0, annot=False)
plt.title("PCA loadings (PC1..PC{})".format(X_pca_80.shape[1]))
plt.tight_layout()
plt.show()


# %%

# Quick summary per cluster
display(clustered.groupby("Cluster").mean().round(4))
# save means in a csv
clustered.groupby("Cluster").mean().round(4).to_csv(
    os.path.join(
        "..", "..", "data", "processed", "municipality_clusters_feature_means.csv"
    )
)

# display standard deviation per cluster
display(clustered.groupby("Cluster").std().round(4))
clustered.groupby("Cluster").std().round(4).to_csv(
    os.path.join(
        "..", "..", "data", "processed", "municipality_clusters_feature_std.csv"
    )
)

# %%
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 1. Load the data
means_df = pd.read_csv(
    os.path.join(
        "..", "..", "data", "processed", "municipality_clusters_feature_means.csv"
    )
)
stds_df = pd.read_csv(
    os.path.join(
        "..", "..", "data", "processed", "municipality_clusters_feature_std.csv"
    )
)

# 2. Extract features and cluster labels
# We exclude the 'Cluster' column because it's our y-axis category, not a feature
features = [col for col in means_df.columns if col != "Cluster"]
n_features = len(features)
clusters = means_df["Cluster"].values

# 3. Calculate grid size for the subplots
cols = 3
# Automatically calculate how many rows are needed for 18 features (18/3 = 6 rows)
rows = int(np.ceil(n_features / cols))

# 4. Create the figure and axes
# figsize determines the width and height of the whole image. Adjust as needed!
fig, axes = plt.subplots(rows, cols, figsize=(15, 2 * best_k * rows))
# fig, axes = plt.subplots(rows, cols, figsize=(15, 4 * rows))
axes = axes.flatten()  # Flatten the 2D array of axes for easy iteration

# Create a color map so each cluster has a distinct color
colors = plt.cm.tab10(np.linspace(0, 1, len(clusters)))

# 5. Loop through each feature and plot it
for i, feature in enumerate(features):
    ax = axes[i]

    # Extract the arrays of means and standard deviations for the current feature
    f_means = means_df[feature].values
    f_stds = stds_df[feature].values

    # Plot the dot and whisker for each cluster
    for j, cluster in enumerate(clusters):
        # Plot the horizontal whisker (mean - std to mean + std)
        ax.hlines(
            y=cluster,
            xmin=f_means[j] - f_stds[j],
            xmax=f_means[j] + f_stds[j],
            color=colors[j],
            linewidth=2,
            alpha=0.7,
        )

        # Plot the dot (the mean)
        ax.plot(
            f_means[j],
            cluster,
            "o",
            color=colors[j],
            markersize=8,
            label=f"Cluster {int(cluster)}" if i == 0 else "",
        )

    # Formatting for the specific subplot
    ax.set_title(feature, fontsize=12, fontweight="bold")
    ax.set_yticks(clusters)
    ax.set_yticklabels([f"C{int(c)}" for c in clusters])
    ax.set_ylim(
        min(clusters) - 0.5, max(clusters) + 0.5
    )  # Add some padding around the clusters
    ax.invert_yaxis()  # Put Cluster 0 at the top, Cluster 2 at the bottom
    ax.grid(
        True, axis="x", linestyle="--", alpha=0.6
    )  # Vertical grid lines for readability

# 6. Clean up empty subplots
# If your features aren't a perfect multiple of the columns, hide the extra blank plots
for k in range(n_features, len(axes)):
    fig.delaxes(axes[k])

# 7. Add a single master legend at the very top of the figure
handles, labels = axes[0].get_legend_handles_labels()
fig.legend(
    handles,
    labels,
    loc="upper center",
    bbox_to_anchor=(0.5, 1.02),
    ncol=len(clusters),
    fontsize=12,
)

# 8. Adjust layout and save
plt.tight_layout()
plt.savefig("faceted_dot_whisker.png", bbox_inches="tight", dpi=300)
plt.show()  # Uncomment this if you are running in a Jupyter Notebook to see it inline

# %%

# Plot PCA 2D scatter with cluster labels
plt.figure(figsize=(10, 6))
palette = sns.color_palette("tab10", n_colors=manual_k)  # best_k
sns.scatterplot(
    x=X_pca_80[:, 0],
    y=X_pca_80[:, 1],
    hue=labels_final,
    palette=palette,
    s=80,
    legend="full",
)
plt.title(f"PCA (2D) - Municipal clusters (k={best_k})")
plt.xlabel("PC1")
plt.ylabel("PC2")
plt.legend(title="Cluster {}", bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.show()

# %%
municipality_names = X.index


# %%
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
import numpy as np
import pandas as pd


pca3 = PCA(n_components=3)
X_pca3 = pca3.fit_transform(X_for_clustering)
X_pca_3_standardized = StandardScaler().fit_transform(X_pca3)  # Equal weighting

df3 = pd.DataFrame(X_pca3, columns=["PC1", "PC2", "PC3"], index=municipality_names)
df3["Cluster"] = labels_final

fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection="3d")
palette = plt.cm.get_cmap("tab10", np.unique(labels_final).size)

for k in np.unique(labels_final):
    mask = df3["Cluster"] == k
    ax.scatter(
        df3.loc[mask, "PC1"],
        df3.loc[mask, "PC2"],
        df3.loc[mask, "PC3"],
        label=f"Cluster {k}",
        s=30,
        alpha=0.8,
        color=palette(k),
    )

ax.set_xlabel("PC1")
ax.set_ylabel("PC2")
ax.set_zlabel("PC3")
ax.set_title("PCA 3D - Municipal Clusters")
ax.legend(loc="upper right", bbox_to_anchor=(1.2, 1))
plt.tight_layout()
# plt.savefig('reports/figures/pca_3d_clusters.png', dpi=200, bbox_inches='tight')
plt.show()


# %%
import plotly.express as px
import pandas as pd


# X_pca3: numpy array shape (n_samples, 3)
# labels_final: 1D array of cluster labels
# municipality_names: index or list of municipality names (length n_samples)
municipality_names = X.index
df3 = pd.DataFrame(X_pca3, columns=["PC1", "PC2", "PC3"], index=municipality_names)
df3["Cluster"] = labels_final
df3["Municipality"] = df3.index

fig = px.scatter_3d(
    df3,
    x="PC1",
    y="PC2",
    z="PC3",
    color="Cluster",
    hover_name="Municipality",
    # symbol='Cluster',
    size_max=6,
    title="PCA 3D - Municipal Clusters",
    opacity=0.9,
)
fig.update_traces(marker=dict(size=4))
fig.update_layout(scene=dict(xaxis_title="PC1", yaxis_title="PC2", zaxis_title="PC3"))
fig.show()

# Optional: save interactive HTML
# fig.write_html('reports/figures/pca_3d_clusters.html', include_plotlyjs='cdn')


# %%
# calculate mean and std dev for all features of munis within each cluster, even the ones not used in clustering
# Pivot tidy_all_data to wide: municipalities × features
df_wide = tidy_all_data.pivot_table(
    index="Municipality_Name",
    columns="Metric",
    values="Value",
    aggfunc="first",  # in case of duplicates
)

# Add cluster labels (merge clusters_df into df_wide)
df_wide = df_wide.merge(clusters_df, left_index=True, right_index=True, how="left")

# Now compute stats per cluster
cluster_stats = df_wide.groupby("Cluster").agg(["mean", "std"])
display(cluster_stats)

# %%
X


# %%
# Eta-squared for each feature across k clusters
def eta_squared(X, labels, col):
    groups = [
        X[col].values[labels == k] for k in np.unique(labels)
    ]  # gets the values from one feature (from cols), and splits it into groups based on the cluster labels
    grand_mean = X[col].mean()

    ss_between = sum(len(g) * (g.mean() - grand_mean) ** 2 for g in groups)
    ss_total = sum((X[col].values - grand_mean) ** 2)

    return ss_between / ss_total if ss_total > 0 else 0


effect_sizes = {}
for col in X.columns:
    effect_sizes[col] = eta_squared(X, labels_final, col)

eta_df = pd.DataFrame.from_dict(
    effect_sizes, orient="index", columns=["eta_squared"]
).sort_values("eta_squared", ascending=False)
print("Features ranked by eta-squared (variance explained by clusters):")
display(eta_df.round(3))

import seaborn as sns
import matplotlib.pyplot as plt

# Assuming you have a dict of labels for different k values
# e.g., all_labels = {2: labels_k2, 3: labels_k3, ..., 7: labels_k7}

eta_matrix = {}
for k, labels in all_labels.items():
    eta_matrix[f"k={k}"] = {col: eta_squared(X, labels, col) for col in X.columns}

eta_heatmap = pd.DataFrame(eta_matrix)

# Sort rows by mean eta-squared across all k
eta_heatmap = eta_heatmap.loc[
    eta_heatmap.mean(axis=1).sort_values(ascending=False).index
]

plt.figure(figsize=(8, 10))
sns.heatmap(eta_heatmap, annot=True, fmt=".2f", cmap="YlOrRd", vmin=0, vmax=1)
plt.title("Feature importance (η²) across different cluster resolutions")
plt.xlabel("Number of clusters")
plt.tight_layout()
plt.show()

# Supervised check: how predictive each feature is of the cluster (permutation importance)
rf = RandomForestClassifier(n_estimators=300, random_state=42, n_jobs=-1)
# X_filled = X.fillna(X.median())
# rf.fit(X_filled, labels_final)
rf.fit(X, labels_final)
perm = permutation_importance(
    rf, X, labels_final, n_repeats=30, random_state=42, n_jobs=-1
)
# perm = permutation_importance(rf, X_filled, labels_final, n_repeats=30, random_state=42, n_jobs=-1)
imp_df = pd.Series(perm.importances_mean, index=X.columns).sort_values(ascending=False)
print("\nTop features by permutation importance (random forest predicting clusters):")
display(imp_df.head(10).round(4))

plt.figure(figsize=(8, 4))
imp_df.head(5).plot.bar()
plt.ylabel("Permutation importance")
plt.title("Top feature importances for cluster prediction")
plt.tight_layout()
plt.show()

# Guidance:
print("\nInterpretation hints:")
print("- PCA loadings: large absolute loading = strong contributor to that PC.")
print("- Explained variance: which PCs capture most variance.")
print("- Cluster centroids: show how clusters differ on original features.")
print("- ANOVA F: features with large F differ most across clusters (statistical).")
print(
    "- Permutation RF importance: features that best predict cluster membership (useful for interpretability)."
)


# %%
# Create tidy cluster dataframe, attach lat/lon, save and plot on BC map
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns

BASE_YEAR = 2021
metric_name = (
    "cluster_energy_wellbeing"  # change to 'cluster_energy' or other if desired
)
unit_name = "cluster_number"

# 1) Build clusters DataFrame (expecting either clusters_df or labels_final + X.index)
if "clusters_df" in globals():
    clusters_src = clusters_df.reset_index()[["Municipality_Name", "Cluster"]].copy()
else:
    # fall back to labels_final and X.index
    if "labels_final" in globals() and "X" in globals():
        clusters_src = pd.DataFrame(
            {"Municipality_Name": X.index, "Cluster": labels_final}
        )
    else:
        raise RuntimeError(
            "No cluster results found. Run the clustering cells first (need `clusters_df` or `labels_final` + `X`)."
        )

clusters_src.head()

# %%
# merge cluster numbers with df_wide by matching municiopality names
df_wide = tidy_all_data.pivot_table(
    index="Municipality_Name",
    columns="Metric",
    values="Value",
)

# Add cluster labels (merge clusters_df into df_wide)
df_wide = df_wide.merge(clusters_df, left_index=True, right_index=True, how="left")


# %%
# plot the final analysis data with coordinates on a map of BC, with shapefile located in the raw dataset subfolder BC_Boundary as BC_Boundary.shp
import geopandas as gpd

# Load the shapefile for BC boundaries
bc_boundaries = gpd.read_file(
    os.path.join("..", "..", "data", "raw", "BC_Boundary", "BC_Boundary.shp")
)
# Convert the final analysis data with coordinates to a GeoDataFrame
final_analysis_gdf = gpd.GeoDataFrame(
    df_wide,
    geometry=gpd.points_from_xy(df_wide["Longitude"], df_wide["Latitude"]),
    crs="EPSG:4326",  # WGS84 coordinate system
)
"""
cluster_colors = {
    0: 'green',
    1: 'blue',
    2: 'orange',
    3: 'purple',
    4: 'pink',
    5: 'red',
    6: 'black'  
}
"""
# Plot BC base map and clusters (one color per cluster)
clusters = sorted([c for c in df_wide["Cluster"].dropna().unique()])
n_clusters = max(1, len(clusters))
palette = sns.color_palette("tab10", n_colors=max(10, n_clusters))
cluster_colors = {c: palette[i % len(palette)] for i, c in enumerate(clusters)}

final_analysis_gdf["color"] = final_analysis_gdf["Cluster"].map(cluster_colors)

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
    for label, color in cluster_colors.items()
]
plt.legend(handles=handles, title="Cluster Type", loc="upper right")

plt.title("Communities in BC with Cluster Types ")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.grid()
plt.tight_layout()
plt.show()

# %%
BASE_YEAR = 2021
metric_name = (
    "cluster_energy_wellbeing"  # change to 'cluster_energy' or other if desired
)
unit_name = "cluster_number"
# 2) Save tidy cluster table with Year, Metric, Value, Unit
tiny_cluster = clusters_src.copy()
tiny_cluster["Year"] = BASE_YEAR
tiny_cluster["Metric"] = metric_name
tiny_cluster["Value"] = tiny_cluster["Cluster"]  # cluster number as value
tiny_cluster["Unit"] = unit_name
tiny_cluster = tiny_cluster[["Municipality_Name", "Year", "Metric", "Value", "Unit"]]

# 5) Save tidy cluster CSV
out_path = os.path.join(
    "..",
    "..",
    "data",
    "processed",
    f"municipality_clusters_tidy_{metric_name}_{BASE_YEAR}.csv",
)
tiny_cluster.to_csv(out_path, index=False)
print(f"Saved tidy cluster CSV to: {out_path}")
print("Sample rows:")
display(tiny_cluster.head(10))
