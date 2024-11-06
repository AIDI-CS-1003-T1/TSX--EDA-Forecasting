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
# env variables TODO: check if this can be added as secrets in gh or render
load_dotenv(dotenv_path=Path('..') / 'utils/.env')

# ------/// API key for Alpha Vantage /// ------ 
keys = json.loads(os.getenv('keys'))
key_list = list(keys.keys())

key_list
current_key = 0

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


# ----/// updating the tickers in the db

sql3


# add the df_sym to the db 




# reading the data /csv and the db files

pd.read_csv(Path('..'+'/tsx_data.csv').resolve())









# -----/// Fetching Data for EDA /// ------

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













def main():
    pass
    return None

if __name__ == "__main__":
    main()