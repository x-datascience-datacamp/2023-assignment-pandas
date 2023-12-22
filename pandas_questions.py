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
    """Charge les données à partir des fichiers CSV pour le référendum, les régions et les départements."""
    referendum = pd.read_csv('data/referendum.csv', sep = ';')
    regions = pd.read_csv('data/regions.csv', sep = ',')
    departments = pd.read_csv('data/departments.csv', sep = ',')
    
    return referendum, regions, departments

referendum, regions, departments = load_data()




def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    #Rename regions

    regions = regions.drop(columns = ['slug','id'])
    regions = regions.rename(columns = {'name':'name_reg'})
    regions = regions.rename(columns = {'code':'code_reg'})

    #Rename departments

    departments = departments.drop(columns = ['slug','id'])
    departments = departments.rename(columns = {'name':'name_dep'})
    departments = departments.rename(columns = {'code':'code_dep'})
    departments = departments.rename(columns = {'region_code':'code_reg'})

    #mERGE
    
    RegDep = regions.merge(departments, on = 'code_reg', how = 'left')

    return RegDep


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum = referendum.rename(columns = {'Department code':'code_dep'})
    referendum = referendum.rename(columns = {'Department name':'name_dep'})

    MergeRRD = regions_and_departments.merge(referendum, on = 'code_dep')


    return MergeRRD


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """

    Somme_reg = referendum_and_areas.groupby(by="name_reg").sum()
    Somme_reg = Somme_reg.drop(columns = 'Town code')


    return Somme_reg


import geodatasets
import geopandas

def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    France = geopandas.read_file("data/regions.geojson")
    France = France.rename(columns = {'nom': 'name_reg'})
    Mergemaps = France.merge(referendum_result_by_regions, on = 'name_reg')
    
    return Mergemaps.plot(column="Choice A", legend=True)


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
