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
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions.rename(columns={"code": "region_code"}, inplace=True)
    regionsEtdepartments = pd.merge(
        departments, regions, how="inner", on=["region_code"]
    )
    regionsEtdepartments.rename(
        columns={
            "code": "code_dep",
            "name_x": "name_dep",
            "name_y": "name_reg",
            "region_code": "code_reg",
        },
        inplace=True,
    )
    regionsEtdepartments = regionsEtdepartments.loc[
        :, ["code_reg", "name_reg", "code_dep", "name_dep"]
    ]
    return regionsEtdepartments


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum.rename(columns={"Department code": "code_dep"}, inplace=True)

    regions_and_departments["code_dep"] = regions_and_departments[
        "code_dep"].str.lstrip("0")

    referendumAreas = pd.merge(
        referendum, regions_and_departments, how="left", on=["code_dep"])

    referendumAreas.rename(columns={"code_dep": "Department code"},
                           inplace=True)

    referendumAreas = referendumAreas[
        ~referendumAreas["Department code"].str.contains("Z")
    ]
    referendumAreas["code_dep"] = referendumAreas["Department code"]
    referendumAreas = referendumAreas.loc[:, ["Department code",
                                              "Department name",
                                              "Town code",
                                              "Town name",
                                              "Registered",
                                              "Abstentions",
                                              "Null",
                                              "Choice A",
                                              "Choice B",
                                              "code_dep",
                                              "code_reg",
                                              "name_reg",
                                              "name_dep"]]
    referendumAreas.dropna(inplace=True)
    return referendumAreas


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    computed = referendum_and_areas.loc[:, ['code_reg', 'name_reg',
                                            'Registered',
                                            'Abstentions', 'Null',
                                            'Choice A', 'Choice B']]

    computed = computed.groupby(by=['code_reg']).sum().sort_values('name_reg')
    computed['name_reg'] = referendum_and_areas[
        'name_reg'].sort_values().unique()

    return computed


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    baseCarte = gpd.read_file('data/regions.geojson')
    carte = pd.merge(baseCarte, referendum_result_by_regions.rename(
                    columns={'name_reg': 'nom'}, inplace=False), how='left',
                    on=['nom']
                    )
    carte['ratio'] = carte['Choice A']/(carte['Choice A'] + carte['Choice B'])

    carte['name_reg'] = carte['nom']
    carte.dropna(inplace=True)
    # carte.plot('ratio', legend = True)

    return carte


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
