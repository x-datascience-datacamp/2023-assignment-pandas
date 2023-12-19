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
    referendum = pd.read_csv("data/referendum.csv", sep=";")
    regions = pd.read_csv("data/regions.csv", sep=",")
    departments = pd.read_csv("data/departments.csv", sep=",")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    merge_ = pd.merge(departments, regions,
                      left_on='region_code', right_on='code')
    merge_ = merge_.rename(columns={'region_code': 'code_reg',
                                    'code_x': 'code_dep',
                                    'name_x': 'name_dep',
                                    'name_y': 'name_reg'})
    merge_ = merge_[['code_reg', 'name_reg', 'code_dep', 'name_dep']]
    return merge_


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum['Department code'] = referendum['Department code'].str.zfill(2)
    merge_ = pd.merge(referendum, regions_and_departments,
                      how='left', left_on='Department code',
                      right_on='code_dep').dropna()
    # import IPython
    # IPython.embed()
    return merge_


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    results = referendum_and_areas.groupby(['code_reg', 'name_reg']).sum()
    results = results.reset_index()
    results = results.set_index('code_reg')
    results = results[['name_reg', 'Registered',
                       'Abstentions', 'Null', 'Choice A', 'Choice B']]
    return results


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    # Load and prepare geo data
    geo_data = gpd.read_file('data/regions.geojson')
    geo_data = geo_data.rename(columns={'code': 'code_reg'})
    geo_data = geo_data.set_index('code_reg')
    # Merge geo and referendum data
    data = pd.merge(geo_data, referendum_result_by_regions, on='code_reg')
    # Compute ratio
    data['ratio'] = data['Choice A'] / (data['Choice A'] + data['Choice B'])
    # Plot data
    data.plot(column='ratio', legend=True)
    # import IPython
    # IPython.embed()
    return data


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
