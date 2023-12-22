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
    departments = pd.read_csv('data/departments.csv')
    regions = pd.read_csv('data/regions.csv')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    a = regions.merge(departments, left_on=['code'],
                      right_on=['region_code'])[['code_x', 'name_x',
                                                 'code_y', 'name_y']]
    a.columns = ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    return a


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad, which all have a code that contains `Z`.

    DOM-TOM-COM departments are departements that are remote from metropolitan
    France, like Guadaloupe, Reunion, or Tahiti.
    """
    referendum = referendum[~referendum['Department code'].str.contains("Z")]

    added_zero = referendum['Department code'].apply(lambda x: x.zfill(2))
    referendum.loc[:, 'Department code'] = added_zero

    referendum = referendum.merge(
        regions_and_departments,
        left_on='Department code',
        right_on='code_dep')

    return referendum.dropna()


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    cls = referendum_and_areas.columns
    dict_cond = {col: ('sum' if col != 'name_reg' else 'first') for col in cls}
    cols_lst = ['name_reg', 'Registered', 'Abstentions',
                'Null', 'Choice A', 'Choice B']
    return referendum_and_areas.groupby('code_reg').agg(dict_cond)[cols_lst]


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map.
    The results
    should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo_data = gpd.read_file('data/regions.geojson')

    merged_pd = pd.merge(geo_data,
                         referendum_result_by_regions,
                         left_on='code',
                         right_index=True)

    merged_pd['ratio'] = merged_pd['Choice A'] /\
        (merged_pd['Choice A'] + merged_pd['Choice B'])
    merged_pd.plot(column='ratio')

    return merged_pd


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
