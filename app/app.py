import os
import pandas as pd
from pathlib import Path
from flask import Flask, render_template_string
import panel as pn
import plotly.graph_objects as go
from plotly.subplots import make_subplots
# import perspective
# import dtale
from datetime import datetime, timedelta
import panel as pn
import pandas as pd
from pathlib import Path
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from statsmodels.graphics.tsaplots import plot_acf
# from darts_test import forecast_arima
import matplotlib.pyplot as plt
from datetime import datetime
import socket
import sql3
import sqlite3

# ------// Panel App // ------

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


# Initialize Flask app
flask_app = Flask(__name__)


db_path = 'stocks.db'
print(db_path)
df=db_fetch_as_frame(db_path=db_path,query='select * from tsx_data')

df['Tick']=df['Symbol'].apply(lambda x: x.split('.')[0])
ticks=db_fetch_as_frame(db_path=db_path,query='select * from tsx_sa_tickers')
ticks=ticks[['symbol','company','revenue','marketCap']]
df=df.merge(ticks,how='left',left_on='Tick',right_on='symbol')
# df.sort_values(by='marketCap',ascending=True,inplace=True)
# Load and preprocess data
# df = pd.read_csv(Path('..' + '/tsx_data.csv').resolve())
df['Date'] = pd.to_datetime(df['Date'])
df.info()



# ----- // forecast fetching // -----
forecast_data=db_fetch_as_frame(db_path=db_path,query='select * from forecast_results')

forecast_data.head(5)

print(forecast_data.columns)

forecast_data=forecast_data.merge(ticks[['symbol','company']],how='left',left_on='Tick',right_on='symbol')
forecast_data['Date']=pd.to_datetime(forecast_data['Date'])



# Global ticker selector
tickers = df['company'].unique().tolist()
ticker_selector = pn.widgets.Select(name='Select Company', options=tickers, value=tickers[0])

# Time range toggle buttons for candlestick chart
time_range_toggle = pn.widgets.ToggleGroup(
    name='Select Time Range',
    options=['1 Day', '7 Days', '30 Days', '3 Months', '6 Months', 'YTD', '1 Year'],
    value='3 Months',
    behavior='radio',
    button_type='primary',
)

# Function to filter data by selected ticker
def filter_data(selected_ticker):
    return df[df['company'] == selected_ticker]

# Function to filter data by selected time range for candlestick chart
@pn.depends(ticker_selector.param.value, time_range_toggle.param.value)
def create_candlestick_chart(selected_ticker, selected_time_range):
    filtered_df = filter_data(selected_ticker)

    # Determine the date range based on selected toggle
    now = pd.Timestamp.now()
    if selected_time_range == '1 Day':
        start_date = now - pd.Timedelta(days=1)
    elif selected_time_range == '7 Days':
        start_date = now - pd.Timedelta(days=7)
    elif selected_time_range == '30 Days':
        start_date = now - pd.Timedelta(days=30)
    elif selected_time_range == '3 Months':
        start_date = now - pd.DateOffset(months=3)
    elif selected_time_range == '6 Months':
        start_date = now - pd.DateOffset(months=6)
    elif selected_time_range == 'YTD':
        start_date = datetime(now.year, 1, 1)
    elif selected_time_range == '1 Year':
        start_date = now - pd.DateOffset(years=1)
    else:
        start_date = filtered_df['Date'].min()

    # Filter the data for the candlestick chart
    candlestick_df = filtered_df[filtered_df['Date'] >= start_date]

    # Create candlestick chart
    fig = go.Figure(data=[go.Candlestick(
        x=candlestick_df['Date'],
        open=candlestick_df['Open'],
        high=candlestick_df['High'],
        low=candlestick_df['Low'],
        close=candlestick_df['Close'],
    )])
    fig.update_layout(
        title=f'Candlestick Chart ({selected_time_range}) - {selected_ticker}',
        xaxis_title='Date',
        yaxis_title='Price',
        height=600,
        width=1000
    )

    return pn.pane.Plotly(fig, sizing_mode='stretch_both')

# RSI Chart
@pn.depends(ticker_selector.param.value)
def create_rsi_chart(selected_ticker):
    filtered_df = filter_data(selected_ticker)

    def compute_rsi(data, time_window):
        diff = data.diff(1).dropna()
        up_chg = diff.where(diff > 0, 0)
        down_chg = -diff.where(diff < 0, 0)
        up_chg_avg = up_chg.rolling(window=time_window).mean()
        down_chg_avg = down_chg.rolling(window=time_window).mean()
        rs = up_chg_avg / down_chg_avg
        rsi = 100 - (100 / (1 + rs))
        return rsi

    filtered_df['RSI'] = compute_rsi(filtered_df['Close'], 14)

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03,
                        subplot_titles=('Closing Price', 'RSI'), row_width=[0.3, 0.7])

    fig.add_trace(go.Scatter(x=filtered_df['Date'], y=filtered_df['Close'], mode='lines', name='Close Price'), row=1, col=1)
    fig.add_trace(go.Scatter(x=filtered_df['Date'], y=filtered_df['RSI'], mode='lines', name='RSI'), row=2, col=1)

    fig.update_layout(height=600, title=f'RSI and Closing Price - {selected_ticker}')
    return pn.pane.Plotly(fig, sizing_mode='stretch_both')

# Moving Averages Chart
@pn.depends(ticker_selector.param.value)
def create_moving_averages_chart(selected_ticker):
    filtered_df = filter_data(selected_ticker)
    filtered_df['MA50'] = filtered_df['Close'].rolling(window=50).mean()
    filtered_df['MA200'] = filtered_df['Close'].rolling(window=200).mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=filtered_df['Date'], y=filtered_df['Close'], mode='lines', name='Close Price'))
    fig.add_trace(go.Scatter(x=filtered_df['Date'], y=filtered_df['MA50'], mode='lines', name='50-day MA'))
    fig.add_trace(go.Scatter(x=filtered_df['Date'], y=filtered_df['MA200'], mode='lines', name='200-day MA'))
    fig.update_layout(title=f'Moving Averages - {selected_ticker}', xaxis_title='Date', yaxis_title='Price')
    return pn.pane.Plotly(fig, sizing_mode='stretch_both')

# Line Chart for Open/High/Low/Close
@pn.depends(ticker_selector.param.value)
def create_line_chart(selected_ticker):
    filtered_df = filter_data(selected_ticker)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=filtered_df['Date'], y=filtered_df['Open'], mode='lines', name='Open'))
    fig.add_trace(go.Scatter(x=filtered_df['Date'], y=filtered_df['High'], mode='lines', name='High'))
    fig.add_trace(go.Scatter(x=filtered_df['Date'], y=filtered_df['Low'], mode='lines', name='Low'))
    fig.add_trace(go.Scatter(x=filtered_df['Date'], y=filtered_df['Close'], mode='lines', name='Close'))
    fig.update_layout(title=f'Stock Prices Over Time - {selected_ticker}', xaxis_title='Date', yaxis_title='Price')
    return pn.pane.Plotly(fig, sizing_mode='stretch_both')


def get_market_cap(selected_ticker):
    filtered_df = filter_data(selected_ticker)
    market_cap = filtered_df['marketCap'].iloc[-1]
    return f"MarketCap: ${int(market_cap):,}"

# Display Revenue with proper binding
@pn.depends(ticker_selector.param.value)
def get_revenue(selected_ticker):
    filtered_df = filter_data(selected_ticker)
    revenue = filtered_df['revenue'].iloc[-1]
    return f"Revenue: ${int(revenue):,}"


# add one more tab using 

# ------ old plot for forecast
# @pn.depends(ticker_selector.param.value)
# def plot_forecasts(selected_ticker):
#     company_name = selected_ticker
#     data = forecast_data[forecast_data['company'] == company_name]
#     actual = data['Actual']
#     xgb_forecast = data['XGB_Forecast']
#     lstm_forecast = data['LSTM_Forecast']
#     arima_forecast = data['ARIMA_Forecast']  
#     test_index = data['Date']

#     fig = go.Figure()

#     fig.add_trace(go.Scatter(x=test_index, y=actual, mode='lines', name='Actual', line=dict(color='black')))
#     fig.add_trace(go.Scatter(x=test_index, y=xgb_forecast, mode='lines', name='XGB Forecast', line=dict(dash='dash', color='blue')))
#     fig.add_trace(go.Scatter(x=test_index, y=lstm_forecast, mode='lines', name='LSTM Forecast', line=dict(dash='dash', color='orange')))
#     fig.add_trace(go.Scatter(x=test_index, y=arima_forecast, mode='lines', name='ARIMA Forecast', line=dict(dash='dash', color='red')))

#     fig.update_layout(
#         title=f'Forecast Comparison for {company_name}',
#         xaxis_title='Date',
#         yaxis_title='Close Price',
#         legend_title='Legend',
#         template='plotly_white'
#     )

#     return pn.pane.Plotly(fig, sizing_mode='stretch_both')

@pn.depends(ticker_selector.param.value)
def plot_forecasts(selected_ticker):
    company_name = selected_ticker
    # Debug prints to check data
    print(f"Selected company: {company_name}")
    print(f"All columns in forecast_data: {forecast_data.columns.tolist()}")
    
    # Filter data for selected company
    data = forecast_data[forecast_data['company'] == company_name].copy()
    print(f"Number of rows for {company_name}: {len(data)}")
    print(f"Columns in filtered data: {data.columns.tolist()}")
    
    # Check if data exists
    if len(data) == 0:
        return pn.pane.Markdown("No forecast data available for this company")
    
    # Print sample of data to verify values
    print("\nFirst few rows of forecasts:")
    print(data[['Date', 'Actual', 'XGB_Forecast', 'LSTM_Forecast', 'ARIMA_Forecast']].head())
    
    fig = go.Figure()
    
    # Add traces with error handling
    try:
        # Add actual data
        fig.add_trace(go.Scatter(
            x=data['Date'], 
            y=data['Actual'], 
            mode='lines', 
            name='Actual', 
            line=dict(color='black')
        ))
        
        # Add XGB forecast
        fig.add_trace(go.Scatter(
            x=data['Date'], 
            y=data['XGB_Forecast'], 
            mode='lines', 
            name='XGB Forecast', 
            line=dict(dash='dash', color='blue')
        ))
        
        # Add LSTM forecast
        fig.add_trace(go.Scatter(
            x=data['Date'], 
            y=data['LSTM_Forecast'], 
            mode='lines', 
            name='LSTM Forecast', 
            line=dict(dash='dash', color='orange')
        ))
        
        # Add ARIMA forecast with explicit error handling
        if 'ARIMA_Forecast' in data.columns:
            print("\nARIMA Forecast values:")
            print(data['ARIMA_Forecast'].head())
            fig.add_trace(go.Scatter(
                x=data['Date'], 
                y=data['ARIMA_Forecast'], 
                mode='lines', 
                name='ARIMA Forecast', 
                line=dict(dash='dash', color='red')
            ))
        else:
            print("\nARIMA_Forecast column not found in data")
            
    except Exception as e:
        print(f"Error adding traces: {str(e)}")
        return pn.pane.Markdown(f"Error creating forecast plot: {str(e)}")

    fig.update_layout(
        title=f'Forecast Comparison for {company_name}',
        xaxis_title='Date',
        yaxis_title='Close Price',
        legend_title='Legend',
        template='plotly_white'
    )

    return pn.pane.Plotly(fig, sizing_mode='stretch_both')

forecast_data.columns

# Full dashboard layout
dashboard = pn.Column(
   pn.Row(
        pn.pane.Markdown("<h1>Stock Data Analysis</h1>", align="start"),
        ticker_selector,
        # pn.bind(lambda cap: pn.pane.Markdown(f"<h3>{cap}</h3>", align="start"), get_market_cap),
        # pn.bind(lambda rev: pn.pane.Markdown(f"<h3>{rev}</h3>", align="start"), get_revenue)
    ),
    pn.Tabs(
        ('Candlestick Chart', pn.Column(time_range_toggle, create_candlestick_chart)),
        ('RSI Chart', create_rsi_chart),
        ('Moving Averages', create_moving_averages_chart),
        ('Line Chart', create_line_chart),
        # ('Data Table', create_data_table),
         ('Forecast Comparison', plot_forecasts)
    )
)


@flask_app.route('/')
def index():
    host=socket.gethostname()
    ip=socket.gethostbyname(host)
    panel_url = f"http://{ip}:5001" 
    return render_template_string(
        f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Flask + Panel Integration</title>
        </head>
        <body style="margin: 0; padding: 0; overflow: hidden;">
            <iframe src="{panel_url}" width="100%" height="100%" style="border: none;"></iframe>
        </body>
        </html>
        """
    )

# Run Panel server if this script is run directly
if __name__ == "__main__":
    # Option 1: Serve Panel as a standalone app
    pn.serve(
    dashboard,
    port=5001,
    address='0.0.0.0',
    allow_websocket_origin=['0.0.0.0:5001', 'localhost:5001'],  
    show=False
)
    # # Option 2: Run Flask app (disable this if using Panel standalone)
    # flask_app.run(host='0.0.0.0', port=5006)
