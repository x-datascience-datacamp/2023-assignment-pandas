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
    referendum = pd.DataFrame(pd.read_csv("data/referendum.csv", sep=';'))
    regions = pd.DataFrame(pd.read_csv("data/regions.csv"))
    departments = pd.DataFrame(pd.read_csv("data/departments.csv"))
    return referendum, regions, departments


def convert_code(code):
    if code.isdigit():
        return int(code)
    else:
        return code


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    X = pd.merge(regions, departments,  left_on="code", right_on="region_code",
                 how="inner", suffixes=('_reg', '_dep'))
    return pd.DataFrame(X[['code_reg', 'name_reg', 'code_dep', 'name_dep']])


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum.drop(referendum[
        referendum['Department code'].str.startswith("Z")].index, inplace=True)
    referendum['Department code'] = referendum['Department code'].apply(
        convert_code)
    regions_and_departments['code_dep'] = regions_and_departments[
        'code_dep'].apply(convert_code)
    X = pd.merge(referendum, regions_and_departments,
                 left_on="Department code", right_on="code_dep")
    return pd.DataFrame(X)


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    regions = pd.DataFrame(pd.read_csv("data/regions.csv"))
    result = referendum_and_areas.groupby('code_reg').agg(
        {'Registered': 'sum', 'Abstentions': 'sum', 'Null': 'sum',
         'Choice A': 'sum', 'Choice B': 'sum'}).reset_index()
    result = pd.merge(result, regions[['code', 'name']], left_on='code_reg',
                      right_on='code', how='inner').set_index('code_reg')
    result = result[['name', 'Registered', 'Abstentions', 'Null', 'Choice A',
                    'Choice B']]
    result.columns = ['name_reg', 'Registered', 'Abstentions', 'Null',
                      'Choice A', 'Choice B']
    return result


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo_data = gpd.read_file('data/regions.geojson')
    merged_data = geo_data.merge(referendum_result_by_regions,
                                 left_on='code', right_on='code_reg',
                                 how='left')

    merged_data['ratio'] = merged_data['Choice A'] / (
        merged_data['Choice A'] + merged_data['Choice B'])
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    merged_data.plot(column='ratio', cmap='coolwarm', linewidth=0.8,
                     ax=ax, edgecolor='0.8', legend=True)
    plt.title('Referendum Results - Choice A Ratio', fontsize=16)
    ax.set_axis_off()
    plt.show()

    return gpd.GeoDataFrame(merged_data)


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
    plot_referendum_map(referendum_results)
