"""Plotting referendum results in pandas.

In short, we want to make a beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as a pandas.DataFrame, merge the info and
aggregate them by regions, and finally plot them on a map using `geopandas`.
"""
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def load_data():
    """Load data from the CSV files referendum/regions/departments."""
    referendum = pd.DataFrame({})
    regions = pd.DataFrame({})
    departments = pd.DataFrame({})

    referendum = pd.read_csv("data/referendum.csv", sep=";")
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments into one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    merged_df = pd.merge(
        regions, departments,
        how="inner", 
        left_on="code", 
        right_on="region_code"
    )

    # Select and rename the desired columns
    merged_df = merged_df[["code_x", "name_x", "code_y", "name_y"]]
    merged_df = merged_df.rename(
        columns={
            "code_x": "code_reg",
            "name_x": "name_reg",
            "code_y": "code_dep",
            "name_y": "name_dep",
        }
    )

    return merged_df


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    French living abroad.
    """
    # Remove leading zeros from 'code_dep' column
    regions_and_departments["code_dep"] = (
        regions_and_departments["code_dep"].astype(str).str.lstrip("0")
    )

    # Merge the DataFrames on appropriate columns
    merged_df = pd.merge(
        referendum,
        regions_and_departments,
        how="inner",
        left_on=["Department code"],
        right_on=["code_dep"],
    )

    # Drop lines relative to DOM-TOM-COM departments and French living abroad
    merged_df = merged_df[
        ~merged_df["Department name"]
        .isin(
            ["COM", "01", "02", "03", "04", "05", "06"]
            )
    ]

    return merged_df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    # Group by 'code_reg' and aggregate the counts for each region
    result_by_regions = (
        referendum_and_areas.groupby("code_reg")
        .agg(
            {
                "name_reg": "first",
                "Registered": "sum",
                "Abstentions": "sum",
                "Null": "sum",
                "Choice A": "sum",
                "Choice B": "sum",
            }
        )
        .reset_index()
    )

    # Set 'code_reg' as the index
    result_by_regions.set_index("code_reg", inplace=True)

    return result_by_regions


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    # Load geographic data from regions.geojson
    geo_data = gpd.read_file("data/regions.geojson")

    # Merge with referendum_result_by_regions on 'code_reg'
    merged_data = pd.merge(
        geo_data,
        referendum_result_by_regions,
        how="inner",
        left_on="code",
        right_index=True,
    )

    # Calculate the ratio of 'Choice A' over all expressed ballots
    merged_data["ratio"] = merged_data["Choice A"] / (
        merged_data["Choice A"] + merged_data["Choice B"]
    )

    # Plot the map
    merged_data.plot(
        column="ratio", cmap="coolwarm", legend=True, figsize=(10, 8)
        )

    # Set plot title
    plt.title("Referendum Results - Choice A Ratio")

    # Show the plot
    plt.show()

    return merged_data


if __name__ == "__main__":
    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(df_reg, df_dep)
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(referendum_and_areas)
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()