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
    referendum = pd.read_csv('data/referendum.csv', delimiter=';')
    df_reg = pd.read_csv('data/regions.csv', delimiter=',')
    df_dep = pd.read_csv('data/departments.csv', delimiter=',')

    return referendum, df_reg, df_dep


def merge_regions_and_departments(df_reg, df_dep):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    """Merge regions and departments datasets and select specific columns."""
    # Merging using 'code' and 'region_code' as the keys
    merged_data = pd.merge(df_reg, df_dep, how='left', left_on='code',
                           right_on='region_code')

    # Renaming columns
    column_mapping = {'code_x': 'code_reg', 'name_x': 'name_reg',
                      'code_y': 'code_dep', 'name_y': 'name_dep'}
    merged_data = merged_data.rename(columns=column_mapping)

    # Selecting specific columns
    selected_columns = ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    merged_data = merged_data[selected_columns]

    return pd.DataFrame(merged_data)


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    # Liste des valeurs à supprimer
    french_abroad = ['ZA', 'ZB', 'ZC', 'ZD', 'ZM', 'ZN', 'ZP', 'ZS', 'ZW',
                     'ZX', 'ZZ']

    # Créer un masque booléen pour les lignes à conserver
    mask = ~referendum['Department code'].isin(french_abroad)

    # Sélectionner les lignes à conserver
    referendum_filtered = referendum[mask]

    # Harmonisation des codes de départements
    regs_and_deps = regions_and_departments.copy()
    regs_and_deps['code_dep'] = regions_and_departments['code_dep'].apply(
        lambda x: int(x) if x not in ('2A', '2B') else x)
    ref2 = referendum_filtered.copy()
    ref2['Department code'] = referendum_filtered['Department code'].apply(
        lambda x: int(x) if x not in ('2A', '2B') else x)

    # Fusion
    final_df = pd.merge(ref2, regs_and_deps,
                        left_on='Department code', right_on='code_dep',
                        how='left')

    return pd.DataFrame(final_df)


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    df_grouped = referendum_and_areas.groupby('code_reg').agg({
        'name_reg': 'first', 'Registered': 'sum', 'Abstentions': 'sum',
        'Null': 'sum', 'Choice A': 'sum', 'Choice B': 'sum'})

    return pd.DataFrame(df_grouped)


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    # Charger les données géographiques depuis le fichier GeoJSON
    geo_data = gpd.read_file('regions.geojson')

    # Fusionner les informations géographiques avec les résultats du référendum
    merged_data = pd.merge(geo_data, referendum_result_by_regions,
                           left_on='code', right_on='code_reg', how='inner')

    # Calculer le taux de 'Choice A' sur tous les bulletins exprimés
    merged_data['ratio'] = merged_data['Choice A'] / (merged_data['Choice A']
                                                      +
                                                      merged_data['Choice B'])
    # Afficher la carte
    merged_data.plot(column='ratio', cmap='coolwarm', legend=True)

    # Retourner le GeoDataFrame avec la colonne 'ratio'
    return merged_data[['name_reg', 'ratio']]


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
