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
    """Load data from the CSV files referendum/regions/departments."""
    referendum = pd.read_csv("data/referendum.csv", sep=";")
    regions = pd.read_csv('data/regions.csv', sep=',')
    departments = pd.read_csv('data/departments.csv', sep=',')
    
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    print(regions.columns)
    regions.columns = ['id', 'region_code', 'name_reg', 'slug']
    print(regions.columns)
    regions_and_departments = pd.merge(
        departments[['region_code', 'code', 'name']],
        regions[['region_code', 'name_reg']],
        on='region_code',
        how='left'
    )
    regions_and_departments.columns = ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    print(regions_and_departments)
    return regions_and_departments


merge_regions_and_departments(load_data()[1], load_data()[2])


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    print(regions_and_departments['code_reg'])
    print(~regions_and_departments['code_reg'].str.contains('COM'))
    regions_and_departments = regions_and_departments[~regions_and_departments['code_reg'].str.contains('COM')]

    return regions_and_departments


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    result_by_regions = referendum_and_areas.set_index('code_reg')[['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']]
    return result_by_regions


def plot_referendum_map(referendum_result_by_regions):
        """Plot a map with the results from the referendum.

        * Load the geographic data with geopandas from `regions.geojson`.
        * Merge these info into `referendum_result_by_regions`.
        * Use the method `GeoDataFrame.plot` to display the result map. The results
            should display the rate of 'Choice A' over all expressed ballots.
        * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
        """
        geo_data = geopandas.read_file('regions.geojson')
        merged_data = geo_data.merge(referendum_result_by_regions, left_on='region_code', right_on='code_reg')
        merged_data['ratio'] = merged_data['Choice A'] / (merged_data['Choice A'] + merged_data['Choice B'])
        merged_data.plot(column='ratio')
        return merged_data


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
