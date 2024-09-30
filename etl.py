# TSX data explore

import requests as r
import pandas as pd

key="BWBVB7B1L78NHG81"



def fetch_tsx_data_ts(symbol,API_AV):
    """
    Fetch data from Alpha Vantage API
    """
    url=f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=TSX:{symbol}&outputsize=full&apikey={API_AV}"
    res = r.get(url)
    data = res.json()
    res
    return data


def dataframe_formatter(data):
    """
    Format the data into a pandas DataFrame
    """
    df = pd.DataFrame(data['Time Series (Daily)']).T
    df['Symbol'] = data['Meta Data']['2. Symbol']
    df.index = pd.to_datetime(df.index)
    df.rename(columns={'1. open': 'Open', '2. high': 'High', '3. low': 'Low',
                        '4. close': 'Close', '5. volume': 'Volume'}, inplace=True)
    return df



def fetch_symbols():
    ''' 
    Different API used for pulling the symbol's 
    '''

    url='https://api.stockanalysis.com/api/screener/a/f?m=marketCap&s=desc&c=no,s,n,marketCap,price,change,revenue&cn=1000&f=exchangeCode-is-TSX,subtype-isnot-etf!cef&i=symbols'
    res=r.get(url)
    data=res.json()
    symbols=[]
    for i in data['data']['data']:
        val = i['s']
        val=val.split("/")[1]
        symbols.append(val)

    return symbols

symbols=fetch_symbols()


def fetch_all_data(symbols):
    """
    Fetch data for all symbols
    """
    data = {}
    for symbol in symbols[:]:
        data[symbol] = dataframe_formatter(fetch_tsx_data_ts(symbol,key))
    return data


data = fetch_all_data(symbols)

df_final=pd.concat(data.values())


df_final.to_csv('tsx_data.csv')

symbols=symbols[:10]

def main():
    pass
    return None

if __name__ == __main__
    main()