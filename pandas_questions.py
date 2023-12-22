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
    referendum_data_path = "data/referendum.csv"
    regions_data_path = "data/regions.csv"
    departments_data_path = "data/departments.csv"
    referendum = pd.read_csv(referendum_data_path, sep=";")
    regions = pd.read_csv(regions_data_path, sep=",")
    departments = pd.read_csv(departments_data_path, sep=",")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    merged_data = pd.merge(regions, departments,
                           how="right",
                           left_on="code",
                           right_on="region_code")
    merged_data.rename(columns={"name_x": "name_reg",
                                "name_y": "name_dep",
                                "code_x": "code_reg",
                                "code_y": "code_dep"},
                       inplace=True)
    columns_to_keep = ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    regions_and_departments = merged_data[columns_to_keep]
    return regions_and_departments


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad, which all have a code that contains `Z`.

    DOM-TOM-COM departments are departements that are remote from metropolitan
    France, like Guadaloupe, Reunion, or Tahiti.
    """
    referendum_merge_key = "Department code"
    area_merge_key = "code_dep"
    # Dropping each line if "department code" column starts with a "Z"
    referendum = referendum[~referendum[referendum_merge_key]
                            .str.startswith('Z')]
    # Merging the data
    referendum_and_areas = pd.merge(referendum, regions_and_departments,
                                    how="left",
                                    left_on=referendum_merge_key,
                                    right_on=area_merge_key)
    return referendum_and_areas


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    # Pivot the DataFrame to get counts for each voter_status
    pivot_table = referendum_and_areas.pivot_table(
                                        index=['code_reg', 'name_reg'],
                                        values=['Registered',
                                                'Abstentions',
                                                'Null',
                                                'Choice A',
                                                'Choice B'],
                                        aggfunc='sum',
                                        fill_value=0)
    # Reset index to make 'code_reg' a column
    pivot_table.reset_index(inplace=True)
    # Reorder columns
    result_by_region = pivot_table[['code_reg', 'name_reg',
                                    'Registered', 'Abstentions',
                                    'Null', 'Choice A', 'Choice B']]
    return result_by_region


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    # Load geographic data from regions.geojson
    geo_data = gpd.read_file('regions.geojson')
    # Merge geographic data with referendum results
    merged_data = geo_data.merge(referendum_result_by_regions,
                                 left_on='code_reg',
                                 right_on='code_reg',
                                 how='left')
    # Calculate the ratio of 'Choice A' over all expressed ballots
    denom = (merged_data['Choice A'] +
             merged_data['Choice B'] +
             merged_data['Null'])
    merged_data['ratio'] = merged_data['Choice A'] / denom
    # Plot the choropleth map
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    merged_data.plot(column='ratio',
                     cmap='Blues',
                     linewidth=0.8,
                     ax=ax,
                     edgecolor='0.8',
                     legend=True)
    ax.set_title('Referendum Results: Choice A ratio')
    # Display the map
    plt.show()
    # Return the GeoDataFrame with the calculated ratio
    return merged_data


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
