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
    dir_path = "./data/"
    referendum = pd.read_csv(
        dir_path + "referendum.csv", on_bad_lines="skip", delimiter=";"
    )
    regions = pd.read_csv(dir_path + "regions.csv", on_bad_lines="skip")
    departments = pd.read_csv(dir_path + "departments.csv",
                              on_bad_lines="skip")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    df = regions[["code", "name"]].merge(
        departments[["code", "region_code", "name"]],
        left_on=["code"],
        right_on=["region_code"],
    )

    df.drop(columns=["region_code"], inplace=True)
    df.columns = ["code_reg", "name_reg", "code_dep", "name_dep"]

    return df


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    idx = referendum[referendum["Department code"].str.startswith("Z")].index
    referendum_t = referendum.drop(idx)

    referendum_t["Department code"] = [
        x if len(x) > 1 else ("0" + x)
        for _i, x in enumerate(referendum_t["Department code"])
    ]

    referendum_and_areas = referendum_t.merge(
        regions_and_departments,
        left_on=["Department code"],
        right_on=["code_dep"],
    )

    return referendum_and_areas


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    cols = [
        "code_reg",
        "name_reg",
        "Registered",
        "Abstentions",
        "Null",
        "Choice A",
        "Choice B",
    ]
    referendum_result_by_regions = (
        referendum_and_areas[cols].groupby(["code_reg", "name_reg"]).sum()
    )
    referendum_result_by_regions.reset_index(inplace=True)
    referendum_result_by_regions.set_index("code_reg", inplace=True, drop=True)
    return referendum_result_by_regions


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    path = "./data/regions.geojson"
    df_json = gpd.read_file(path)

    merged_gdf = referendum_result_by_regions.merge(
        df_json, left_on=["code_reg"], right_on=["code"]
    )

    # Calculate the ratio of 'Choice A' over all expressed ballots
    merged_gdf["ratio"] = merged_gdf["Choice A"] / (
        merged_gdf["Choice A"] + merged_gdf["Choice B"]
    )

    result_gdf = gpd.GeoDataFrame(merged_gdf, geometry="geometry")

    # Plot the map using GeoDataFrame.plot
    _ = result_gdf.plot(column="ratio",
                        cmap="viridis",
                        legend=True,
                        figsize=(10, 8))

    # Add a title
    plt.title("Referendum Results: Ratio of Choice A")

    # Show the plot
    plt.show()

    return result_gdf


if __name__ == "__main__":
    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(df_reg, df_dep)
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()
