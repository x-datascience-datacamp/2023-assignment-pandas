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
    referendum = pd.DataFrame({})
    regions = pd.DataFrame({})
    departments = pd.DataFrame({})
    referendum = pd.read_csv("./data/referendum.csv", sep=";")
    regions = pd.read_csv("./data/regions.csv", sep=",")
    departments = pd.read_csv("./data/departments.csv", sep=",")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    res = pd.merge(
        left=regions,
        right=departments,
        left_on="code",
        right_on="region_code",
        suffixes=("_reg", "_dep"),
    )[["code_reg", "name_reg", "code_dep", "name_dep"]]

    return res


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    fr_out = ["ZA", "ZB", "ZC", "ZD", "ZM", "ZN", "ZP", "ZS", "ZW", "ZX", "ZZ"]

    # Créer un masque booléen pour les lignes à conserver
    mask = ~referendum["Department code"].isin(fr_out)

    # Sélectionner les lignes à conserver
    referendum_filtered = referendum[mask]
    referendum_filtered["Department code"] = referendum_filtered[
        "Department code"
    ].apply(lambda x: "{0:0>2}".format(x))

    ref_reg_dep = pd.merge(
        left=referendum_filtered,
        right=regions_and_departments,
        left_on="Department code",
        right_on="code_dep",
    )

    return ref_reg_dep.dropna()


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    referendum_and_areas_copy = referendum_and_areas.copy()
    data = referendum_and_areas_copy.groupby("code_reg", as_index=True).agg(
        {
            "name_reg": "min",
            "Registered": "sum",
            "Abstentions": "sum",
            "Null": "sum",
            "Choice A": "sum",
            "Choice B": "sum",
        }
    )

    return data


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    carte_regions = gpd.read_file("./data/regions.geojson")
    df_tot = pd.merge(
        left=carte_regions,
        right=referendum_result_by_regions,
        left_on="nom",
        right_on="name_reg",
    )
    a = df_tot["Choice A"]
    b = df_tot["Choice B"]
    df_tot["ratio"] = a / (a + b)
    df_tot.plot(column="ratio", cmap="coolwarm", legend=True)

    return df_tot


if __name__ == "__main__":
    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(df_reg, df_dep)
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    ref_results = compute_referendum_result_by_regions(referendum_and_areas)
    print(ref_results)

    plot_referendum_map(ref_results)
    plt.show()
