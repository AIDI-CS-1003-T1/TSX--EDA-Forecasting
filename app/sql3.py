import sqlite3
import pandas as pd


def db_create_table(df: pd.DataFrame, db_path: str, table_name: str, primary_key: str) -> None:
    """Create a table in a SQLite database from a DataFrame with a specified primary key.

    Args:
        df (pd.DataFrame): DataFrame to be stored in the database
        db_path (str): Path to the SQLite database file
        table_name (str): Name of the table to be created
        primary_key (str): Column to be set as the primary key

    Returns:
        None
    """

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create table with primary key
    columns = ', '.join([f'"{col}" TEXT' for col in df.columns])
    create_table_sql = f'CREATE TABLE IF NOT EXISTS "{table_name}" ({columns}, PRIMARY KEY("{primary_key}"))'
    cursor.execute(create_table_sql)

    # Insert data into the table
    df.to_sql(table_name, conn, if_exists="replace", index=False)

    conn.commit()
    conn.close()

def db_upsert(df, db_path, table_name, primary_keys):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create the table if it doesn't exist
    columns = ', '.join([f"{col} TEXT" for col in df.columns])
    primary_keys_str = ', '.join(primary_keys)
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            {columns},
            PRIMARY KEY ({primary_keys_str}))""")

    # Perform the UPSERT operation
    for index, row in df.iterrows():
        columns = ', '.join(row.index)
        placeholders = ', '.join(['?'] * len(row))
        update_placeholders = ', '.join([f"{col}=excluded.{col}" for col in row.index])
        cursor.execute(f"""
            INSERT INTO {table_name} ({columns})
            VALUES ({placeholders})
            ON CONFLICT({', '.join(primary_keys)}) DO UPDATE SET
            {update_placeholders}
        """, tuple(row))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def db_fetch_as_frame(db_path: str, query: str) -> pd.DataFrame:
    """
    Read data from a SQLite database.
    
    Args:
    db_path (str): Path to the SQLite database file
    table_name (str): Name of the table to be read
    
    Returns:
    pd.DataFrame: DataFrame containing the data from the table
    """
    conn = sqlite3.connect(db_path)
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def list_tables(db_path):
    """
    List the tables in a SQLite database.

    Args:
    db_path (str): Path to the SQLite database file

    Returns:
    list: List of tuples, each containing the name of a table in the database.
    """
    conn = sqlite3.connect(db_path)
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    conn.close()
    return tables


def get_table_info(db_path, table_name):

    """
    Get the column names and types of a table in a SQLite database, including the primary key.

    Args:
    db_path (str): Path to the SQLite database file
    table_name (str): Name of the table to get the column info for

    Returns:
    dict: Dictionary with keys 'columns' and 'primary_key'. 'columns' is a list of tuples, each containing the column name, data type, whether the column is nullable, whether it has a default value, and the default value. 'primary_key' is a list of columns that make up the primary key.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Query to get column names and types
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    # Extract primary key information
    primary_key = [col[1] for col in columns if col[5] > 0]
    
    conn.close()
    
    return {'columns': columns, 'primary_key': primary_key}




def create_new_table_query(df, db_path, table_name, primary_keys):
    import sqlite3

    # Generate the SQL for creating the table
    columns = ', '.join([f"{col} {dtype}" for col, dtype in zip(df.columns, df.dtypes)])
    primary_keys_str = ', '.join(primary_keys)
    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        {columns},
        PRIMARY KEY ({primary_keys_str})
    );
    """

    # Execute the SQL
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(create_table_sql)
    conn.commit()
    conn.close()



def execute_query(db_path, query):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    conn.close()







if __name__ == "__main__":

    pass
    

