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
    # Renaming columns to do the merge
    regions = regions.rename(columns={"code": "code_reg", "name": "name_reg"})
    departments = departments.rename(
        columns={"region_code": "code_reg",
                 "code": "code_dep", "name": "name_dep"}
    )
    # Merging
    merged_df = pd.merge(regions, departments, on="code_reg")
    # Column selection
    merged_df = merged_df[["code_reg", "name_reg", "code_dep", "name_dep"]]
    return merged_df


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    # Adding a 0 in front of the single number departments codes
    referendum["Department code"] = referendum["Department code"].apply(
        lambda x: "0" + str(x) if len(str(x)) == 1 else str(x)
    )
    # Merging
    referendum_and_areas = pd.merge(
        referendum,
        regions_and_departments,
        left_on="Department code",
        right_on="code_dep",
    )
    return referendum_and_areas


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    # Column selection
    name_reg = referendum_and_areas[["code_reg", "name_reg"]]
    referendum_and_areas = referendum_and_areas[
        ["code_reg", "Registered", "Abstentions", "Null",
         "Choice A", "Choice B"]
    ]
    # Grouping by regions
    results_computation = referendum_and_areas.groupby("code_reg").sum()
    name_reg = name_reg.drop_duplicates()
    # Merging
    referendum_by_regions = pd.merge(
        name_reg, results_computation, on="code_reg"
    )
    # Indexing code_reg
    referendum_by_regions = referendum_by_regions.set_index("code_reg")
    return referendum_by_regions


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    # Load the geographic data with geopandas from `regions.geojson`.
    geo_data = gpd.read_file("data/regions.geojson")
    # Merge these info into `referendum_result_by_regions`.
    merged_df = pd.merge(
        geo_data, referendum_result_by_regions,
        left_on="code", right_on="code_reg"
    )
    # Calculation of rate of "Choice A"
    merged_df["ratio"] = merged_df["Choice A"] / (
        merged_df["Choice A"] + merged_df["Choice B"]
    )
    # Use the method `GeoDataFrame.plot` to display the result map.
    merged_df.plot(column="ratio", legend=True)

    return merged_df


if __name__ == "__main__":
    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(df_reg, df_dep)
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas)
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()
