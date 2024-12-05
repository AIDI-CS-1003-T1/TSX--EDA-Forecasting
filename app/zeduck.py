# import duckdb
import duckdb
import pandas as pd

dir(duckdb)

# create a duckdb file
con = duckdb.connect('../data/duckdata.duckdb')

con.register('tsx_data', pd.read_csv('../tsx_data.csv'))

# create a function that adds df as table in the duckdb file
def create_table(df:pd.DataFrame, db_path:str,table_name:str):
    """
    Create a table in a duckdb database from a DataFrame.
    
    Args:
    df (pd.DataFrame): DataFrame to be stored in the database
    db_path (str): Path to the duckdb database file
    table_name (str): Name of the table to be created

    Returns:
    None
    """
    con = duckdb.connect(db_path)
    con.register(table_name, df)
    con.exe
    con.close()



df=pd.read_excel("https://github.com/Vimalraj2506/Auto_forecast/raw/refs/heads/main/Data_cleaned.xlsx")


dtale.show(df).open_browser()

df['Frame No'].isna().sum()