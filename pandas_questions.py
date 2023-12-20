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
    regions = pd.read_csv('data/regions.csv')
    departments = pd.read_csv('data/departments.csv')
    return referendum, regions, departments

def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    merged_df = pd.merge(regions, departments, how='inner', left_on='code', right_on='region_code')
    merged_df = merged_df[['code_x', 'name_x', 'code_y', 'name_y']]
    result_df = merged_df.rename(columns={'code_x': 'code_reg', 'name_x': 'name_reg', 'code_y':'code_dep','name_y': 'name_dep'})
    return result_df

def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad, which all have a code that contains `Z`.
    """
    referendum = referendum[~referendum['Department code'].str.startswith('Z')]
    result_df = pd.merge(regions_and_departments, referendum, how='inner', left_on='code_dep', right_on='Department code')
    return result_df 

def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    referendum_and_areas = referendum_and_areas.drop({'code_dep','name_dep','code_reg','Department code', 'Department name','Town code', 'Town name'}, axis=1)
    result_df = referendum_and_areas.groupby(['name_reg']).sum().reset_index()
    return result_df

def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo_data = gpd.read_file('data/regions.geojson')
    referendum_result_by_regions = referendum_result_by_regions.set_index('name_reg')
    merged_data = geo_data.merge(referendum_result_by_regions, left_on='nom', right_index=True)
    merged_data['ratio'] = merged_data['Choice A'] / (merged_data['Choice A'] + merged_data['Choice B'])
    merged_data.plot(column='ratio', cmap='viridis', legend=True, figsize=(12, 8))
    plt.title('Referendum Results: Ratio of "Choice A" over all expressed ballots')
    plt.show()
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
