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
    regions = pd.read_csv('data/regions.csv', sep=',')
    departments = pd.read_csv('data/departments.csv', sep=',')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    rad = pd.merge(departments,
                   regions,
                   left_on=['region_code'],
                   right_on=['code']
                   )
    regions_and_departments = rad[
        ['region_code', 'name_y', 'code_x', 'name_x']
        ]
    regions_and_departments.columns = [
        'code_reg', 'name_reg', 'code_dep', 'name_dep']

    return regions_and_departments


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    dep = regions_and_departments['code_dep'].str.lstrip('0')
    regions_and_departments['code_dep'] = dep
    Z = (1 - referendum['Department code'].str.startswith('Z'))
    bool = Z.astype('boolean')
    metropol_ref = referendum[bool]

    referendum_and_areas = pd.merge(metropol_ref,
                                    regions_and_departments,
                                    left_on=['Department code'],
                                    right_on=['code_dep'])

    referendum_and_areas = referendum_and_areas.dropna()

    return referendum_and_areas


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    a = referendum_and_areas.groupby(['code_reg', 'name_reg'])
    b = a.sum().reset_index('name_reg')
    referendum_result_by_regions = b[['name_reg',
                                      'Registered',
                                      'Abstentions',
                                      'Null',
                                      'Choice A',
                                      'Choice B']]
    return referendum_result_by_regions


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    gdf = gpd.read_file("data/regions.geojson")

    referendum_result_by_regions_map = pd.merge(gdf,
                                                referendum_result_by_regions,
                                                right_on='code_reg',
                                                left_on='code')
    A = referendum_result_by_regions_map['Choice A']
    B = referendum_result_by_regions_map['Choice B']
    referendum_result_by_regions_map['ratio'] = A / (A + B)

    s = referendum_result_by_regions.sum()
    ca = round(100*s['Choice A'] / (s['Choice A'] + s['Choice B']), 2)
    referendum_result_by_regions_map.plot(column='ratio', cmap='Blues')
    plt.title('Choice A ratio over the regions')
    plt.text(x=-5.7,
             y=50.1,
             s=f'Choice A ratio over all \nexpressed ballots : \n{ca} %')
    plt.show()

    return referendum_result_by_regions_map


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
