# =====================================================================
#  Side-by-side cluster comparison map  (panel a vs panel b)
#  Panel (a): clustering on Latitude ONLY  -> no PCA (single feature)
#  Panel (b): clustering on residential_electrification_policy -> PCA(0.80)
#
#  Drop this in a new cell AFTER:
#    - `tidy_all_data` is loaded   (your cell 0)
#    - `residential_electrification_policy` is defined  (your cell 2)
# =====================================================================
import os
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

REFERENCE_YEAR = 2021
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SHAPEFILE_PATH = os.path.join(
    BASE_DIR, "..", "..", "data", "raw", "BC_Boundary", "BC_Boundary.shp"
)
tidy_all_data = pd.read_csv(
    os.path.join(BASE_DIR, "..", "..", "data", "processed", "tidy_all_metrics.csv")
)

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
    # Climate action institutional capacity
    "Climate_Action_N_Barriers",
    "Climate_Action_Score",
    # Aggregate per capita energy and emissions
    "Log_Utility_Residential_Emissions_Factor",
    "Log_Residential_Total_Energy_Per_Capita",
    "Log_Diff_Utility_Residential_Emissions_Factor",
    "Log_Diff_Residential_Total_Energy_Per_Capita",
]


sensitivity_test_features = [
    "Latitude",
    "Income",
    "Housing",
    "Log_Utility_Residential_Emissions_Factor",
    "Log_Residential_Total_Energy_Per_Capita",
]


def cluster_municipalities(
    tidy_df, features, year=REFERENCE_YEAR, use_pca=True, k=None, k_range=range(2, 10)
):
    """Run your standard pipeline for one feature set and return a tidy
    cluster table: DataFrame[Municipality_Name, Cluster, Latitude, Longitude].

    use_pca=False skips PCA  (needed for the Latitude-only case, where a
    single feature cannot be reduced by PCA).
    k=None  -> pick k automatically by best silhouette over k_range.
    k=<int> -> force that many clusters (use this to fix k across both panels).
    """
    # --- build wide matrix for the reference year (same as your cell 2) ---
    base = tidy_df.loc[
        tidy_df["Year"] == year, ["Municipality_Name", "Metric", "Value"]
    ]
    wide = base.pivot_table(
        index="Municipality_Name", columns="Metric", values="Value", aggfunc="first"
    )

    needed = list(dict.fromkeys(features + ["Latitude", "Longitude"]))
    for f in needed:
        if f not in wide.columns:
            wide[f] = np.nan

    # keep only rows that have every clustering feature (StandardScaler/PCA
    # reject NaN). Coordinates must also be present to place a point.
    X = wide[features].dropna()
    coords = wide.loc[X.index, ["Latitude", "Longitude"]].dropna()
    X = X.loc[coords.index]

    # --- standardize (your cell 5) ---
    X_scaled = StandardScaler().fit_transform(X)

    # --- PCA only when there is more than one feature ---
    if use_pca and X_scaled.shape[1] > 1:
        X_cluster = PCA(n_components=0.80, svd_solver="full").fit_transform(X_scaled)
        print(
            f"  [{len(features)} feature(s)] PCA -> {X_cluster.shape[1]} comps for 80% var"
        )
    else:
        X_cluster = X_scaled
        print(
            f"  [{len(features)} feature(s)] no PCA, clustering on scaled feature(s) directly"
        )

    # --- choose k by silhouette unless forced (your cells 12 + 14) ---
    if k is None:
        best_k, best_score = None, -1.0
        for kk in k_range:
            lbl = KMeans(n_clusters=kk, random_state=42, n_init=100).fit_predict(
                X_cluster
            )
            s = silhouette_score(X_cluster, lbl)
            if s > best_score:
                best_k, best_score = kk, s
        k = best_k
        print(f"  best k by silhouette = {k} (score={best_score:.3f})")
    else:
        print(f"  k forced = {k}")

    labels = KMeans(n_clusters=k, random_state=42, n_init=100).fit_predict(X_cluster)
    labels = labels + 1  # start cluster numbering at 1 (your cell 14)

    out = coords.copy()
    out["Cluster"] = labels
    return out.reset_index(), k


def plot_panel(ax, gdf, bc_boundaries, panel_label, title, show_side=True):
    """Draw one BC map onto `ax`. show_side=False hides the y-label and legend
    (use for the right panel, where they'd be redundant)."""
    clusters = sorted(gdf["Cluster"].dropna().unique())
    palette = sns.color_palette("tab10", n_colors=max(10, len(clusters)))
    cmap = {c: palette[i % len(palette)] for i, c in enumerate(clusters)}

    bc_boundaries.plot(ax=ax, color="lightgrey", edgecolor="black", linewidth=0.6)
    gdf.plot(
        ax=ax,
        marker="o",
        color=gdf["Cluster"].map(cmap),
        markersize=18,
        edgecolor="white",
        linewidth=0.3,
    )

    ax.axhline(y=51.628, color="red", linewidth=2, linestyle="-", label="Lat 51.628")

    if show_side:
        handles = [
            plt.Line2D(
                [0],
                [0],
                marker="o",
                color="w",
                markerfacecolor=cmap[c],
                markersize=9,
                label=f"Cluster {int(c)}",
            )
            for c in clusters
        ]
        handles.append(
            plt.Line2D([0], [0], color="red", linewidth=2, label="Lat 51.628")
        )
        ax.legend(handles=handles, title="Cluster", loc="upper right", fontsize=9)

    ax.set_title(title, fontsize=12)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude" if show_side else "")  # y-label only on panel (a)

    ax.text(
        0.5,
        -0.12,
        panel_label,
        transform=ax.transAxes,
        fontsize=16,
        fontweight="bold",
        va="top",
        ha="center",
    )


# ---------------------------------------------------------------------
# Run both settings.  Set k=<int> on either call to fix the cluster count
# (e.g. k=2 for both) if you want a like-for-like comparison.
# ---------------------------------------------------------------------
print("Panel (a) — Latitude only:")
clusters_lat, k_lat = cluster_municipalities(
    tidy_all_data, ["Latitude"], use_pca=False, k=None
)

print("Panel (b) — residential_electrification_policy:")
clusters_rep, k_rep = cluster_municipalities(
    tidy_all_data, residential_electrification_policy, use_pca=True, k=None
)

bc_boundaries = gpd.read_file(SHAPEFILE_PATH)


def to_gdf(df):
    return gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df["Longitude"], df["Latitude"]),
        crs="EPSG:4326",
    )


gdf_lat = to_gdf(clusters_lat)
gdf_rep = to_gdf(clusters_rep)

fig, axes = plt.subplots(1, 2, figsize=(16, 9), constrained_layout=True)

plot_panel(
    axes[0], gdf_lat, bc_boundaries, "(a)", f"Clustering on Latitude only (k={k_lat})"
)
plot_panel(
    axes[1],
    gdf_rep,
    bc_boundaries,
    "(b)",
    f"Clustering on 18 residential electrification features (k={k_rep})",
    show_side=True,
)

fig.savefig("cluster_comparison_lat_vs_rep.png", dpi=300, bbox_inches="tight")
plt.show()
