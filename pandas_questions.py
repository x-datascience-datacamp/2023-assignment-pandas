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
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.read_csv("data/referendum.csv", sep=";")
    regions = pd.read_csv("data/regions.csv", sep=",")
    departments = pd.read_csv("data/departments.csv", sep=",")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions_and_departments = pd.merge(
        regions,
        departments,
        how="right",
        left_on="code",
        right_on="region_code",
        suffixes=["_reg", "_dep"],
    )
    return regions_and_departments[
        ["code_reg", "name_reg", "code_dep", "name_dep"]
    ]


def custom_int_converter(x):
    """Convert element to int if possible, otherwise return the element."""
    try:
        return int(x)
    except ValueError:
        return x


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    regions_and_departments_copy = regions_and_departments.copy()
    referendum_copy = referendum.copy()
    regions_and_departments_copy["code_dep"] = regions_and_departments_copy[
        "code_dep"
    ].apply(custom_int_converter)
    referendum_copy["Department code"] = referendum_copy[
        "Department code"
    ].apply(custom_int_converter)
    referendum_and_areas = pd.merge(
        referendum_copy,
        regions_and_departments_copy,
        how="left",
        left_on="Department code",
        right_on="code_dep",
    )
    return referendum_and_areas.dropna()


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    return (
        referendum_and_areas.groupby(["code_reg", "name_reg"])[
            ["Registered", "Abstentions", "Null", "Choice A", "Choice B"]
        ]
        .sum()
        .reset_index("name_reg")
    )


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    with open("data/regions.geojson") as file:
        regions_geo = gpd.read_file(file)
    referendum_and_areas_geo = gpd.GeoDataFrame(
        pd.merge(
            referendum_result_by_regions.reset_index(),
            regions_geo,
            how="left",
            left_on="code_reg",
            right_on="code",
        )
    )
    referendum_and_areas_geo["ratio"] = referendum_and_areas_geo[
        "Choice A"
    ] / (
        referendum_and_areas_geo["Choice A"]
        + referendum_and_areas_geo["Choice B"]
    )
    referendum_and_areas_geo.plot(column="ratio")
    return referendum_and_areas_geo


if __name__ == "__main__":
    referendum, df_reg, df_dep = load_data()

    regions_and_departments = merge_regions_and_departments(df_reg, df_dep)
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )

    plot_referendum_map(referendum_results)
    plt.show()
