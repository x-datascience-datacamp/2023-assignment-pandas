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
    final_df = departments.merge(
        regions, left_on="region_code", right_on="code", how="left"
    ).rename(
        columns={
            "code_x": "code_dep",
            "name_x": "name_dep",
            "code_y": "code_reg",
            "name_y": "name_reg",
        }
    )[
        ["code_reg", "name_reg", "code_dep", "name_dep"]
    ]
    return final_df


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum = referendum[
        ~(referendum["Department name"] == "FRANCAIS DE L'ETRANGER")
    ]
    to_remove = [
        "Guadeloupe",
        "Martinique",
        "Guyane",
        "La Réunion",
        "Mayotte",
        "Collectivités d'Outre-Mer",
    ]
    dep_to_drop = ["ZA", "ZB", "ZC", "ZD", "ZM", "ZN", "ZP", "ZS", "ZW", "ZX"]
    regions_and_departments = regions_and_departments[
        ~regions_and_departments["name_reg"].isin(to_remove)
    ]
    referendum = referendum[~referendum["Department code"].isin(dep_to_drop)]
    referendum["Department code"] = referendum["Department code"].apply(
        lambda x: int(x) if x.isdigit() else str(x)
    )
    regions_and_departments["code_dep"] = \
        regions_and_departments["code_dep"].apply(
        lambda x: int(x) if x.isdigit() else str(x)
    )
    output = referendum.merge(
        regions_and_departments,
        left_on="Department code",
        right_on="code_dep",
        how="outer",
    ).dropna()
    return output


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    grouped = referendum_and_areas.groupby(["code_reg", "name_reg"])
    result = grouped[
        ["Registered", "Abstentions", "Null", "Choice A", "Choice B"]
    ].sum()
    return result.reset_index().drop("code_reg", axis=1)


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    gdf_regions = gpd.read_file("data/regions.geojson")
    merged_gdf = gdf_regions.merge(
        referendum_result_by_regions, left_on="nom", right_on="name_reg"
    )
    expressed_ballots = (
        merged_gdf["Registered"] -
        merged_gdf["Abstentions"] - merged_gdf["Null"]
    )
    merged_gdf["ratio"] = merged_gdf["Choice A"] / expressed_ballots
    merged_gdf.plot(column="ratio", legend=True)
    plt.show()
    return merged_gdf


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
