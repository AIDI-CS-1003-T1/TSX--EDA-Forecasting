import sqlite3
import pandas as pd


# create a function to create a table in .db file inputs are df and db path
def create_table(df:pd.DataFrame, db_path:str,table_name:str) -> None:
    """
    Create a table in a SQLite database from a DataFrame.
    
    Args:
    df (pd.DataFrame): DataFrame to be stored in the database
    db_path (str): Path to the SQLite database file
    table_name (str): Name of the table to be created

    Returns:
    None


    """

    conn = sqlite3.connect(db_path)
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.commit()
    conn.close()


# upsert function for the db

import sqlite3
import pandas as pd

import sqlite3
import pandas as pd

def db_upsert(df: pd.DataFrame, db_path: str, table_name: str, primary_keys: list) -> None:
    """
    Update or insert data in a SQLite database from a DataFrame.
    
    Args:
    df (pd.DataFrame): DataFrame to be upserted into the database
    db_path (str): Path to the SQLite database file
    table_name (str): Name of the table to be upserted
    primary_keys (list): List of primary key columns
    
    Returns:
    None
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create a temporary table
    temp_table_name = f"{table_name}_temp"
    df.to_sql(temp_table_name, conn, if_exists='replace', index=False)
    
    # Construct the columns and update_columns strings
    columns = ', '.join(df.columns)
    update_columns = ', '.join([f"{col}=excluded.{col}" for col in df.columns if col not in primary_keys])
    
    # Construct the ON CONFLICT clause
    conflict_clause = ', '.join(primary_keys)
    
    upsert_query = f"""
    INSERT INTO {table_name} ({columns})
    SELECT {columns} FROM {temp_table_name}
    ON CONFLICT({conflict_clause}) DO UPDATE SET {update_columns};
    """
    
    cursor.execute(upsert_query)
    conn.commit()
    
    # Drop the temporary table
    cursor.execute(f"DROP TABLE {temp_table_name}")
    conn.commit()
    
    conn.close()

# Example usage
db_path = "../data/stocks.db"
df = pd.read_csv("../tsx_data.csv")
df.rename(columns={'Unnamed: 0': 'Date'}, inplace=True)
df.to_csv("../tsx_data.csv", index=False)

# Perform upsert with single primary key
db_upsert(df, db_path, 'tsx_data', ['id'])

# Perform upsert with composite primary key
db_upsert(df, db_path, 'tsx_data', ['id', 'Date'])



# createa function that lists the tables in the db
def list_tables(db_path):
    conn = sqlite3.connect(db_path)
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    conn.close()
    return tables




def get_table_info(db_path, table_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Query to get column names and types
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    conn.close()
    
    return columns

# Example usage
db_path = "../data/stocks.db"
table_name = "tsx_data"
get_table_info(db_path, table_name)





if __name__ = "__main__":
    pass
    return None

