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
    # Rename columns in the 'regions' DataFrame
    regions = regions.rename(columns={'code': 'code_reg', 'name': 'name_reg'})

    # Rename columns in the 'departments' DataFrame
    departments = departments.rename(
        columns={
            'region_code': 'code_reg', 'name': 'name_dep', 'code': 'code_dep'
        }
    )

    # Merge based on the 'code_reg' column
    merged_df = pd.merge(
        regions, departments,
        on='code_reg',
        how='inner'
    )

    # Select the desired columns
    result_df = merged_df[['code_reg', 'name_reg', 'code_dep', 'name_dep']]

    return result_df


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """

    referendum['Department code'] = referendum['Department code'].str.zfill(2)
    dep_to_exclude = [
        "ZZ", "ZX", "ZW", "ZS", "ZP", "ZN", "ZM", "ZD", "ZC", "ZB", "ZA"
    ]
    referendum = referendum.loc[
        ~referendum['Department code'].isin(dep_to_exclude)
    ]

    regions_to_exclude = ['COM', '01', '02', '03', '04', '06']
    regions_and_departments = regions_and_departments.loc[
        ~regions_and_departments['code_reg'].isin(regions_to_exclude)
    ]

    # Merge based on the common column, e.g., 'code_dep' or 'department_code'
    merged_df = pd.merge(
        referendum, regions_and_departments,
        left_on='Department code',
        right_on='code_dep',
        how='inner'
    )

    return merged_df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """

    # Group by 'code_reg' and aggregate the counts for each category)
    result_df = referendum_and_areas.groupby('code_reg').agg({
        'name_reg': 'first',  # Take the first name_reg
        'Registered': 'sum',
        'Abstentions': 'sum',
        'Null': 'sum',
        'Choice A': 'sum',
        'Choice B': 'sum'
    })

    return result_df


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    # Load geographic data
    regions_geojson = gpd.read_file('data/regions.geojson')

    # Merge referendum results with geographic data
    merged_data = pd.merge(
        regions_geojson,
        referendum_result_by_regions,
        left_on='code', right_on='code_reg', right_index=True,
        how='inner'
    )

    # Calculate the ratio of 'Choice A' over all expressed ballots
    merged_data['ratio'] = merged_data['Choice A'] / (merged_data['Choice A']
                                                      + merged_data['Choice B']
                                                      )

    gdf = gpd.GeoDataFrame(
        merged_data,
        crs="EPSG:4326"
    )

    gdf.plot(column="ratio", legend=True)

    return gdf


referendum, df_reg, df_dep = load_data()
regions_and_departments = merge_regions_and_departments(
    df_reg, df_dep
)
referendum_and_areas = merge_referendum_and_areas(
    referendum, regions_and_departments
)
referendum_result_by_regions = compute_referendum_result_by_regions(
    referendum_and_areas
)

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
