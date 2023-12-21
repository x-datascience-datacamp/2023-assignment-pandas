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
    referendum = pd.read_csv("./data/referendum.csv", sep=";")
    regions = pd.read_csv("./data/regions.csv", sep=",")
    departments = pd.read_csv("./data/departments.csv", sep=",")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions.rename(columns={"code": "code_reg", "name": "name_reg"},
                   inplace=True)
    departments.rename(columns={"code": "code_dep",
                                "name": "name_dep",
                                "region_code": "code_reg"},
                       inplace=True)
    df = pd.merge(regions, departments, on="code_reg")
    return df[['code_reg', 'name_reg', 'code_dep', 'name_dep']]


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    # Correctly formatting the code_dep column : 1 --> 01 as in
    # regions_and_departments.
    referendum["Department code"] = referendum["Department code"].apply(
        lambda x: '0'+x if len(x) == 1 else x)
    df = pd.merge(regions_and_departments, referendum, left_on="code_dep",
                  right_on="Department code", how="inner")
    return df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    # We group by region and sum the values for each column.
    df = referendum_and_areas[['code_reg', 'name_reg', 'Registered',
                               'Abstentions', 'Null', 'Choice A', 'Choice B']]
    df = df.groupby(['code_reg', 'name_reg']).sum()
    df.reset_index(inplace=True)
    df.set_index('code_reg', inplace=True)
    return df


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo_df = gpd.read_file("./data/regions.geojson")
    # print(geo_df.head())
    df = pd.merge(referendum_result_by_regions, geo_df, left_on='code_reg',
                  right_on='code')
    df['ratio'] = df['Choice A'] / (df['Choice A'] + df['Choice B'])
    df = gpd.GeoDataFrame(df, geometry='geometry')
    df.plot(column='ratio', legend=True)
    return df


if __name__ == "__main__":

    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(
        df_reg, df_dep
    )
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    print(set(referendum_and_areas.columns))
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    print(referendum_results)
    plot_referendum_map(referendum_results)
    plt.show()
