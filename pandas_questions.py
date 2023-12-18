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
    referendum = pd.read_csv("data//referendum.csv", sep=";", header=0)
    departments = pd.read_csv("data//departments.csv", sep=",", header=0)
    regions = pd.read_csv("data//regions.csv", sep=",", header=0)

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions_and_departments = departments.merge(
        regions.rename(columns={"name": "name_reg", "code": "code_reg"})[[
            "name_reg", "code_reg"
            ]],
        how='left', 
        left_on='region_code',
        right_on='code_reg').rename(
            columns={"name": "name_dep", "code": "code_dep"}
            ).drop(
                columns=["slug", "id", "region_code"])
 
    return regions_and_departments


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    regions_and_departments['code_dep'] = [
        ele.lstrip("0") for ele in regions_and_departments['code_dep']]

    referendum_merged = referendum.merge(
        regions_and_departments, 
        how='left', 
        left_on='Department code',
        right_on='code_dep')
    
    dom_tom_list = [
        'ZA', 'ZB', 'ZC', 'ZD',
        'ZM', 'ZN', 'ZP', 'ZS',
        'ZW', 'ZX', 'ZZ'
        ]
    referendum_merged = referendum_merged.loc[
        (referendum_merged['Department code'].isin(dom_tom_list)) == 0
        ]

    return referendum_merged


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
    regions_geo = gpd.read_file("data//regions.geojson")
    referendum_geo = referendum_result_by_regions.merge(
        regions_geo,
        left_on="code_reg",
        right_on="code")
    referendum_geo = gpd.GeoDataFrame(data=referendum_geo)
    referendum_geo["ratio"] = referendum_geo["Choice A"] / (referendum_geo[
        "Choice A"
        ] + referendum_geo["Choice B"])
    referendum_geo.plot("ratio")
    return referendum_geo


if __name__ == "__main__":

    referendum, df_reg, df_dep = load_data()
    
    regions_and_departments = merge_regions_and_departments(
        df_reg, df_dep
    )
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    print(referendum_and_areas)
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )

    plot_referendum_map(referendum_results)
    plt.show()
    
