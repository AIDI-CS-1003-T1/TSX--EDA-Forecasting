import panel as pn
import pandas as pd
from pathlib import Path
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from statsmodels.graphics.tsaplots import plot_acf
import matplotlib.pyplot as plt
from datetime import datetime

# Load and preprocess data
df = pd.read_csv(Path('..' + '/tsx_data.csv').resolve())
df.rename(columns={'Unnamed: 0': 'Date'}, inplace=True)
df['Date'] = pd.to_datetime(df['Date'])

# Global ticker selector
tickers = df['Symbol'].unique().tolist()
ticker_selector = pn.widgets.Select(name='Select Ticker', options=tickers, value=tickers[0])

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
    return df[df['Symbol'] == selected_ticker]

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

    return pn.pane.Plotly(fig)

# Function for Autocorrelation with a dynamic lag slider
acf_lag_slider = pn.widgets.IntSlider(name="Autocorrelation Lag", start=1, end=100, value=50)

@pn.depends(ticker_selector.param.value, acf_lag_slider.param.value)
def create_autocorrelation_chart(selected_ticker, lag):
    filtered_df = filter_data(selected_ticker)
    
    plt.figure(figsize=(12, 6))
    plot_acf(filtered_df['Close'].dropna(), lags=lag)
    plt.title(f'Autocorrelation of Closing Prices - {selected_ticker} (Lag: {lag})')
    acf_fig = pn.pane.Matplotlib(plt.gcf(), sizing_mode='stretch_both')
    plt.close('all')

    return acf_fig

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
    return pn.pane.Plotly(fig)

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
    return pn.pane.Plotly(fig)

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
    return pn.pane.Plotly(fig)

# Data Table
@pn.depends(ticker_selector.param.value)
def create_data_table(selected_ticker):
    filtered_df = filter_data(selected_ticker)
    return pn.pane.Perspective(filtered_df, sizing_mode='stretch_both')

# Full dashboard layout
dashboard = pn.Column(
    pn.Row(
        pn.pane.Markdown("<h1>Stock Data Analysis</h1>", align="start"),
        ticker_selector
    ),
    pn.Tabs(
        ('Candlestick Chart', pn.Column(time_range_toggle, create_candlestick_chart)),
        ('RSI Chart', create_rsi_chart),
        ('Moving Averages', create_moving_averages_chart),
        ('Line Chart', create_line_chart),
        ('Data Table', create_data_table),
        ('Autocorrelation', pn.Column(acf_lag_slider, create_autocorrelation_chart)),
    )
)

# Serve the dashboard
if __name__ == "__main__":
    dashboard.show()