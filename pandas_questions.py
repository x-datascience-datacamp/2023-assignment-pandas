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
    regions = pd.read_csv('./data/regions.csv', sep=',')
    departments = pd.read_csv('./data/departments.csv', sep=',')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    merge = pd.merge(
        left=regions,
        right=departments,
        how='inner',
        left_on='code',
        right_on='region_code'
    )

    merge.drop(
        columns=['slug_x', 'slug_y', 'code_x', 'id_x', 'id_y'],
        inplace=True
    )

    cols_to_change = {
        'name_x': 'name_reg',
        'region_code': 'code_reg',
        'name_y': 'name_dep',
        'code_y': 'code_dep'
    }

    merge.rename(
        columns=cols_to_change,
        inplace=True
        )

    return merge


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum['Department code'] = referendum['Department code'].apply(
        lambda x: '0' + x if len(x) == 1 else x
        )

    return pd.merge(
        left=referendum,
        right=regions_and_departments,
        how='inner',
        left_on='Department code',
        right_on='code_dep'
        )


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    referendum_results = referendum_and_areas[['name_reg',
                                               'Registered',
                                               'Abstentions',
                                               'Null',
                                               'Choice A',
                                               'Choice B',
                                               'code_reg']].copy()

    referendum_results = referendum_results.groupby(
        ['code_reg', 'name_reg'],
        as_index=False
        ).sum()

    referendum_results.set_index(
        'code_reg',
        inplace=True
        )

    return referendum_results


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo_data = gpd.read_file("./data/regions.geojson")
    referendum_result_by_regions = geo_data.merge(
        referendum_result_by_regions,
        left_on='code',
        right_index=True
        )

    referendum_result_by_regions.set_index(
        'code',
        inplace=True
        )

    referendum_result_by_regions['ratio'] = (
        referendum_result_by_regions['Choice A'] /
        (referendum_result_by_regions['Choice A'] +
         referendum_result_by_regions['Choice B'])
        )

    fig, ax = plt.subplots(1, 1, figsize=(12, 8))

    referendum_result_by_regions.plot(
        column='ratio',
        cmap='coolwarm',
        linewidth=0.8,
        ax=ax,
        edgecolor='0.8',
        legend=True
        )

    ax.set_title(
        "Referendum Results: Choice A / All Expressed Ballots"
        )

    ax.set_axis_off()
    plt.show()
    result_with_ratio = referendum_result_by_regions[
        ['name_reg',
         'ratio']
         ]

    return gpd.GeoDataFrame(
        result_with_ratio,
        geometry=referendum_result_by_regions.geometry
        )


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
