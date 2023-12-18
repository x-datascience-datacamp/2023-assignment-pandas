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
import os


def find(name, path):
    """Find a file in a directory."""
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    referendum_path = find("referendum.csv", "../")
    region_path = find("regions.csv", "../")
    department_path = find("departments.csv", "../")
    referendum = pd.read_csv(referendum_path, sep=";")
    regions = pd.read_csv(region_path, sep=",")
    departments = pd.read_csv(department_path, sep=",")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    df = pd.merge(departments, regions, left_on="region_code",
                  right_on="code", how="inner")
    df = df[["region_code", "name_y", "code_x", "name_x"]]
    df.rename(columns={"region_code": "code_reg",
                       "name_y": "name_reg",
                       "code_x": "code_dep",
                       "name_x": "name_dep"}, inplace=True)
    return df


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    new_code_dep = regions_and_departments["code_dep"].str.lstrip('0')
    regions_and_departments["code_dep"] = new_code_dep
    df = pd.merge(referendum, regions_and_departments,
                  left_on="Department code",
                  right_on="code_dep", how="inner")
    return df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    df = referendum_and_areas[['code_reg', 'name_reg', 'Registered',
                               'Abstentions', 'Null', 'Choice A', 'Choice B']]
    df = df.groupby(["code_reg", "name_reg"]).sum()
    df = df.reset_index(level=1)
    return df


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geojson_path = find("regions.geojson", "../")
    geo_data = gpd.read_file(geojson_path)

    merged_data = pd.merge(geo_data, referendum_result_by_regions,
                           left_on="code",
                           right_index=True, how="inner")
    numerator = merged_data['Choice A']
    denominator = merged_data['Choice A'] + merged_data['Choice B']
    merged_data['ratio'] = numerator / denominator
    ax = merged_data.plot(column='ratio', cmap='viridis',
                          legend=True, figsize=(10, 10))
    ax.set_title("Referendum Results - Choice A Ratio")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")

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
