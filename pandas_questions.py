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
    referendum = pd.read_csv(
        "/Users/aconrad/Desktop/2023-assignment-pandas/data/referendum.csv",
        sep=';'
        )
    regions = pd.read_csv(
        "/Users/aconrad/Desktop/2023-assignment-pandas/data/regions.csv"
        )
    departments = pd.read_csv(
        "/Users/aconrad/Desktop/2023-assignment-pandas/data/departments.csv"
        )

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """

    regions_and_departments = pd.merge(
        regions,
        departments, left_on='code', right_on='region_code'
        )
    regions_and_departments.drop(
        columns=['id_x', 'slug_x', 'id_y', 'region_code', 'slug_y'],
        inplace=True
        )
    regions_and_departments.rename(
        columns={
            'code_x': 'code_reg',
            'name_x': 'name_reg',
            'code_y': 'code_dep',
            'name_y': 'name_dep'
        },
        inplace=True
        )
    return regions_and_departments


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum_and_areas = pd.merge(
        referendum,
        regions_and_departments,
        left_on='Department code', right_on='code_dep'
        )
    referendum_and_areas.dropna(inplace=True)
    return referendum_and_areas


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    referendum_results = referendum_and_areas.groupby('code_reg').agg({
        'name_reg': 'first',
        'Registered': 'sum',
        'Abstentions': 'sum',
        'Null': 'sum',
        'Choice A': 'sum',
        'Choice B': 'sum'
    }).reset_index()
    return referendum_results


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    regions_geojson = gpd.read_file(
        "/Users/aconrad/Desktop/2023-assignment-pandas/data/regions.geojson"
        )
    merged_dt = pd.merge(
        regions_geojson,
        referendum_result_by_regions,
        how='left',
        left_on='nom',
        right_on='name_reg'
        )
    merged_dt.drop(columns=['name_reg'], inplace=True)
    merged_dt['ratio'] = (
        merged_dt['Choice A'] /
        (merged_dt['Registered'] - merged_dt['Abstentions'])
        )

    _, ax = plt.subplots(1, 1, figsize=(10, 10))
    merged_dt.plot(
        column='ratio',
        cmap='OrRd',
        linewidth=0.8,
        edgecolor='0.8',
        legend=True,
        legend_kwds={'label': "Choice A Rate", 'orientation': "horizontal"},
        ax=ax
        )

    return merged_dt


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
