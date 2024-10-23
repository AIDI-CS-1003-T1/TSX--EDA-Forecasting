import sqlite3
import pandas as pd

pd.read_csv('../tsx_data.csv')



# create a connection to the database
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Connection to {db_file} successful")
    except Exception as e:
        print(e)
    return conn

create_connection('../data/stocks.db')

# create a table in the database

def create_table(conn, create_table_sql):
    # check if table exists
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='stocks'")