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
    referendum = pd.read_csv('data/referendum.csv', delimiter=';')
    regions = pd.read_csv('data/regions.csv')
    departments = pd.read_csv('data/departments.csv')
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    merged_df = pd.merge(
        departments,
        regions,
        left_on='region_code',
        right_on='code',
        suffixes=('_dep', '_reg')
    )
    return merged_df[['code_reg', 'name_reg', 'code_dep', 'name_dep']]


def merge_referendum_and_areas(referendum, regions_depart):
    """Merge referendum and regions_and_departments in one DataFrame.
    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    regions_depart["code_dep"] = regions_depart["code_dep"].str.lstrip("0")
    merged_df = pd.merge(
        referendum,
        regions_depart,
        left_on='Department code',
        right_on='code_dep'
    )
    mask = merged_df["Department name"].isin(
        [
            "GUADELOUPE",
            "MARTINIQUE",
            "GUYANE",
            "LA REUNION",
            "MAYOTTE",
            "NOUVELLE CALEDONIE",
            "POLYNESIE FRANCAISE",
            "SAINT PIERRE ET MIQUELON",
            "WALLIS-ET-FUTUNA",
            "SAINT-MARTIN/SAINT-BARTHELEMY",
            "FRANCAIS DE L'ETRANGER",
        ]
    )
    merged_df = merged_df.loc[~mask]
    merged_df.dropna(inplace=True)
    return merged_df



def compute_referendum_result_by_regions(referendum_and_areas):
    referendum_result = (
        referendum_and_areas.groupby('code_reg').agg({
        'name_reg': 'first', 'Registered': 'sum', 'Abstentions': 'sum',
        'Null': 'sum', 'Choice A': 'sum', 'Choice B': 'sum'
        }))
    return referendum_result


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
    should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo_data = gpd.read_file('data/regions.geojson')
    geo_data = geo_data.merge(
        referendum_result_by_regions,
        left_on="code",
        right_index=True,
    )
    geo_data["expressed"] = (geo_data["Choice A"] + geo_data["Choice B"])
    geo_data["ratio"] = (geo_data["Choice A"] / geo_data["expressed"])
    f, ax = plt.subplots()
    geo_data.plot(
        "ratio",
        ax=ax,
        legend=True,
        cmap="OrRd",
    )
    f.suptitle("Ratio of Choice A over all expressed ballots")
    return geo_data


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
