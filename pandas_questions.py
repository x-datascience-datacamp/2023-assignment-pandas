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
    referendum = pd.read_csv('data/referendum.csv', sep=';')
    regions = pd.read_csv('data/regions.csv')
    departments = pd.read_csv('data/departments.csv')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    reg = regions[["code", "name"]].rename(
        {"code": "code_reg", "name": "name_reg"}, axis='columns')
    dep = departments[["code", "name", "region_code"]].rename(
        {"code": "code_dep", "name": "name_dep", "region_code": "code_reg"},
        axis='columns')
    return pd.merge(reg, dep, on="code_reg")


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    ref = referendum.copy()
    ref.loc[:, 'Department code'] = ref['Department code'].apply(
        lambda s: (2 - len(s))*"0" + s)
    ref = ref[ref["Department name"].isin(
        ["DOM", "TOM", "COM", "FRANCAIS DE L'ETRANGER"]) == 0]

    # referendum = referendum[referendum["Department code"] <= "95"]
    ref["code_dep"] = ref["Department code"]

    return pd.merge(ref, regions_and_departments, on="code_dep")


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    cols = ['code_reg', 'name_reg', 'Registered', 'Abstentions',
            'Null', 'Choice A', 'Choice B']
    ref_and_areas = referendum_and_areas[cols].groupby(
        ["code_reg", "name_reg"]).sum()
    return ref_and_areas.reset_index("name_reg")


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo = gpd.read_file("./data/regions.geojson")
    geo = geo.rename({"code": "code_reg", "nom": "name_reg"}, axis='columns')
    geo = pd.merge(geo, referendum_result_by_regions, on=["name_reg"])
    geo = gpd.GeoDataFrame(geo)
    geo["ratio"] = geo["Choice A"] / (geo["Choice A"]+geo["Choice B"])
    return gpd.GeoDataFrame(geo)


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
