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
    referendum = pd.read_csv('./data/referendum.csv', sep=';')
    regions = pd.read_csv('./data/regions.csv')
    departments = pd.read_csv('./data/departments.csv')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions_and_departments = pd.merge(
        regions,
        departments,
        left_on='code',
        right_on='region_code',
        suffixes=['_reg', '_dep'])[['code_reg',
                                    'name_reg',
                                    'code_dep',
                                    'name_dep']]
    return regions_and_departments


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    merge_r = referendum[~referendum['Department code'].str.startswith('Z')]
    merge_r['Department code'] = merge_r['Department code'].str.zfill(2)
    r_a_a = pd.merge(regions_and_departments,
                     merge_r,
                     left_on='code_dep',
                     right_on='Department code',
                     how='inner')
    return r_a_a


def compute_referendum_result_by_regions(r_a_a):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    r_r_b_r = r_a_a.groupby(by='code_reg')[['code_reg',
                                            'Registered',
                                            'Abstentions',
                                            'Null',
                                            'Choice A',
                                            'Choice B']
                                           ].sum().reset_index()
    r_r_b_r['name_reg'] = r_a_a['name_reg'].unique()
    r_r_b_r = r_r_b_r.loc[
        :,
        ['code_reg',
         'name_reg',
         'Registered',
         'Abstentions',
         'Null',
         'Choice A',
         'Choice B']
    ]
    r_r_b_r = r_r_b_r.set_index('code_reg')
    return r_r_b_r


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    # Load the geographic data with geopandas
    geo_data = gpd.read_file('./data/regions.geojson')
    geo_data.rename(columns={'code': 'code_reg'}, inplace=True)
    # Merge these info
    referendum_map = pd.merge(referendum_result_by_regions,
                              geo_data,
                              left_on='code_reg',
                              right_on='code_reg')
    referendum_map.set_index('code_reg', inplace=True)
    referendum_map.drop(columns='nom', inplace=True)
    # Compute the ratio
    referendum_map['ratio'] = referendum_map[
        'Choice A'] / (referendum_map['Choice A']+referendum_map['Choice B'])
    # Display the result map
    referendum_map = gpd.GeoDataFrame(referendum_map,
                                      geometry=referendum_map['geometry'])
    referendum_map.plot(column='ratio')
    return referendum_map


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
