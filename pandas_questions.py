"""Plotting referendum results in pandas.

In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using `geopandas`.
"""
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def load_data():
    """Load data from the CSV files referendum/regions/departments."""
    referendum = pd.read_csv("./data/referendum.csv", sep=";")
    regions = pd.read_csv("./data/regions.csv")
    departments = pd.read_csv("./data/departments.csv")

    return referendum, regions, departments


def merge_regions_and_departments(regions_df: pd.DataFrame,
                                  departments_df: pd.DataFrame):
    """Merge regions and departments in one DataFrame."""
    map_reg = {"code": "code_reg", "name": "name_reg"}
    map_dep = {
        "region_code": "code_reg",
        "name": "name_dep",
        "code": "code_dep",
    }

    reg_df = regions_df[["code", "name"]].rename(map_reg, axis=1).copy()
    dep_df = departments_df[["region_code", "code", "name"]].rename(
        map_dep, axis=1).copy()

    regions_and_departments = pd.merge(reg_df, dep_df, on="code_reg")
    return regions_and_departments


def merge_referendum_and_areas(
    referendum_df: pd.DataFrame, regions_and_departments_df: pd.DataFrame
):
    """Merge referendum and regions_and_departments in one DataFrame."""
    ref_df = referendum_df.copy()
    ref_df["Department code"] = (
        ref_df["Department code"].astype(str).str.zfill(2)
    )
    regs_deps_df = regions_and_departments_df.copy()

    referendum_and_areas = pd.merge(
        ref_df, regs_deps_df, left_on="Department code", right_on="code_dep"
    )
    return referendum_and_areas


def compute_referendum_result_by_regions(
    referendum_and_areas_df: pd.DataFrame
):
    """Return a table with the absolute count for each region."""
    refer_areas_df = referendum_and_areas_df.copy()
    referendum_results_by_regions = (
        refer_areas_df
        .groupby(["code_reg", "name_reg"])[
            ["Registered", "Abstentions", "Null", "Choice A", "Choice B"]
        ]
        .sum()
        .reset_index("name_reg")
    )
    return referendum_results_by_regions


def plot_referendum_map(
    referendum_result_by_regions_df: pd.DataFrame
):
    """Plot a map with the results from the referendum."""
    regions_gdf: gpd.GeoDataFrame = gpd.read_file("./data/regions.geojson")
    gdf_referendum = regions_gdf.merge(
        referendum_result_by_regions_df,
        how="right",
        left_on="code",
        right_index=True,
    )
    gdf_referendum["ratio"] = (
        gdf_referendum["Choice A"]
        / gdf_referendum[["Choice A", "Choice B"]].sum(axis=1)
    )
    gdf_referendum.plot("ratio")
    plt.show()
    return gdf_referendum


if __name__ == "__main__":
    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(
        df_reg, df_dep
    )
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()
