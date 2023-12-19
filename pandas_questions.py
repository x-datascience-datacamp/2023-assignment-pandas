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
    referendum = pd.DataFrame(pd.read_csv("data/referendum.csv", sep=";"))
    regions = pd.DataFrame(pd.read_csv("data/regions.csv"))
    departments = pd.DataFrame(pd.read_csv("data/departments.csv"))

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    merge_dep_reg = pd.merge(
        departments, regions, left_on='region_code', right_on='code'
    ).rename(
        columns={
            'code_x': 'code_dep',
            'name_x': 'name_dep',
            'code_y': 'code_reg',
            'name_y': 'name_reg',
        }
    ).loc[:, ['code_reg', 'name_reg', 'code_dep', 'name_dep']]

    return merge_dep_reg


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    regions_and_departments = regions_and_departments[
        ~regions_and_departments['code_reg'].str.contains('COM')]

    referendum['Department code'] = (
        referendum['Department code']
        .astype(str)
        .str.zfill(2)
    )

    return pd.merge(
        referendum,
        regions_and_departments,
        left_on='Department code',
        right_on='code_dep'
    )


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    dic_code_name_region = referendum_and_areas.set_index(
        'code_reg')['name_reg'].to_dict()

    referendum_result_by_regions = referendum_and_areas.groupby(
        'code_reg').sum().loc[:, [
            'Registered',
            'Abstentions',
            'Null',
            'Choice A',
            'Choice B'
            ]]

    referendum_result_by_regions[
        'name_reg'] = referendum_result_by_regions.index.map(
        lambda x: dic_code_name_region[x])

    return referendum_result_by_regions.loc[:, [
        'name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B'
        ]]


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The
    results should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo_data_regions = gpd.read_file('data/regions.geojson')

    merged_data = geo_data_regions.merge(
        referendum_result_by_regions,
        left_on='code',
        right_index=True
    )

    merged_data['ratio'] = merged_data['Choice A'] / (
        merged_data['Choice A'] + merged_data['Choice B'])

    merged_data.plot(column='ratio', cmap='coolwarm', legend=True)

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
