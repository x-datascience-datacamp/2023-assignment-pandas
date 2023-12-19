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
    referendum = pd.read_csv("data/referendum.csv", delimiter=";")
    regions = pd.read_csv("data/regions.csv", delimiter=",")
    departments = pd.read_csv("data/departments.csv", delimiter=",")
    return referendum, regions, departments


referendum, regions, departments = load_data()


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """

    regions_and_departments = pd.merge(
        departments,
        regions,
        left_on='region_code',
        right_on='code',
        suffixes=('_dep', '_reg')
    )[["region_code", "name_reg", "code_dep", "name_dep"]]
    regions_and_departments = regions_and_departments.rename(
        columns={
            "region_code": "code_reg"
        }
    )
    return regions_and_departments


print(len(merge_regions_and_departments(regions, departments)))


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    regions_and_departments['code_dep'] = \
        regions_and_departments['code_dep'].str.lstrip('0')
    drop_dep = ["COM", "01", "02", "03", "04", "06"]
    regions_and_departments = regions_and_departments[
        ~regions_and_departments['code_reg'].isin(drop_dep)
    ]
    referendum_and_areas = pd.merge(
        referendum,
        regions_and_departments,
        left_on='Department code',
        right_on='code_dep',
    )
    return referendum_and_areas


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    referendum_and_areas = referendum_and_areas.groupby(
        ['name_reg']
    ).sum('Registered').reset_index()
    return referendum_and_areas[
        [
            'name_reg',
            'Registered',
            'Abstentions',
            'Null',
            'Choice A',
            'Choice B'
        ]
    ]


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    regions_gpd = gpd.read_file('data/regions.geojson')
    regions_results = pd.merge(
        referendum_result_by_regions,
        regions_gpd,
        left_on='name_reg',
        right_on='nom',
    )
    regions_results['ratio'] = regions_results['Choice A'] / \
        (regions_results['Choice A'] + regions_results['Choice B'])
    plot_data = gpd.GeoDataFrame(
        regions_results[["name_reg", "ratio", "geometry"]]
    )
    plot_data.plot(column='ratio', legend=True)
    return plot_data


if __name__ == "__main__":
    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(df_reg, df_dep)
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()
