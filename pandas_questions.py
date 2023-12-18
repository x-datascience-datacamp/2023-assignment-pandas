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
    """Load data from the CSV files rePferundum/regions/departments."""
    referendum = pd.read_csv("data/referendum.csv", sep=";")
    regions = pd.read_csv("data/regions.csv", sep=",")
    departments = pd.read_csv("data/departments.csv", sep=",")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions.columns = ["id", "code_reg", "name_reg", "slug"]
    departments.columns = ["id", "code_reg", "code_dep", "name_dep", "slug"]

    merged_data = regions.merge(departments, on='code_reg')
    regions_and_departments = merged_data[
        ['code_reg', 'name_reg', 'code_dep', 'name_dep']
        ]
    return regions_and_departments


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.
    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """

    referendum["Department code"] = referendum["Department code"]\
        .apply(lambda x: "0" + str(x) if len(str(x)) == 1 else str(x))

    referendum_and_areas = referendum.merge(regions_and_departments,
                                            left_on="Department code",
                                            right_on='code_dep')
    referendum_and_areas = referendum_and_areas\
        .loc[~referendum_and_areas["Department code"].str.startswith("Z")]

    return referendum_and_areas


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.
    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """

    referendum_result_by_region = referendum_and_areas\
        .groupby(["code_reg", "name_reg"])\
        .sum()[["Registered", "Abstentions", "Null", "Choice A", "Choice B"]]\
        .reset_index("name_reg")

    return referendum_result_by_region


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The
    results should display the rate of 'Choice A' over all expressed
    ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the
    results.
    """
    regions = gpd.read_file("data/regions.geojson")
    regions = regions.rename(columns={"nom": "name_reg"})
    merged_data = regions.merge(
            referendum_result_by_regions,
            on='name_reg'
            )
    merged_data['ratio'] = merged_data['Choice A'] / (
        merged_data['Choice A']
        + merged_data['Choice B']
        )
    merged_data.plot(column='ratio', cmap='coolwarm', legend=True)

    return merged_data


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
