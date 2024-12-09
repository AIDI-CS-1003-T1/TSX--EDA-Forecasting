from utilz.utils import discord_logger
import os 
import logging
import sql3
import json
import time
logging.basicConfig(level=logging.INFO)


load_dotenv(dotenv_path=Path('..') / 'utilz/.env')
db_path='../data/stocks.db'
# ------///  loading secrets 
keys = json.loads(os.getenv('SECRET_KEYS'))
discord_hook = json.loads(os.getenv('discord_hook'))




discord_logger(os.getenv('discord_hook'), "ETL pipeline event triggered")
logging.info("ETL pipeline event triggered")



db_path='../data/stocks.db'


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
