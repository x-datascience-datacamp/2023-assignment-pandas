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
    merged_data = pd.merge(regions, departments, left_on='code',
                           right_on='region_code', how='left')
    results = merged_data[['code_x', 'name_x', 'code_y', 'name_y']]
    results.columns = ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    return results


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum['Department code'] = (referendum['Department code']
                                     .astype(str).str
                                     .zfill(2))  # Replace code 1 with 01
    merged_data = pd.merge(referendum, regions_and_departments,
                           left_on='Department code',
                           right_on='code_dep', how='left')
    filtered_data = (merged_data[~merged_data['code_reg']
                                 .isin(['TOM', 'DOM', 'COM'])])
    filtered_data = (filtered_data
                     .dropna(subset=['code_dep']))  # drop French a l'etrangé

    return filtered_data


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    results = referendum_and_areas.groupby(['code_reg', 'name_reg']).agg(
        Registered=('Registered', 'sum'),
        Abstentions=('Abstentions', 'sum'),
        Null=('Null', 'sum'),
        Choice_A=('Choice A', 'sum'),
        Choice_B=('Choice B', 'sum')
    ).reset_index().set_index('code_reg')
    results.columns = ['name_reg', 'Registered',
                       'Abstentions', 'Null',
                       'Choice A', 'Choice B'
                       ]
    return results


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    gdf = gpd.read_file('data/regions.geojson')
    merged_df = pd.merge(gdf, referendum_result_by_regions,
                         left_on='code', right_on='code_reg',
                         how='left')
    merged_df['Total expressed'] = (merged_df[['Choice A', 'Choice B']]
                                    .sum(axis=1))
    merged_df['ratio'] = merged_df['Choice A'] / merged_df['Total expressed']
    merged_df.drop('Total expressed', axis=1, inplace=True)
    gdf_for_plot = gpd.GeoDataFrame(merged_df, geometry='geometry')

    gdf_for_plot.plot(column='ratio',
                      cmap='coolwarm', legend=True,
                      figsize=(10, 8))

    plt.title('Rate of Choice A over Total Expressed Ballots')

    return merged_df


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
