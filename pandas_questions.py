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
    referendum = pd.read_csv("data/referendum.csv", sep=";")
    regions = pd.read_csv("data/regions.csv", sep=",")
    departments = pd.read_csv("data/departments.csv", sep=",")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments into one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    merged = pd.merge(
        regions.drop(["slug", "id"], axis=1),
        departments.drop(["slug", "id"], axis=1),
        how="left",
        right_on="region_code",
        left_on="code",
        suffixes=("_reg", "_dep")
    )
    merged = merged.drop("region_code", axis=1)

    return merged


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments into one DataFrame.
    Drop the lines relative to DOM-TOM-COM departments,and the French
    living abroad.
    """
    referendum["Department code"].replace(
        ["1", "2", "3", "4", "5", "6", "7", "8", "9"],
        ["01", "02", "03", "04", "05", "06", "07", "08", "09"],
        inplace=True
    )
    merged = pd.merge(
        referendum,
        regions_and_departments,
        how="inner",
        left_on="Department code",
        right_on="code_dep"
    )
    return merged


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    count_regions = referendum_and_areas[
        ["name_reg", "code_reg", "Registered",
            "Abstentions", "Null", "Choice A",
            "Choice B"]
    ].groupby(
        ["code_reg", "name_reg"]
        ).sum().reset_index().set_index("code_reg")

    return count_regions


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map.
    * The results should display the rate of
    'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    regions = gpd.read_file("data/regions.geojson")
    referendum_result_by_regions = referendum_result_by_regions.reset_index()
    referendum_result_by_regions["ratio"] = (
        referendum_result_by_regions["Choice A"] /
        (referendum_result_by_regions["Choice A"] +
         referendum_result_by_regions["Choice B"])
    )
    merged = pd.merge(
        regions,
        referendum_result_by_regions,
        how="inner",
        left_on="code",
        right_on="code_reg"
    )
    merged.plot(column="ratio", legend=True)

    return merged


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
