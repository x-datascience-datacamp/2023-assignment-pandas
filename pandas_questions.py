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
    regions_and_departments = pd.merge(regions, departments,
                                       how="right",
                                       left_on="code",
                                       right_on="region_code")
    regions_and_departments.drop(columns=[
        "id_x", "slug_x", "id_y", "region_code", "slug_y"], inplace=True)
    regions_and_departments.rename(columns={"name_x": "name_reg",
                                            "name_y": "name_dep",
                                            "code_x": "code_reg",
                                            "code_y": "code_dep"},
                                   inplace=True)

    return regions_and_departments


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    # change codes to match
    code_dep = regions_and_departments['code_dep']
    regions_and_departments['code_dep'][code_dep.str[0] == '0'] = code_dep[
        code_dep.str[0] == '0'].str[1]

    referendum_and_areas = pd.merge(referendum, regions_and_departments,
                                    how="left",
                                    left_on="Department code",
                                    right_on="code_dep")
    referendum_and_areas.dropna(inplace=True)

    return referendum_and_areas


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    referendum_result_by_regions = (referendum_and_areas
                                    .groupby(['code_reg', 'name_reg'],
                                             group_keys=True)
                                    [['Registered',
                                      'Abstentions',
                                      'Null',
                                      'Choice A',
                                      'Choice B']]
                                    .sum()
                                    .reset_index(level='name_reg'))

    return referendum_result_by_regions


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    # load the geographic data
    regions = gpd.read_file("data/regions.geojson")

    # merge the info
    referendum_result_by_regions_ = gpd.GeoDataFrame(
        pd.merge(referendum_result_by_regions,
                 regions,
                 how="right",
                 left_on="code_reg",
                 right_on="code")
        )

    # compute the ratio
    referendum_result_by_regions_['ratio'] = (referendum_result_by_regions_[
        'Choice A'] / (referendum_result_by_regions_['Choice A'] +
                       referendum_result_by_regions_['Choice B']))

    # plot the map (x and y axes should be the same scale)
    fig, ax = plt.subplots(figsize=(10, 10))
    referendum_result_by_regions_.plot(column='ratio',
                                       legend=True,
                                       ax=ax,
                                       legend_kwds={'label': "ratio"},
                                       cmap='RdBu_r')
    ax.set_aspect('equal', adjustable='box')
    ax.set_title("ratio of 'Choice A' over all expressed ballots")

    return referendum_result_by_regions_


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
