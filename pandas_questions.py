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
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    departments = departments.rename(columns={"region_code": "code_reg",
                                              "code": "code_dep",
                                              "name": "name_dep"})
    merged = departments.merge(
        regions.rename(columns={"code": "code_reg", "name": "name_reg"}),
        how="inner", on="code_reg")
    return merged.drop(["id_x", "slug_x", "id_y", "slug_y"], axis=1)[[
        'code_reg', 'name_reg', 'code_dep', 'name_dep']]


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    regions_and_departments = regions_and_departments[~regions_and_departments[
        'code_dep'].isin(['971', '972', '973', '974', '976', '975', '977',
                          '978', '984', '986', '987', '988', '989'])]
    referendum["Department code"] = referendum["Department code"].replace(
        {'1': "01", '2': "02", '3': "03", '4': "04", '5': "05", '6': "06", '7':
         "07", '8': "08", '9': "09"})
    res = regions_and_departments.merge(referendum, left_on='code_dep',
                                        right_on='Department code', how='left')
    return res


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    referendum_by_region = referendum_and_areas[
        [
            'code_reg', 'name_reg', 'Registered', 'Abstentions',
            'Null', 'Choice A', 'Choice B'
        ]
    ].groupby(
        by=["name_reg", 'code_reg'], as_index=False
        ).agg('sum').set_index("code_reg")
    return referendum_by_region


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    region_geo = gpd.read_file("data//regions.geojson")
    merged = referendum_result_by_regions.merge(region_geo, left_on="code_reg",
                                                right_on="code", how="inner")
    geo_ref = gpd.GeoDataFrame(merged)
    geo_ref.plot("Choice A")
    geo_ref["ratio"] = geo_ref["Choice A"]/(geo_ref["Choice A"] +
                                            geo_ref["Choice B"])
    return geo_ref


if __name__ == "__main__":

    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(
        df_reg, df_dep
    )
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    print(referendum_and_areas.head())
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    print(referendum_results.head())

    plot_referendum_map(referendum_results)
    plt.show()
