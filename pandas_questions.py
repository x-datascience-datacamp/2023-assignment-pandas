"""Plotting referendum results in pandas.

In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using `geopandas`.
# """
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def load_data():
    """Load data from the CSV files referendum/regions/departments."""
    referendum = pd.read_csv('data/referendum.csv', sep=';')
    regions = pd.read_csv('data/regions.csv', sep=',')
    departments = pd.read_csv('data/departments.csv', sep=',')
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame."""
    regions.rename(columns={'code': 'code_reg', 'name': 'name_reg'},
                   inplace=True)
    departments.rename(columns={'code': 'code_dep', 'name': 'name_dep'},
                       inplace=True)
    merged_df = pd.merge(regions, departments,
                         left_on='code_reg', right_on='region_code')
    merged_df = merged_df[['code_reg', 'name_reg', 'code_dep', 'name_dep']]
    return merged_df


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad, which all have a code that contains `Z`.

    DOM-TOM-COM departments are departements that are remote from metropolitan
    France, like Guadaloupe, Reunion, or Tahiti.
    """
    referendum['Department code'] = referendum['Department code'].apply(
        lambda x: '0' + x if len(x) == 1 else x)
    merged_df = pd.merge(referendum, regions_and_departments,
                         left_on='Department code', right_on='code_dep')
    return merged_df
    return pd.DataFrame({})


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region."""
    referendum_and_areas = referendum_and_areas[
        ['code_reg', 'name_reg', 'Registered',
         'Abstentions', 'Null', 'Choice A', 'Choice B']]
    result = referendum_and_areas.groupby('code_reg').sum()
    result['name_reg'] = referendum_and_areas.groupby(
        'code_reg')['name_reg'].first()
    return result


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum."""
    geo_data = gpd.read_file('data/regions.geojson')
    merged = pd.merge(geo_data, referendum_result_by_regions,
                      left_on='code', right_on='code_reg')
    merged['ratio'] = merged['Choice A'] / (
        merged['Choice A'] + merged['Choice B'])
    merged = gpd.GeoDataFrame(merged)
    merged.plot(column='ratio', legend=True,
                legend_kwds={
                    'label': "Pourcentage de vote \"A\" au référendum"},
                cmap='OrRd_r')
    plt.title('Résultats du référendum par région')
    plt.savefig('figures/referendum_map.png')
    return merged


if __name__ == "__main__":
    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(df_reg, df_dep)
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments)
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas)
    print(referendum_results)
    plot_referendum_map(referendum_results)
    plt.show()