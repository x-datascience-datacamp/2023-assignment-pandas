import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def load_data():
    """Load data from the CSV files referendum/regions/departments."""
    referendum = pd.read_csv("data/referendum.csv", sep=";")
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """

    regions.rename(columns={"code": "code_reg", "name": "name_reg"},
                   inplace=True)
    departments.rename(columns={"code": "code_dep", "name": "name_dep"},
                       inplace=True)
    merged = pd.merge(
        regions.drop(["id", "slug"], axis=1),
        departments.drop(["id", "slug"], axis=1),
        left_on="code_reg",
        right_on="region_code",
        how="inner",
    ).drop(["region_code"], axis=1)
    return merged


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    df = regions_and_departments
    df["code_dep"] = df["code_dep"].apply(
        lambda s: s.lstrip("0")
    )
    merged = pd.merge(
        referendum,
        regions_and_departments,
        left_on="Department code",
        right_on="code_dep",
        how="inner",
    )
    return merged


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    df = referendum_and_areas.drop(
        [
            "code_reg",
            "name_dep",
            "code_dep",
            "Town code",
            "Town name",
            "Department name",
            "Department code",
        ],
        axis=1,
    )
    df = df.groupby("name_reg").sum().reset_index()
    return df


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo_data = gpd.read_file(
        "data/regions.geojson"
    )

    merged_data = geo_data.merge(
        referendum_result_by_regions, left_on="nom", right_on="name_reg",
        how="left"
    )

    merged_data["ratio"] = merged_data["Choice A"] / (
        merged_data["Choice A"] + merged_data["Choice B"]
    )
    print(merged_data[["name_reg", "ratio"]])
    ax = merged_data.plot(column="ratio", cmap="Blues", legend=True,
                          figsize=(10, 8))
    ax.set_title("Referendum Results - Choice A Ratio")
    ax.set_axis_off()

    return merged_data


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
