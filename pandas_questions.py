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
    referendum = pd.read_csv("data/referendum.csv", sep=';')
    regions = pd.DataFrame(pd.read_csv("data/regions.csv", sep=','))
    departments = pd.DataFrame(pd.read_csv("data/departments.csv", sep=','))

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    df = pd.merge(regions[['code', 'name']],
                  departments[['region_code', 'code', 'name']],
                  how='left', right_on='region_code', left_on='code',
                  suffixes=['_reg', '_dep'])
    return pd.DataFrame(df[['code_reg', 'name_reg', 'code_dep', 'name_dep']])


def merge_referendum_and_areas(referendum, regions_and_departments):
    """
    Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    These lines are for those living abroad but this is not required
    referendum=referendum[~referendum['Department code'].str.contains('A')]
    referendum=referendum[~referendum['Department code'].str.contains('B')]
    """
    referendum = referendum[~referendum['Department code'].str.contains('Z')]
    referendum['Department code'].replace(["1", "2", "3", "4", "5", "6",
                                           "7", "8", "9"], ["01", "02", "03",
                                                            "04", "05",
                                                            "06", "07", "08",
                                                            "09"],
                                          inplace=True)
    df = referendum.merge(regions_and_departments, left_on='Department code',
                          right_on='code_dep')
    return df.dropna()


def compute_referendum_result_by_regions(referendum_and_areas):
    """
    Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    b = referendum_and_areas.set_index('code_reg')
    b = b[['name_reg', 'Registered', 'Abstentions', 'Null',
           'Choice A', 'Choice B']]
    b = b.groupby(['code_reg', 'name_reg']).sum().reset_index()
    return pd.DataFrame(b.set_index('code_reg'))


def plot_referendum_map(referendum_result_by_regions):
    """
    Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    regionss = gpd.read_file("data/regions.geojson")
    mer = pd.merge(referendum_result_by_regions, regionss, right_on='code',
                   left_index=True)
    mer['ratio'] = mer['Choice A']/(mer['Choice A']+mer['Choice B'])
    mer.plot(column='ratio')
    return gpd.GeoDataFrame(mer)


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
