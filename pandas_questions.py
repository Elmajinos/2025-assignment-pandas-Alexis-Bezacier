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
    referendum = pd.read_csv('./data/referendum.csv', sep=';')
    regions = pd.read_csv('./data/regions.csv')
    departments = pd.read_csv('./data/departments.csv')

    return referendum, regions, departments

referendum, regions, departments = load_data()

def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.
    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    results = regions.merge(departments,
                            left_on = 'code',
                            right_on = 'region_code'
                            )
    
    remove_cols = ['id_x', 'slug_x','id_y', 'slug_y', 'region_code']

    results = results.rename(columns={'code_x' : 'code_reg', 'name_x' : 'name_reg', 'code_y' : 'code_dep', 'name_y' : 'name_dep'})
    results = results.drop(columns=remove_cols)

    return results
    
results = merge_regions_and_departments(regions, departments)
print(results.head())


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad, which all have a code that contains `Z`.

    DOM-TOM-COM departments are departements that are remote from metropolitan
    France, like Guadaloupe, Reunion, or Tahiti.
    """
    # First filter out referendum entries with 'Z' in Department code (french living abroad)
    referendum_metro = referendum[~referendum['Department code'].str.contains("Z", na=False)].copy()
    
    # Normalize department codes: add leading zero to single digit codes (except 2A and 2B)
    referendum_metro['Department code'] = referendum_metro['Department code'].apply(
        lambda x: x.zfill(2) if x not in ['2A', '2B'] else x
    )
    
    # Filter out DOM-TOM-COM departments from regions_and_departments
    regions_and_departments_metro = regions_and_departments[
        ~regions_and_departments['code_reg'].isin(['01', '02', '03', '04', '06', 'COM'])
    ]
    
    results_1 = regions_and_departments_metro.merge(
        referendum_metro, 
        left_on = 'code_dep',
        right_on ='Department code'
    )

    return results_1

ref = merge_referendum_and_areas(referendum, results)
print(ref.head())



def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    results = (
        referendum_and_areas
        .groupby(["code_reg"], as_index=True)
        .agg({
            "name_reg": "first",  
            "Registered": "sum",
            "Abstentions": "sum",
            "Null": "sum",
            "Choice A": "sum",
            "Choice B": "sum"
        })
    )

    return results

ref_2 = compute_referendum_result_by_regions(ref)
print(ref_2.head())

def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geographic_data = gpd.read_file('./data/regions.geojson')
    
    referendum_with_geo = geographic_data.merge(
        referendum_result_by_regions.reset_index(),
        left_on='code',
        right_on='code_reg'
    )

    referendum_with_geo['ratio'] = (
        referendum_with_geo['Choice A'] / 
        (referendum_with_geo['Registered'] - referendum_with_geo['Abstentions'] - referendum_with_geo['Null'])
    )
    
    referendum_with_geo.plot(column='ratio', cmap='RdYlGn', legend=True, 
                             edgecolor='black', figsize=(10, 10))
    plt.title('Referendum Results by Region - Choice A Rate')
    
    return referendum_with_geo


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
