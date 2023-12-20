"""Plotting referendum results in pandas.

In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/2023-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using `geopandas`.
"""
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.read_csv("./data/referendum.csv", sep=";")
    regions = pd.read_csv("./data/regions.csv")
    departments = pd.read_csv("./data/departments.csv")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions_tomerge = regions[["code", "name"]]
    regions_tomerge = regions_tomerge.rename(
        columns={"code": "code_reg", "name": "name_reg"}
        )
    departments_tomerge = departments[["region_code", "code", "name"]]
    departments_tomerge = departments_tomerge.rename(
        columns={"region_code": "code_reg",
                 "code": "code_dep",
                 "name": "name_dep"}
        )
    reg_and_dep = pd.merge(regions_tomerge,
                           departments_tomerge,
                           on="code_reg")
    return reg_and_dep


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum['Department code'] = referendum['Department code'].apply(
        lambda x: '0' + x if len(x) == 1 else x)
    dep_name = referendum["Department name"]
    dom = (dep_name != "DOM")
    tom = (dep_name != "TOM")
    com = (dep_name != "COM")
    etr = (dep_name != "FRANCAIS DE L'ETRANGER")
    bool_ind = dom & tom & com & etr

    referendum_tomerge = referendum.loc[bool_ind, :]
    referendum_tomerge = referendum_tomerge[
        referendum_tomerge["Department code"] <= "95"
        ]
    referendum_tomerge = referendum_tomerge.rename(
        columns={"Department code": "code_dep", "Department name": "name_dep"}
        )

    merged = pd.merge(referendum_tomerge,
                      regions_and_departments,
                      on="code_dep")
    merged["Department code"] = merged["code_dep"]
    return merged.rename(columns={"name_dep_x": "name_dep",
                                  "name_dep_y": "Department name"})


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    cols = ['code_reg', 'name_reg', 'Registered', 'Abstentions',
            'Null', 'Choice A', 'Choice B']
    ref_and_ar_togroup = referendum_and_areas.loc[:, cols]
    ref_and_ar_grouped = ref_and_ar_togroup.groupby(
        ["code_reg", "name_reg"]
        ).sum()
    return ref_and_ar_grouped.reset_index("name_reg")


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo_data = gpd.read_file("./data/regions.geojson")
    geo_data = geo_data.rename(columns={"code": "code_reg", "nom": "name_reg"})
    geo_ref = gpd.GeoDataFrame(
        pd.merge(
            referendum_result_by_regions, geo_data, on=["code_reg", "name_reg"]
            )
        )
    geo_ref.plot(column="Choice A", legend=True).set_title(
        "Votes for Choice A across France"
        )
    vote_sum = (geo_ref["Choice B"]+geo_ref["Choice A"])
    geo_ref["ratio"] = geo_ref["Choice A"] / vote_sum
    return gpd.GeoDataFrame(geo_ref)


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
