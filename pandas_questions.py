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
    regions = regions.loc[:, ['code', 'name']]
    departments = departments.loc[:, ['region_code', 'code', 'name']]
    regions.rename(columns={'code': 'code_reg',
                            'name': 'name_reg'}, inplace=True)
    departments.rename(columns={'region_code': 'code_reg',
                                'code': 'code_dep',
                                'name': 'name_dep'}, inplace=True)
    regions_and_departments = pd.merge(regions, departments, on='code_reg')

    return regions_and_departments


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum = referendum[
        ~referendum['Department code'].str.startswith('97')]
    referendum = referendum[
        ~referendum['Department code'].str.startswith('Z')]
    regions_and_departments['code_dep'] = regions_and_departments[
        'code_dep'].astype(str).str.lstrip('0')
    referendum_and_areas = pd.merge(
        referendum, regions_and_departments,
        left_on='Department code', right_on='code_dep', how='left')
    return referendum_and_areas


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    referendum_result_by_regions = referendum_and_areas.groupby(
        'name_reg').agg({
            'Registered': 'sum',
            'Abstentions': 'sum',
            'Null': 'sum',
            'Choice A': 'sum',
            'Choice B': 'sum'}
    ).reset_index()

    return referendum_result_by_regions


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo_data = gpd.read_file('data/regions.geojson')
    geo_data.rename(columns={'nom': 'name_reg'}, inplace=True)
    print(geo_data.head())
    gdf_referendum = pd.merge(
        geo_data, referendum_result_by_regions, on='name_reg')

    gdf_referendum['ratio'] = gdf_referendum['Choice A'] / (
        gdf_referendum['Choice A'] + gdf_referendum['Choice B'])
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    gdf_referendum.plot(column='ratio',
                        cmap='viridis', linewidth=0.8,
                        ax=ax, edgecolor='0.8', legend=True)
    plt.title('Referendum Results: Ratio of Choice A over Expressed Ballots')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')

    plt.show()

    return gdf_referendum


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
