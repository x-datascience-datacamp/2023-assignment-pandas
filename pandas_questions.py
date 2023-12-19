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
    referendum = pd.DataFrame({})
    regions = pd.DataFrame({})
    departments = pd.DataFrame({})
    referendum = pd.read_csv('./data/referendum.csv', delimiter=';')
    regions = pd.read_csv('./data/regions.csv', delimiter=',')
    departments = pd.read_csv('./data/departments.csv', delimiter=',')
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    merge = pd.merge(departments, regions, left_on='region_code',
                     right_on='code', how='left')[['region_code',
                                                   'name_y', 'code_x',
                                                   'name_x']]
    merge = merge.rename(columns={"region_code": "code_reg",
                                  "name_y": "name_reg",
                                  "code_x": "code_dep",
                                  "name_x": "name_dep"})
    return merge


def add_0(string):
    """Add a 0 before each department code.

    Ex: 1 becomes 01.
    """
    if len(string) == 1:
        return "0" + string
    else:
        return string


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    ref_copy = referendum[referendum['Department code'] <= '95'].copy()
    ref_copy.loc[:, 'Department code'] = ref_copy['Department code'
                                                  ].apply(add_0)
    reg_copy = regions_and_departments[
        regions_and_departments['code_dep'] <= '95']
    merge = pd.merge(ref_copy, reg_copy, left_on='Department code',
                     right_on='code_dep', how='left')

    return merge


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    df_count = referendum_and_areas.groupby([
        'code_reg', 'name_reg']).sum()[['Registered',
                                        'Abstentions',
                                        'Null',
                                        'Choice A',
                                        'Choice B']]

    return df_count.reset_index(level='name_reg')


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo_data = gpd.read_file('./data/regions.geojson')
    merge_geo_count = geo_data.merge(referendum_result_by_regions,
                                     left_on='code',
                                     right_on='code_reg',
                                     how='left')
    merge_geo_count['total_expressed'] = merge_geo_count[
        'Choice A'] + merge_geo_count['Choice B']
    merge_geo_count['ratio'] = merge_geo_count[
        'Choice A'] / merge_geo_count['total_expressed']
    merge_geo_count.plot('ratio')
    return merge_geo_count


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
