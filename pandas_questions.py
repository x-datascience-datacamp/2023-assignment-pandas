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

    def add_leading_zero(code):
        if len(str(code)) == 1:  # Check if the code is a single digit
            return '0' + str(code)  # Add a leading zero to single-digit codes
        else:
            return code  # Keep the original code for other cases

# Applying the function to the "Department code" column
    referendum['Department code'] = referendum['Department code'].apply(
        add_leading_zero
        )
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    return regions.merge(
        departments,
        left_on='code',
        right_on='region_code',
        suffixes=('_reg', '_dep')
        )[['code_reg', 'name_reg', 'code_dep', 'name_dep']]


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    merged_data = referendum.merge(
        regions_and_departments,
        left_on='Department code',
        right_on='code_dep'
    )

    # Dropping rows with missing values after the join
    merged_data.dropna(inplace=True)

    return merged_data


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    tmp = referendum_and_areas.groupby(
        ['code_reg', 'name_reg'],
        as_index=False
        )[['Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']].sum()
    tmp.set_index('code_reg', inplace=True)
    return tmp


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo_data = gpd.read_file('data/regions.geojson')

    merged_data = referendum_result_by_regions.merge(
        geo_data,
        left_index=True,
        right_on='code'
        )

    merged_data['ratio'] = merged_data['Choice A']
    merged_data['ratio'] /= (merged_data['Choice A'] + merged_data['Choice B'])

    merged_data = gpd.GeoDataFrame(merged_data, geometry='geometry')
    # Plot the map
    ax = merged_data.plot(column='ratio', legend=True)

    # Customize plot
    ax.set_axis_off()
    ax.set_title('Referendum Results by Region')

    # Show the plot
    plt.show()

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
