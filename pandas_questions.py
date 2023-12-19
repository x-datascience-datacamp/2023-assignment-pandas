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
    regions = pd.read_csv('data/regions.csv', sep=',')
    departments = pd.read_csv('data/departments.csv', sep=',')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    dtf = pd.merge(regions, departments, left_on='code',
                   right_on='region_code', how='right',
                   suffixes=('_reg', '_dep'))
    # print(dtf)
    dtf["name_reg"].str.strip('"')
    return dtf[['code_reg', 'name_reg', 'code_dep', 'name_dep']]


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    # because in referendum they do 1,2,3 and in dep 01,02,03
    rg = regions_and_departments
    # to be less than 93 in next line
    regions_and_departments['code_dep'] = rg['code_dep'].str.lstrip('0')
    # print(regions_and_departments)
    dtf = pd.merge(referendum, regions_and_departments,
                   left_on='Department code', right_on='code_dep', how="left")
    # the dom_tom codes start with Z
    dtf = dtf[~dtf['Department code'].str.startswith('Z')]
    return dtf


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    region_counts = referendum_and_areas.groupby('code_reg').agg({
        'name_reg': 'first',  # taking the first one
        'Registered': 'sum',
        'Abstentions': 'sum',
        'Null': 'sum',
        'Choice A': 'sum',
        'Choice B': 'sum'
    })
    return region_counts.loc[:]


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    regions_geojson = gpd.read_file('data/regions.geojson')
    print(regions_geojson)
    print(referendum_result_by_regions)
    geo = pd.merge(referendum_result_by_regions, regions_geojson,
                   left_index=True, right_on="code", how="inner")
    # calculate rate
    print(geo)
    geo['ratio'] = geo['Choice A'] / (geo['Choice A'] + geo['Choice B'])
    # Plot the map
    geo.plot(column='ratio')

    # Return the GeoDataFrame with the 'ratio' column
    return gpd.GeoDataFrame({'name_reg': geo['name_reg'],
                             'ratio': geo['ratio']})


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
