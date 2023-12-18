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

    referendum = pd.read_csv('data/referendum.csv', delimiter=';')
    regions = pd.read_csv('data/regions.csv')
    departments = pd.read_csv('data/departments.csv')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """

     # Merge the two DataFrames
    merged_df = pd.merge(departments, regions, left_on='region_code', right_on='code')
    merged_df = merged_df[['code_y', 'name_y', 'code_x', 'name_x']]
    merged_df.columns = ['code_reg', 'name_reg', 'code_dep', 'name_dep']

    return merged_df


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """

      # Filter out rows where 'name_dep' is not in valid_departments departmenet entre 1 et 95
    valid_departments = [str(i) for i in range(1, 96)]

    # Merge the DataFrames using the correct column names
    referendum_and_areas = pd.merge(
        referendum,
        regions_and_departments,
        left_on='Department code',
        right_on='code_dep',
    )

    # Filter out rows where 'name_dep' is not in valid_departments
    referendum_and_areas = referendum_and_areas[
        referendum_and_areas['code_dep'].isin(valid_departments)
    ]

    return referendum_and_areas




def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """

     # Regrouper les données par code_reg (code de région) et calculer les sommes
    referendum_result_by_regions = referendum_and_areas.groupby('code_reg').agg({
        'Registered': 'sum',
        'Abstentions': 'sum',
        'Null': 'sum',
        'Choice A': 'sum',
        'Choice B': 'sum'
    }).reset_index()  # Réinitialiser l'index pour avoir code_reg comme colonne

    referendum_result_by_regions['name_reg'] = referendum_and_areas.groupby('code_reg').first()['name_reg'].values
    referendum_result_by_regions = referendum_result_by_regions[['code_reg', 'name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']]
    referendum_result_by_regions.set_index('code_reg', inplace=True)

    return referendum_result_by_regions


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """

    # Load the geographic data
    gdf = gpd.read_file('data/regions.geojson')

    # Merge the geographic data with referendum results
    merged = gdf.merge(referendum_result_by_regions, left_on='code', right_on='code_reg', how='left')

    # Calculate the ratio of 'Choice A' over all expressed ballots
    merged['ratio'] = merged['Choice A'] / (merged['Choice A'] + merged['Choice B'])

    # Create a beautiful map
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    merged.plot(column='ratio', ax=ax, legend=True, cmap='YlGnBu', linewidth=0.8, edgecolor='0.8')

    # Customize legend
    legend = ax.get_legend()
    if legend is not None:
        legend.set_title("Choice A Ratio")

    # Add a title
    ax.set_title("Referendum Results - Choice A Ratio", fontsize=16)

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
