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
    m = regions[["code", "name"]]\
        .merge(departments[["region_code", "code", "name"]],
               right_on="region_code", left_on="code")
    m = m.drop(columns="region_code").rename(columns={"code_x": "code_reg",
                                                      "name_x": "name_reg",
                                                      "code_y": "code_dep",
                                                      "name_y": "name_dep"})
    return m


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    def chgt(nom):
        if len(nom) == 1:
            return "0"+nom
        else:
            return nom
    referendum["Department code"] = referendum["Department code"].apply(chgt)
    m = referendum\
        .merge(regions_and_departments,
               right_on="code_dep", left_on="Department code").dropna()
    return m


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    m = referendum_and_areas.loc[:, ["code_reg", "name_reg", "Registered",
                                     "Abstentions", "Null", "Choice A",
                                     "Choice B"]].groupby(
                                   ["code_reg", "name_reg"]).sum(
                                       numeric_only=True).reset_index(
                                           level=["name_reg"])

    return m


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    df = gpd.read_file(
        "https://france-geojson.gregoiredavid.fr/repo/regions.geojson")
    ndf = referendum_result_by_regions.merge(df, left_index=True,
                                             right_on="code")
    ndf["ratio"] = ndf["Choice A"]/(ndf["Choice B"]+ndf["Choice A"])
    ndf["ratio"].plot()
    return gpd.GeoDataFrame({"name_reg": ndf["name_reg"],
                            "ratio": ndf["ratio"]})


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
