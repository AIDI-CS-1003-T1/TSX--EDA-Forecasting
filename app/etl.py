# -----------------------
# ETL script - Fetching data from Alpha Vantage and Stockanalysis 
# -----------------------
import requests as r
import pandas as pd
import sqlite3
import random
import re
import os
from dotenv import load_dotenv,set_key
from pathlib import Path
import json
import sql3
import dtale
import time
import statsmodels.api 
# env variables 

#TODO: check if this can be added as secrets in gh or render



load_dotenv(dotenv_path=Path('..') / 'utils/.env')
db_path='../data/stocks.db'
# ------///  loading secrets 
keys = json.loads(os.getenv('SECRET_KEYS'))
discord_hook = json.loads(os.getenv('discord_hook'))



# ----- /// keygen


def keygen():
    csrf_url = "https://www.alphavantage.co/support/#api-key"
    session = r.Session()
    response = session.get(csrf_url)
    csrf_token = session.cookies.get('csrftoken')

    post_url = "https://www.alphavantage.co/create_post/"
    
    occupations = ['Educator', 'Student', 'Investor', 'Software Developer']
    companies = ['Google', 'Microsoft', 'Apple', 'College', 'University']
    first_names = ['john', 'jane', 'alex', 'emily']
    last_names = ['doe', 'smith', 'johnson', 'williams']
    domains = ['gmail.com', 'aol.com', 'outlook.com', 'yahoo.com']

    payload = {
        "first_text": "deprecated",
        "last_text": "deprecated",
        "occupation_text": random.choice(occupations),
        "organization_text": random.choice(companies),
        "email_text": f"{random.choice(first_names)}.{random.choice(last_names)}{random.randint(1, 1000)}@{random.choice(domains)}"
    }
    user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"
    ]

    headers = {
        "Referer": "https://www.alphavantage.co/",
        "User-Agent": random.choice(user_agents),
        "X-CSRFToken": csrf_token
    }

    res = session.post(post_url, data=payload, headers=headers)
    key_res=res.json()
    print(res.text,res.json())
    pattern = r'[A-Z0-9]{16}'
    match = re.search(pattern, key_res['text'])
    if match:
        val = match.group(0)
    else:
        val = None
    return val
  



keyframe=pd.DataFrame(data=list(keys.keys()),columns=['key'])
keyframe['status']=True
keyframe['fail_count']=0
keyframe['last_run_dttm']=None
keyframe['runcount']=0
keyframe.info(verbose=True)
keyframe = keyframe.where(pd.notnull(keyframe), None)
keyframe


sql3.db_create_table(df=keyframe,db_path=db_path,table_name='keyframe',primary_key='key')
sql3.db_create_table?



create_table_query="""
CREATE TABLE IF NOT EXISTS keyframe (
    key TEXT PRIMARY KEY,
    status BOOLEAN,
    fail_count INTEGER,
    last_run_dttm DATETIME,
    runcount INTEGER
)"""

sql3.execute_query(db_path=db_path,query=create_table_query)
sql3.get_table_info(db_path=db_path,table_name='keyframe')

# insert data
sql3.db_upsert(df=keyframe,db_path=db_path,table_name='keyframe',primary_keys=['key'])

sql3.db_fetch_as_frame(db_path=db_path,query='select * from keyframe')




droptable_query='drop table if exists keyframe'
sql3.execute_query(db_path='../data/stocks.db',query=droptable_query)
sql3.get_table_info(db_path=db_path,table_name='keyframe')
sql3.list_tables(db_path=db_path)



sql3.db_upsert(df=keyframe,db_path='../data/stocks.db',table_name='keyframe',primary_keys=['key'])
sql3.get_table_info(db_path='../data/stocks.db',table_name='keyframe')
t=sql3.db_fetch_as_frame(db_path='../data/stocks.db',query='select * from keyframe')
sql3.db_create_table(df=keyframe,db_path='../data/stocks.db',table_name='keyframe')









# ------/// ETL for daily ticker refresh /// -------

def fetch_tsx_data_ts(symbol: str, vantage_key: str) -> dict:
    """
    Fetch daily stock data for a given symbol from Alpha Vantage.

    Args:
        symbol (str): The symbol of the stock to fetch data for.
        API_AV (str): The API key for Alpha Vantage.

    Returns:
        dict: A dictionary containing the stock data.
    """


    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}.TRT&outputsize=full&apikey={vantage_key}"
    response = r.get(url)
    data = response.json()
    return data

"""
https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=SHOP.TRT&outputsize=full&apikey=demo
https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=GPV.TRV&outputsize=full&apikey=demo
"""
def fetch_tsxv_data_ts(symbol: str, vantage_key: str) -> dict:
    """
    Fetch daily stock data for a given symbol from Alpha Vantage.

    Args:
        symbol (str): The symbol of the stock to fetch data for.
        API_AV (str): The API key for Alpha Vantage.

    Returns:
        dict: A dictionary containing the stock data.
    """
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}.TRV&outputsize=full&apikey={vantage_key}"
    print(url)
    response = r.get(url)
    data = response.json()
    return data





fetch_tsx_data_ts(symbol='TD',vantage_key=keys['key2'])

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

df_sym=fetch_tickers_tsx()
df_sym.reset_index(drop=True,inplace=True)

df_tsx=df_sym[df_sym['exchange']=='TSX']
df_tsxv=df_sym[df_sym['exchange']=='TSXV']



dtale.show(df_sym).open_browser()

df_sym

for i in df_tsx['symbol']:print(i)


































# upsert check 
sql3.db_upsert(df= df_sym, db_path='../data/stocks.db', table_name='tsx_tickers_sa', primary_keys=['sym'])
df_tickers=sql3.db_fetch_as_frame('../data/stocks.db',"select * from tsx_tickers_sa")
df_temp=sql3.db_fetch_as_frame('../data/stocks.db',"select * from tsx_data_temp")




df_tickers['exchange'].value_counts()

sql3.list_tables('../data/stocks.db')

sql3.get_table_info('../data/stocks.db','tsx_data_temp')



for i in df_tickers['sym']: print(i)

tsx_quote=f'https://stockanalysis.com/quote/tsx/{tick}/financials/__data.json?'
tsxv_quote =f"https://stockanalysis.com/quote/tsxv/{tick}/financials/__data.json"




# ------ /// ETL for stockanalysis - TSX & TSXV - Overview & Metrics /// ------




















def main():
    pass
    return None

if __name__ == "__main__":
    main()


