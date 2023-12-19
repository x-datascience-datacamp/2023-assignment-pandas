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
    # Assuming you have CSV files named 'referendum.csv', 'regions.csv',
    # and 'departments.csv'
    referendum = pd.read_csv('data/referendum.csv', delimiter=";")
    regions = pd.read_csv('data/regions.csv', delimiter=",")
    departments = pd.read_csv('data/departments.csv', delimiter=",")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    merged_df = pd.merge(regions[['code', 'name']],
                         departments[['region_code', 'code', 'name']],
                         left_on='code',
                         right_on='region_code',
                         how='left')
    merged_df = merged_df.drop(columns=['region_code'])
    merged_df = merged_df.rename(columns={'code_x': 'code_reg',
                                          'name_x': 'name_reg',
                                          'code_y': 'code_dep',
                                          'name_y': 'name_dep'})
    merged_df['code_dep'] = merged_df['code_dep'].str.lstrip('0')

    return merged_df


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    merged_df_2 = pd.merge(referendum,
                           regions_and_departments,
                           left_on='Department code',
                           right_on='code_dep',
                           how='left')

    delete_row = merged_df_2[merged_df_2["Department code"].str.startswith('Z')
                             ].index
    merged_df_2 = merged_df_2.drop(delete_row)
    return merged_df_2


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    result_by_regions = referendum_and_areas.groupby('code_reg').agg({
        'name_reg': 'first',
        'Registered': 'sum',
        'Abstentions': 'sum',
        'Null': 'sum',
        'Choice A': 'sum',
        'Choice B': 'sum'
    }).reset_index()

    result_by_regions = result_by_regions.drop(columns=['code_reg'])
    return result_by_regions


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    regions_geojson = gpd.read_file('data/regions.geojson')
    # Merge geographic data with referendum results
    merged_geo_data = pd.merge(regions_geojson,
                               referendum_result_by_regions,
                               left_on='nom',
                               right_on='name_reg',
                               how='left')

    # Calculate the ratio of 'Choice A' over all expressed ballots
    total = (merged_geo_data['Choice A'] + merged_geo_data['Choice B'])
    merged_geo_data['ratio'] = merged_geo_data['Choice A'] / total

    # Plot the map
    merged_geo_data.plot(column='ratio',
                         cmap='viridis',
                         legend=True,
                         legend_kwds={'label': "Choice A ratio"},
                         figsize=(10, 8))
    plt.title('Referendum Results by Regions')

    return merged_geo_data


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
