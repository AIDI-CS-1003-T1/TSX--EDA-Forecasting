# -----------------------
# ETL script - Fetching data from Alpha Vantage and Stockanalysis 
# Last update: 2024-10-01

import requests as r
import pandas as pd
import sqlite3
import os
from dotenv import load_dotenv
from pathlib import Path
import json
import sql3
import dtale
# env variables TODO: check if this can be added as secrets in gh or render
load_dotenv(dotenv_path=Path('..') / 'utils/.env')

# ------/// API key for Alpha Vantage /// ------ 
keys = json.loads(os.getenv('keys'))
key_list = list(keys.keys())

key_list

# ------/// List of symbols to fetch data for /// ------
def fetch_tsx_data_ts(symbol: str, API_AV: str) -> dict:

    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=TSX:{symbol}&outputsize=full&apikey={API_AV}"
    response = r.get(url)

    if 'Information' in response.json().keys() and current_key >= len(key_list):
        print(f"API limit reached for key: {API_AV} and no more keys available!")
        
    elif 'Information' in response.json().keys():
        print(f"API limit reached for key: {API_AV}")
        current_key += 1
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=TSX:{symbol}&outputsize=full&apikey={keys[current_key]}"
        response = r.get(url)

    data = response.json()
    return data



def dataframe_formatter(data: dict) -> pd.DataFrame:

    df = pd.DataFrame(data['Time Series (Daily)']).T
    df['Symbol'] = data['Meta Data']['2. Symbol']
    df.index = pd.to_datetime(df.index)
    df.rename(columns={'1. open': 'Open',
                        '2. high': 'High',
                        '3. low': 'Low',
                        '4. close': 'Close',
                        '5. volume': 'Volume'}, inplace=True)
    return df


# ---- /// Handling keys and API calls


def fetch_tickers_tsx():
    """
    Stockanalysis for TSX tickers
    """
    frames=[]
    exchange=['TSX','TSXV']
    for i in exchange:
        url=f'https://api.stockanalysis.com/api/screener/a/f?m=marketCap&s=desc&c=no,s,n,marketCap,price,change,revenue&cn=1000&f=exchangeCode-is-{i},subtype-isnot-etf!cef&i=symbols'
        res=r.get(url)
        data=res.json()
        if 'data' not in data['data'].keys():
            raise Exception(f"Request failed - ticker lookup failed")
        else:
            df=pd.DataFrame(data['data']['data'])
            df['exchange']=i
            df.rename(columns={'s':'sym','n':'company'},inplace=True)
            df.drop('no',axis=1,inplace=True)
            df['symbol'] = df['sym'].str.split('/').str[1]    
            df.sort_values(by='marketCap',ascending=False)
            frames.append(df)

    

    return pd.concat(frames)



# 

df_sym=fetch_tickers_tsx()
df_tsx=df_sym[df_sym['exchange']=='TSX']
df_tsxv=df_sym[df_sym['exchange']=='TSXV']

df_tickers=sql3.db_fetch_as_frame('../data/stocks.db',"select * from tsx_tickers_sa")

df_temp=sql3.db_fetch_as_frame('../data/stocks.db',"select * from tsx_data_temp")
df_temp


df_tickers


sql3.list_tables('../data/stocks.db')

sql3.get_table_info('../data/stocks.db','tsx_data_temp')

# fetch tsx_tickers_sa from db











existing_symbols = t['Symbol'].str.split(':').str[1].unique().tolist()
all_symbols = df_tsx['symbol'].unique().tolist()


symbol_to_fetch = [x for x in all_symbols if x not in existing_symbols]

len(symbol_to_fetch)



t=pd.read_csv(Path('..'+'/tsx_data.csv').resolve())
t['Symbol'].unique().tolist()

# ----/// updating the tickers in the db

sql3



# reading the data /csv and the db files

pd.read_csv(Path('..'+'/tsx_data.csv').resolve())



# fetch data from the db
db_path = "../data/stocks.db"
conn = sqlite3.connect(db_path)
query = "SELECT name FROM sqlite_master WHERE type='table';"
# df = pd.read_sql("SELECT * FROM master_schema", conn)

def run_query(query: str,db_path: str) -> pd.DataFrame:
    conn = sqlite3.connect(db_path)
    df = pd.read_sql(query, conn)
    conn.close()
    return df


s=run_query('select * from tsx_data_temp',db_path)




# -----/// Fetching Data for EDA /// ------










def main():
    pass
    return None

if __name__ == "__main__":
    main()