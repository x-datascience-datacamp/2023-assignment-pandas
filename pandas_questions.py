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
import os
import matplotlib.pyplot as plt

# Get the directory of the current Python file
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the folder
data_folder_path = os.path.join(current_dir, 'data')


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.read_csv(os.path.join(data_folder_path, 'referendum.csv'),
                             on_bad_lines='skip', sep=';')
    regions = pd.read_csv(os.path.join(data_folder_path, 'regions.csv'),
                          sep=',')
    departments = pd.read_csv(os.path.join(data_folder_path,
                                           'departments.csv'), sep=',')
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """
    Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    departments = departments.rename(columns={'region_code': 'code_reg',
                                              'code': 'code_dep',
                                              'name': 'name_dep'})
    regions = regions.rename(columns={'code': 'code_reg', 'name': 'name_reg'})

    # Select only the required columns for merging
    merged_df = pd.merge(departments[['code_reg', 'code_dep', 'name_dep']],
                         regions[['code_reg', 'name_reg']],
                         on='code_reg',
                         how='left')
    return merged_df


def merge_referendum_and_areas(referendum, regions_and_departments):
    """
    Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    # Merge and keep only the necessary columns
    merged_df = pd.merge(referendum, regions_and_departments[['code_dep',
                                                              'code_reg',
                                                              'name_reg',
                                                              'name_dep']],
                         left_on='Department code', right_on='code_dep')

    # Drop rows for DOM-TOM-COM and French living abroad
    merged_df = merged_df[~merged_df['code_reg'].isin(
        ['97', '98', '99', 'COM'])]
    # Drop NA values if necessary
    merged_df.dropna(inplace=True)

    return merged_df


def compute_referendum_result_by_regions(referendum_and_areas):
    """
    Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    result = referendum_and_areas.groupby('code_reg').agg({
        'name_reg': 'first',
        'Registered': 'sum',
        'Abstentions': 'sum',
        'Null': 'sum',
        'Choice A': 'sum',
        'Choice B': 'sum'
    }).reset_index()
    return result


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    gdf = gpd.read_file(os.path.join(data_folder_path, 'regions.geojson'))
    merged = gdf.merge(referendum_result_by_regions, left_on='nom',
                       right_on='name_reg')
    merged['ratio'] = merged['Choice A'] / (merged['Choice A'] +
                                            merged['Choice B'])
    merged.plot(column='ratio', legend=True, figsize=(10, 10))
    return merged


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
