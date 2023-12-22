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
    r = regions.rename(columns={'code': 'code_reg', 'name': 'name_reg'})
    d = departments.rename(
        columns={'region_code': 'code_reg', 'code': 'code_dep'}
        )
    d = departments.rename(
        columns={'name': 'name_dep'}
        )
    bd = pd.merge(r, d, on="code_reg")
    bd = bd[['code_reg', 'name_reg', 'code_dep', 'name_dep']]
    return bd


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.

    """
    rd = regions_and_departments
    rf = referendum
    rf['Department code'] = rf['Department code'].apply(
        lambda x: '0' + str(x) if len(str(x)) == 1 else str(x)
        )

    bd = pd.merge(rf, rd, left_on='Department code', right_on='code_dep')
    bd.loc[bd['code_dep'].str.len() == 2]
    return bd


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    # filtering of the columns
    name_reg = referendum_and_areas[["code_reg", "name_reg"]]
    name_reg = name_reg.drop_duplicates()
    referendum_and_areas = referendum_and_areas[
        ["code_reg", "Registered", "Abstentions", "Null",
         "Choice A", "Choice B"]
        ]
    # Regrouping by code_reg
    resreg = referendum_and_areas.groupby('code_reg').sum()
    # Creating final df and setting index on code reg
    rfrr = pd.merge(name_reg, resreg, on='code_reg')
    rfrr = rfrr.set_index("code_reg")
    return rfrr


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    # Charge spatial data
    geo_data = gpd.read_file("data/regions.geojson")
    # Join with `referendum_result_by_regions`.
    bd = pd.merge(geo_data, referendum_result_by_regions,
                  left_on="code", right_on="code_reg")
    # Calculation of the rate of "Choice A"
    bd["rate"] = bd["Choice A"] / (bd["Choice A"] + bd["Choice B"])
    # Generate plot of the result.
    bd.plot(column="rate", legend=True)
    return bd


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
