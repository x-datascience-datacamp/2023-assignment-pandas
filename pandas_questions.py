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
import numpy as np


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.read_csv('data/referendum.csv', sep=';')
    regions = pd.read_csv('data/regions.csv')
    departments = pd.read_csv('data/departments.csv')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions_and_departments = pd.merge(  # Inner join by default
        left=regions,
        right=departments,
        left_on="code",
        right_on="region_code",
    )
    regions_and_departments.drop(        # Drop unwanted columns
        columns=["id_x", "id_y", "slug_x", "region_code", "slug_y"],
        inplace=True,
    )
    regions_and_departments.rename(      # Used assigned column names
        columns={
            "code_x": "code_reg",
            "name_x": "name_reg",
            "code_y": "code_dep",
            "name_y": "name_dep",
        },
        inplace=True,
    )
    return regions_and_departments


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    regions_and_departments["code_dep"] = regions_and_departments[
        "code_dep"
    ].str.lstrip("0")

    # take department codes from regions_and_departments as basis
    referendum_and_areas = pd.merge(
        how="left",
        left=regions_and_departments,
        right=referendum,
        left_on="code_dep",
        right_on="Department code",
    )

    # Drop unwanted lines
    mask = referendum_and_areas["Department name"].isin(
        [
            "GUADELOUPE",
            "MARTINIQUE",
            "GUYANE",
            "LA REUNION",
            "MAYOTTE",
            "NOUVELLE CALEDONIE",
            "POLYNESIE FRANCAISE",
            "SAINT PIERRE ET MIQUELON",
            "WALLIS-ET-FUTUNA",
            "SAINT-MARTIN/SAINT-BARTHELEMY",
            "FRANCAIS DE L'ETRANGER",
        ]
    )
    referendum_and_areas = referendum_and_areas.loc[~mask]

    referendum_and_areas.dropna(inplace=True)

    return referendum_and_areas


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """

    agg_cols = [
        "name_reg",
        "Registered",
        "Abstentions",
        "Null",
        "Choice A",
        "Choice B",
    ]

    def agg_func_helper(s: pd.Series):
        """agg_func_helper"""

        if s.name == "name_reg":
            return np.max(s)
        else:
            return np.sum(s)

    referendum_result_by_regions = referendum_and_areas.groupby("code_reg")[
        agg_cols
    ].agg(agg_func_helper)

    return referendum_result_by_regions


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.
    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """

    referendum_results = gpd.read_file("data/regions.geojson")

    referendum_results = referendum_results.merge(
        referendum_result_by_regions,
        left_on="code",
        right_index=True,
    )

    referendum_results["expressed"] = (
        referendum_results["Choice A"] + referendum_results["Choice B"]
    )

    referendum_results["ratio"] = (
        referendum_results["Choice A"] / referendum_results["expressed"]
    )

    f, ax = plt.subplots()
    referendum_results.plot(
        "ratio",
        ax=ax,
        legend=True,
        cmap="OrRd",
    )
    f.suptitle("Ratio of Choice A over all expressed ballots")

    return referendum_results


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
