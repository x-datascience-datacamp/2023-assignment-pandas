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
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    rename_regions = regions.rename(
        columns={"code": "code_reg", "name": "name_reg"}
    )
    rename_departments = departments.rename(
        columns={"region_code": "code_reg", "code": "code_dep", "name": "name_dep"}
    )
    merge_regions_and_departments = pd.merge(
        rename_regions[["code_reg", "name_reg"]],
        rename_departments[['code_reg', 'code_dep', 'name_dep']],
        on='code_reg',
        how='left'
    )

    return merge_regions_and_departments


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    merge_regions_and_departments_without_DOMTOM = regions_and_departments[
        ~regions_and_departments["code_dep"].isin(['971', 
                                                   '972', 
                                                   '973', 
                                                   '974', 
                                                   '976', 
                                                   '975', 
                                                   '977', 
                                                   '978', 
                                                   '984', 
                                                   '986', 
                                                   '987', 
                                                   '988', 
                                                   '989'])
    ]
    merge_regions_and_departments_without_DOMTOM.loc[:, "code_dep"] = merge_regions_and_departments_without_DOMTOM.loc[:, "code_dep"].apply(lambda x: x.lstrip('0'))
    rename_referendum = referendum.rename(columns={"Department code": "code_dep"})
    rename_referendum_without_DOMTOM = rename_referendum[~rename_referendum["code_dep"].isin(['ZA', 'ZB', 'ZC', 'ZD', 'ZM', 'ZN', 'ZP', 'ZS', 'ZW', 'ZX', 'ZZ'])]
    merge_referendum_and_areas = pd.merge(
        merge_regions_and_departments_without_DOMTOM,
        rename_referendum_without_DOMTOM.drop(columns=["Department name"], axis=1),
        on="code_dep",
        how="left"
    )

    return merge_referendum_and_areas


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    referendum_result_by_regions = referendum_and_areas.groupby(
        ["code_reg", "name_reg"]
    ).sum(numeric_only=True).reset_index().set_index('code_reg').drop(columns=["Town code"], axis=1)

    return referendum_result_by_regions


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geographic_data = gpd.read_file("data/regions.geojson")
    geographic_data.rename(columns={"code": "code_reg"}, inplace=True)
    geographic_data.set_index("code_reg", inplace=True)
    referendum_result_by_regions_geo = pd.merge(
        referendum_result_by_regions,
        geographic_data,
        left_index=True,
        right_index=True,
        how="left"
    ).drop(columns=["nom"], axis=1)
    referendum_result_by_regions_geo["ratio"] = referendum_result_by_regions_geo["Choice A"] / (
            referendum_result_by_regions_geo["Choice A"] + referendum_result_by_regions_geo["Choice B"]
    )
    gdf = gpd.GeoDataFrame(
        referendum_result_by_regions_geo,
        geometry=referendum_result_by_regions_geo['geometry']
    )

    return gdf


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
