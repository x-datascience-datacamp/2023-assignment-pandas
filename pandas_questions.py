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
    departments = pd.read_csv("data/departments.csv")

    return referendum, regions, departments


def merge_regions_deps(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    df = pd.merge(
        regions, departments, left_on="code", right_on="region_code", how="right"
    )
    df = df[["region_code", "name_x", "code_y", "name_y"]]
    df = df.rename(
        columns={
            "region_code": "code_reg",
            "name_x": "name_reg",
            "code_y": "code_dep",
            "name_y": "name_dep",
        }
    )

    return df


def merge_referendum_and_areas(referendum, regions_deps):
    """Merge referendum and regions_deps in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """

    regions_deps["code_dep"] = regions_deps["code_dep"].apply(lambda x: x.lstrip("0"))
    referendum_new = referendum[
        referendum["Department code"].isin(regions_deps["code_dep"])
    ]

    df = pd.merge(
        referendum_new,
        regions_deps,
        left_on="Department code",
        right_on="code_dep",
        how="left",
    )

    return df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """

    # we start by grouping by code of regions
    region_counts = referendum_and_areas.groupby("name_reg")[
        ["Registered", "Abstentions", "Null", "Choice A", "Choice B"]
    ].sum()
    region_counts = region_counts.reset_index()

    return region_counts


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """

    # we start by reading the geographic data
    geographic_data = gpd.read_file("data/regions.geojson")

    # we merge the geographic data with referendum results
    geographic = geographic_data.merge(
        referendum_result_by_regions, left_on="nom", right_on="name_reg"
    )

    # we add the rate of choice A
    geographic["ratio"] = geographic["Choice A"] / (
        geographic["Choice A"] + geographic["Choice B"]
    )

    # we transform it into a geodataframe
    geographic = gpd.GeoDataFrame(geographic)

    # now, we plot the result
    geographic.plot(column="ratio")

    return geographic


if __name__ == "__main__":
    referendum, df_reg, df_dep = load_data()
    regions_deps = merge_regions_deps(df_reg, df_dep)
    referendum_areas = merge_referendum_and_areas(referendum, regions_deps)
    referendum_results = compute_referendum_result_by_regions(referendum_areas)
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()
