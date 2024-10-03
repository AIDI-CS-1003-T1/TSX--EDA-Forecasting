# -----------------------
# ETL script to fetch data on TSX
# Last update: 2024-10-01

import requests as r
import pandas as pd
import sqlite3
import os
from dotenv import load_dotenv
from pathlib import Path
import json

# env variables TODO: check if this can be added as secrets in gh or render
load_dotenv(dotenv_path=Path('..') / 'utils/.env')

# ------/// API key for Alpha Vantage /// ------ 
keys = json.loads(os.getenv('keys'))
current_key = keys['key1']

# ------/// List of symbols to fetch data for /// ------
def fetch_tsx_data_ts(symbol: str, API_AV: str) -> dict:
    """
    Fetch data from Alpha Vantage API.

    Parameters:
    symbol (str): The symbol of the stock to fetch data for.
    API_AV (str): The API key for Alpha Vantage.

    Returns:
    dict: A dictionary containing the fetched data.
    """
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=TSX:{symbol}&outputsize=full&apikey={API_AV}"
    response = r.get(url)

    if 'Error Message' in response.json().keys():
        raise Exception(f"Request failed with status {response.json().values()} for symbol - {symbol}")

    data = response.json()
    return data

tt=fetch_tsx_data_ts('TD', current_key)

if 'Error Message' in tt.keys():
    print('Error Message')

def dataframe_formatter(data: dict) -> pd.DataFrame:
    """
    Format the data fetched from Alpha Vantage API into a DataFrame.

    Parameters:
    data (dict): The data fetched from Alpha Vantage API.

    Returns:
    pd.DataFrame: The formatted DataFrame
    """
    df = pd.DataFrame(data['Time Series (Daily)']).T
    df['Symbol'] = data['Meta Data']['2. Symbol']
    df.index = pd.to_datetime(df.index)
    df.rename(columns={'1. open': 'Open',
                        '2. high': 'High',
                        '3. low': 'Low',
                        '4. close': 'Close',
                        '5. volume': 'Volume'}, inplace=True)
    return df


def fetch_all_data(symbols:pd.Series, key:str) -> dict:
    """
    Fetch data for all the symbols in the list.

    Description:
    This function fetches data for all the symbols in the list using
    the fetch_tsx_data_ts function and formats the data using the
    dataframe_formatter function.

    Parameters:
    symbols (pd.Series): The list of symbols to fetch data for.
    key (str): The API key for Alpha Vantage.

    Returns:
    dict: A dictionary containing the fetched data.

    """
    data = {}
    for symbol in symbols[:]:
        data[symbol] = dataframe_formatter(fetch_tsx_data_ts(symbol,key))
    return data




def fetch_symbols_frame():
    # TODO: log response frame in db for future reference
    # fetch data from stockanalysis API
    url='https://api.stockanalysis.com/api/screener/a/f?m=marketCap&s=desc&c=no,s,n,marketCap,price,change,revenue&cn=1000&f=exchangeCode-is-TSX,subtype-isnot-etf!cef&i=symbols'
    res=r.get(url)
    data=res.json()
    if 'data' not in data['data'].keys():
    
        raise Exception(f"Request failed - recheck the API response")


    # convert to DataFrame and extract symbol
    df=pd.DataFrame(data['data']['data'])  
    df.rename(columns={'s':'sym','n':'company'},inplace=True)

    df.drop('no',axis=1,inplace=True)
    df['symbol'] = df['sym'].str.split('/').str[1]    
    df.sort_values(by='marketCap',ascending=False)

    # limiting frame to top 100 companies
    # df=df.head(100)
    # rename columns 
    df.columns
    return df

df_sym=fetch_symbols_frame()




# overview of tickers 

df_sym['symbol'].values

responses=[]
for index, symb in enumerate(df_sym['symbol'].values):
    print(index, symb)
    if index>10:
        break
    print(symb,x)

    api_overview=f"https://stockanalysis.com/quote/tsx/{symb}/company/__data.json?x-sveltekit-trailing-slash=1&x-sveltekit-invalidated=001"
    responses.append(r.get(api_overview).json())


responses

# pull out the data and convert it into a table
def extract_data(response):
    data=response['data']
    data['symbol']=response['symbol']
    return data


responses[0].keys()



def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Connection to {db_file} successful")
    except Exception as e:
        print(e)
    return conn


def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
        print("Table created successfully")
    except Exception as e:
        print(e)


def main():
    database = "tsx_data.db"

    sql_create_table = """ CREATE TABLE IF NOT EXISTS tsx_data (
                                symbol text PRIMARY KEY,
                                name text NOT NULL,
                                marketCap text NOT NULL,
                                price text NOT NULL,
                                change text NOT NULL,
                                revenue text NOT NULL
                            ); """

    conn = create_connection(database)
    if conn is not None:
        create_table(conn, sql_create_table)
    else:
        print("Error! cannot create the database connection.")
    return None


df_sym

def main():
    pass
    return None

if __name__ == "__main__":
    main()