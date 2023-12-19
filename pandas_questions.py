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
    regions = pd.read_csv('./data/regions.csv', index_col='id')
    departments = pd.read_csv('./data/departments.csv', index_col='id')
    regions.rename(columns={'code': 'region_code'}, inplace=True)
    departments.rename(columns={'code': 'Department code', 'name':'Department name'}, inplace=True)

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    merged_df = pd.merge(regions, departments, on='region_code', how='inner')
    merged_df = merged_df[['region_code', 'name', 'Department code', 'Department name']]
    merged_df.rename(columns={'region_code': 'code_reg', 
                              'name':'name_reg',
                              'Department code':'code_dep',
                              'Department name':'name_dep'}, inplace=True)
    return merged_df


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad, which all have a code that contains `Z`.

    DOM-TOM-COM departments are departements that are remote from metropolitan
    France, like Guadaloupe, Reunion, or Tahiti.
    """
    referendum.rename(columns={'Department code':'code_dep'}, inplace=True)
    features = ['code_dep', 'Town code', 'Town name','Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    merged_df = pd.merge(referendum[features], regions_and_departments, on='code_dep', how='inner')
    merged_df = merged_df[~merged_df['code_dep'].str.contains('Z')] #Drop DOM-TOM

    return merged_df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    grouped_df = referendum_and_areas.groupby(['name_reg']).agg({
        'Registered': 'sum',
        'Abstentions': 'sum',
        'Null': 'sum',
        'Choice A': 'sum',
        'Choice B': 'sum'
        }).reset_index().sort_values(by='name_reg', ascending=True)
    return grouped_df


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    # Step 1: Load geographic data
    geo_data_path = './data/regions.geojson'
    geo_df = gpd.read_file(geo_data_path)
    geo_df.rename(columns={'nom':'name_reg'}, inplace=True)

    # Step 2: Merge geographic data with referendum_result_by_regions
    merged_df = pd.merge(geo_df, referendum_result_by_regions, on='name_reg', how='left')

    # Step 3: Calculate the ratio of 'Choice A' over all expressed ballots
    merged_df['ratio'] = merged_df['Choice A'] / (merged_df['Choice A'] + merged_df['Choice B'] + merged_df['Null'])

    # Step 4: Plot the map
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    plt.title("Proportion of choice A by region")
    merged_df.plot(column='ratio', cmap='viridis', linewidth=0.8, ax=ax, edgecolor='0.8', legend=True)

    # Step 5: Return the GeoDataFrame
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
