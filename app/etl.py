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

#TODO: 
# make changes to the ETL , move to main
# fix app and darts to load both into the app.py by 6 
# work on deployment 

load_dotenv(dotenv_path=Path('..') / 'utilz/.env')
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
  

keygen()

json.dumps(keys)
str(keys)
keys
json.loads(str(keys))
# remove keys from keys dict that are None

keys={k:v for k,v in keys.items() if v is not None}
keys
last_key_val=''.join(filter(str.isdigit, list(keys.keys())[-1]))

for i in range(int(last_key_val)+1,int(last_key_val)+21):
    print(i)
    val=keygen()
    if val is None:
        break
    else:
        keys[f'key{i}']=keygen()





# key_frame=pd.DataFrame.from_dict(keys,orient='index',columns=['key'])
# key_frame.reset_index(inplace=True)
# del key_frame['key']
# key_frame.rename(columns={'index':'key'},inplace=True)
# key_frame['status']=False
# key_frame['fail_count']=0
# key_frame['last_run_dttm']=0

# key_frame

# sql3.db_upsert(df=key_frame,db_path=db_path,table_name='keyframe',primary_keys=['key'])

sql3.db_create_table(df=keyframe,db_path=db_path,table_name='keyframe',primary_key='key')



create_table_query="""
CREATE TABLE IF NOT EXISTS keyframe (
    key TEXT PRIMARY KEY,
    status BOOLEAN,
    fail_count INTEGER,
    last_run_dttm DATETIME) """

# drop runcount column from keyframe

sql3.get_table_info(db_path=db_path,table_name='keyframe')
sql3.list_tables(db_path=db_path)


sql3.execute_query(db_path=db_path,query=create_table_query)
sql3.get_table_info(db_path=db_path,table_name='keyframe')

# insert data
sql3.db_fetch_as_frame(db_path=db_path,query='select * from keyframe')
sql3.db_upsert(df=keyframe,db_path=db_path,table_name='keyframe',primary_keys=['key'])












# ------/// ETL for daily ticker refresh /// -------

def fetch_tsx_data_ts(symbol: str, vantage_key: str) -> dict:
    """
    Fetch daily stock data for a given symbol from Alpha Vantage.

    Args:
        symbol (str): The symbol of the stock to fetch data for.
        vantage_key (str): The API key for Alpha Vantage.

    Returns:
        dict: A dictionary containing the stock data.
    """
    session = r.Session()
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}.TRT&outputsize=full&apikey={vantage_key}"
    response = session.get(url)
    data = response.json()
    session.close()
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


def dataframe_formatter(data: dict) -> pd.DataFrame:

    df = pd.DataFrame(data['Time Series (Daily)']).T
    df['Symbol'] = data['Meta Data']['2. Symbol']
    df.index = pd.to_datetime(df.index)
    df.rename(columns={'1. open': 'Open',
                        '2. high': 'High',
                        '3. low': 'Low',
                        '4. close': 'Close',
                        '5. volume': 'Volume'}, inplace=True)
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'Date'}, inplace=True)
    df['Date'] = df['Date'].astype(str)

    return df



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
df_tsxv.reset_index(drop=True,inplace=True)




# create 2 tables for TSX and TSXV
sql3.db_create_table(df=df_tsx,db_path=db_path,table_name='tsx_sa_tickers',primary_key='symbol')
sql3.db_create_table(df=df_tsxv,db_path=db_path,table_name='tsxv_sa_tickers',primary_key='symbol')

sql3.db_fetch_as_frame(db_path=db_path,query='select * from tsx_sa_tickers')



# running etl job for tsx first


tsx_df=sql3.db_fetch_as_frame(db_path=db_path,query='select * from tsx_sa_tickers')
tsx_df.sort_values(by='marketCap',ascending=False,inplace=True)
tsx_df['symbol'].value_counts().reset_index()


key_frame=sql3.db_fetch_as_frame(db_path=db_path,query='select * from keyframe')

key_frame


tsx_data=sql3.db_fetch_as_frame(db_path=db_path,query='select * from tsx_data')

print(tsx_data['Symbol'].nunique())
tsx_data
# split Symbol column in tsx_data into 2 columns . 1 for TSX and 1 for TSXV

tsx_data['tick']=[x.split('.')[0] for x in tsx_data['Symbol']]
tsx_data['exhcange']=[x.split('.')[1] for x in tsx_data['Symbol']]

tsx_data.to_csv('../tsx_data.csv',index=False)



# pending_stocks
existing=list(tsx_data['Symbol'].unique())
existing=[x.split('.')[0] for x in existing]
len(existing)
all_stocks=list(tsx_df['symbol'])
# all_stocks=[x]
all_stocks.index('STLR')
pending=list(set(all_stocks)-set(existing))
pending
pending
len(pending)

i='GRT.UN:TOR'

# data=fetch_tsx_data_ts(symbol='GRT-UN',vantage_key=keys['key111'])

def tsx_data_etl():
    key_val=180
    data={}
    while len(pending)>0 and key_val<len(keys):
        if '.' in pending[0]:
            pending.remove(pending[0])
            continue
            
        time.sleep(.1)
        current_key=key_frame['key'][key_val]
        key=keys[current_key]
        print(pending[0],key,key_val,key_frame['key'][key_val])
        data=fetch_tsx_data_ts(symbol=pending[0],vantage_key=key)
        print(data.keys())


        
        if 'Time Series (Daily)' in data.keys():
            df=dataframe_formatter(data)
            print(f'upserting to db {pending[0]}')

            sql3.db_upsert(df=df,db_path=db_path,table_name='tsx_data',primary_keys=['Date','Symbol'])
            pending.remove(pending[0])

        elif 'Error Message' in data.keys():
            print(f'ticker {pending[0]} not found, switching to next tick')
            pending.remove(pending[0])


        elif 'Information' in data.keys():
            print(f'limit reached unknown reason,breaking out of loop')
            break   
            pending.remove(pending[0])
            key_val+=1  
            

tsx_data_etl()




            









data=fetch_tsx_data_ts(symbol='RY',vantage_key=keys['key10'])
df=dataframe_formatter(data)
df.reset_index(inplace=True)
df.rename(columns={'index':'Date'},inplace=True)
df['Date']= df['Date'].astype('str')
# sql3.create_new_table_query(df=df,db_path=db_path,table_name='tsx_data',primary_keys=['Date','Symbol'])
# sql3.db_upsert(df=df,db_path=db_path,table_name='tsx_data',primary_keys=['Date','Symbol'])

dataframe_formatter(data)


tsx_data_etl()


df=pd.read_csv('../tsx_data.csv')

df=sql3.db_fetch_as_frame(db_path=db_path,query='select * from tsx_data')

df[['Date','Symbol']].drop_duplicates()

df['Symbol'].value_counts(dropna=False).sort_index().reset_index()

df[~df['Date'].isna()]













table_name='tsx_data'
# list all tables
sql3.list_tables(db_path=db_path)


# list all columns in table
sql3.get_table_info(db_path=db_path,table_name=table_name)

sql3.db_upsert(df=stock_data,db_path=db_path,table_name='tsx_data',primary_keys=['Date','Symbol'])

sql3.db_fetch_as_frame(db_path=db_path,query='select * from tsx_data')



#---- /// all queries ///----

query="""
Drop table if exists keyframe;

"""


sql3.execute_query(db_path=db_path,query=query)

df=sql3.db_fetch_as_frame(db_path=db_path,query='select * from tsx_tickers_sa_temp')
df


tsx_df['Date'].max()




fetch_tsx_data_ts(symbol='TD',vantage_key=keys['key2'])

fetch_tsxv_data_ts(symbol=df_tsxv['symbol'].loc[0],vantage_key=keys['key2'])






def main():
    pass
    return None

if __name__ == "__main__":
    main()


