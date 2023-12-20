"""Plotting referendum results in pandas.

In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using `geopandas`.
"""

import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.read_csv('data/referendum.csv', sep=';')
    regions = pd.read_csv('data/regions.csv', sep=',')
    departments = pd.read_csv('data/departments.csv', sep=',')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    departments = departments.drop(['slug', 'id'], axis=1)
    list = {'region_code': 'code_reg', 'code': 'code_dep', 'name': 'name_dep'}
    departments = departments.rename(columns=list)
    regions = regions.drop(['id', 'slug'], axis=1)
    regions = regions.rename(columns={'code': 'code_reg', 'name': 'name_reg'})
    merged_df = pd.merge(regions, departments, on='code_reg')
    merged_df = merged_df[['code_reg', 'name_reg', 'code_dep', 'name_dep']]
    return merged_df


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum['Department code'] = referendum['Department code'].str.zfill(2)
    X = referendum
    y = regions_and_departments
    cd1 = 'Department code'
    cd2 = 'code_dep'
    merged_df = pd.merge(X, y, how='left', left_on=cd1, right_on=cd2).dropna()
    return merged_df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    results = referendum_and_areas.groupby(['code_reg', 'name_reg']).sum()
    results = results.reset_index()
    results = results.set_index('code_reg')
    list_columns = ['name_reg', 'Registered', 'Abstentions', 'Null']
    list_columns.append('Choice A')
    list_columns.append('Choice B')
    results = results[list_columns]
    return results


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    df = gpd.read_file('data/regions.geojson')
    df = df.rename(columns={'code': 'code_reg', 'nom': 'name_reg'})
    df = df[~df['code_reg'].str.startswith('0')]
    df = df.set_index('code_reg')
    merged = pd.merge(df, referendum_result_by_regions, on='name_reg')
    L = pd.Series(merged['Choice A']/(merged['Choice A'] + merged['Choice B']))
    merged_df = pd.concat([merged, L], axis=1)
    merged_df = merged_df.rename(columns={0: 'ratio'})
    merged_df.plot(column='ratio', legend=True, cmap='OrRd', figsize=(12, 12))
    return merged_df


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
