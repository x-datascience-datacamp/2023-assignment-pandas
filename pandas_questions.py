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
    """Load data from the CSV files referundum/regions/departments.
    referendum = pd.DataFrame({})
    regions = pd.DataFrame({})
    departments = pd.DataFrame({})"""
    referendum = pd.read_csv('data/referendum.csv', sep=';')
    regions = pd.read_csv('data/regions.csv', sep=',')
    departments = pd.read_csv('data/departments.csv', sep=',')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    df1 = pd.merge(regions, departments,
                   left_on='code', right_on='region_code')
    df2 = df1[['region_code', 'name_x', 'code_y', 'name_y']]
    df3 = df2.rename(columns={'region_code': 'code_reg',
                              'name_x': 'name_reg',
                              'code_y': 'code_dep',
                              'name_y': 'name_dep'})
    return df3


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    # df1 = referendum[~referendum['Department code'].
    # str.contains('Z')] # ~ = not
    df1 = referendum[(referendum['Department code'].str.isdigit()) |
                     (referendum['Department code'] == '2A') |
                     (referendum['Department code'] == '2B')]
    df1.loc[:, 'Department code'] = df1['Department code'].apply(
        lambda x: x.zfill(2))
    df2 = pd.merge(regions_and_departments, df1,
                   left_on='code_dep', right_on='Department code')
    return df2


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    result_by_region = referendum_and_areas.groupby('code_reg').agg({
        'name_reg': 'first',
        'Registered': 'sum',
        'Abstentions': 'sum',
        'Null': 'sum',
        'Choice A': 'sum',
        'Choice B': 'sum'
    }).reset_index()
    result_by_region.set_index('code_reg', inplace=True)
    return result_by_region


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo_data = gpd.read_file('data/regions.geojson')
    df1 = pd.merge(geo_data, referendum_result_by_regions,
                   left_on='code', right_index=True)
    df1['ratio'] = df1['Choice A'] / (df1['Choice A'] + df1['Choice B'])
    df1.plot(column='ratio', legend=True)
    return df1


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
