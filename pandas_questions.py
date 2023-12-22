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
    regions = regions[['code', 'name']]
    departments = departments[['region_code', 'code', 'name']]

    regions.rename(columns={'code': 'code_reg',
                   'name': 'name_reg'},
                   inplace=True)

    departments.rename(columns={'region_code': 'code_reg',
                       'code': 'code_dep', 'name': 'name_dep'},
                       inplace=True)

    regions_and_departments = pd.merge(departments,
                                       regions,
                                       on="code_reg",
                                       how='left')

    return regions_and_departments


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum = referendum.loc[referendum['Department code'] <= '95', :]

    referendum['Department code'] = (referendum['Department code']
                                     .astype(str).str.zfill(2))

    referendum_and_areas = pd.merge(referendum,
                                    regions_and_departments,
                                    left_on=['Department code'],
                                    right_on=['code_dep'],
                                    how='left')

    return referendum_and_areas


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    ref_results = referendum_and_areas.loc[:, ['code_reg',
                                               'name_reg',
                                               'Registered',
                                               'Abstentions',
                                               'Null',
                                               'Choice A',
                                               'Choice B']]

    ref_results = ref_results.groupby(['code_reg', 'name_reg']).sum()
    ref_results = ref_results.reset_index('name_reg')

    return ref_results


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geoData = gpd.read_file('data/regions.geojson')

    geo_ref_results = gpd.GeoDataFrame(pd.merge(referendum_result_by_regions,
                                                geoData,
                                                left_on=['code_reg'],
                                                right_on=['code'],
                                                how='left')
                                       )

    geo_ref_results['ratio'] = (geo_ref_results['Choice A'] /
                                (geo_ref_results['Choice A'] +
                                 geo_ref_results['Choice B']))

    geo_ref_results.plot(column='ratio')

    return geo_ref_results


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
