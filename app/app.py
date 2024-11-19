import panel as pn 
import pandas as pd
from pathlib import Path
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import perspective
import dtale
from flask import Flask

# Create Flask app
flask_app = Flask(__name__)

# ------// Panel App // ------

# Read and process the data
df = pd.read_csv(Path('/app/tsx_data.csv').resolve())
df.rename(columns={'Unnamed: 0':'Date'}, inplace=True)
df['Date'] = pd.to_datetime(df['Date'])

# Filter data (for example, for a specific stock symbol)
df = df[df['Symbol'].str.contains('TSX:TD')]

# Create Plotly figure (Open, High, Low, Close) trace
fig = go.Figure()

# Add traces for open, high, low, close
fig.add_trace(go.Scatter(x=df.index, y=df['Open'], mode='lines', name='Open'))
fig.add_trace(go.Scatter(x=df.index, y=df['High'], mode='lines', name='High'))
fig.add_trace(go.Scatter(x=df.index, y=df['Low'], mode='lines', name='Low'))
fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='Close'))

# Add bar trace for volume on a separate y-axis
fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume', yaxis='y2'))

# Create a layout with 2 y-axes
fig.update_layout(
    yaxis=dict(title='Price'),
    yaxis2=dict(title='Volume', overlaying='y', side='right'),
    title='Stock Price and Volume Over Time',
    xaxis=dict(title='Date')
)

# Calculate the date 3 months ago for filtering
from datetime import datetime, timedelta
three_months_ago = datetime.now() - timedelta(days=90)
df_last_3_months = df[df['Date'] > three_months_ago]

# Create Candlestick Chart for the last 3 months
fig_candlestick = go.Figure(data=[go.Candlestick(x=df_last_3_months['Date'],
                open=df_last_3_months['Open'], high=df_last_3_months['High'],
                low=df_last_3_months['Low'], close=df_last_3_months['Close'],
                name='Price')])

fig_candlestick.update_layout(height=600, width=1000, title_text="Candlestick Chart - Last 3 Months")
pane2 = pn.pane.Plotly(fig_candlestick)

# Line plot for Closing Prices
fig_line = go.Figure()
fig_line.add_trace(go.Scatter(x=df['Date'], y=df['Close'], mode='lines', name='Close Price'))
fig_line.update_layout(title='Closing Price Over Time', xaxis_title='Date', yaxis_title='Price')

# Moving Averages: 50-day and 200-day
df['MA50'] = df['Close'].rolling(window=50).mean()
df['MA200'] = df['Close'].rolling(window=200).mean()

fig_ma = go.Figure()
fig_ma.add_trace(go.Scatter(x=df['Date'], y=df['Close'], mode='lines', name='Close Price'))
fig_ma.add_trace(go.Scatter(x=df['Date'], y=df['MA50'], mode='lines', name='50-day MA'))
fig_ma.add_trace(go.Scatter(x=df['Date'], y=df['MA200'], mode='lines', name='200-day MA'))
fig_ma.update_layout(title='Closing Price with Moving Averages', xaxis_title='Date', yaxis_title='Price')

pane1 = pn.pane.Plotly(fig_ma, sizing_mode='stretch_both')

# Compute Relative Strength Index (RSI)
def compute_rsi(data, time_window):
    diff = data.diff(1).dropna()
    up_chg = 0 * diff
    down_chg = 0 * diff
    up_chg[diff > 0] = diff[diff > 0]
    down_chg[diff < 0] = -diff[diff < 0]
    up_chg_avg = up_chg.ewm(com=time_window-1, min_periods=time_window).mean()
    down_chg_avg = down_chg.ewm(com=time_window-1, min_periods=time_window).mean()
    rs = up_chg_avg / down_chg_avg
    rsi = 100 - 100 / (1 + rs)
    return rsi

df['RSI'] = compute_rsi(df['Close'], 14)

# RSI with closing price plot
fig_rsi = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, subplot_titles=('Closing Price', 'RSI'), row_width=[0.7, 0.3])
fig_rsi.add_trace(go.Scatter(x=df['Date'], y=df['Close'], mode='lines', name='Close Price'), row=1, col=1)
fig_rsi.add_trace(go.Scatter(x=df['Date'], y=df['RSI'], mode='lines', name='RSI'), row=2, col=1)
fig_rsi.update_layout(height=600, width=1000, title_text="Closing Price and RSI")
fig_rsi.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
fig_rsi.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

# Create Panel view for the data
df_pane = pn.pane.Perspective(df, sizing_mode='stretch_both')

# Panel tabs
app = pn.Tabs(('Pane 1', pane1), ('Pane 2', pane2), ('Data', df_pane))

# ------// Flask and Panel integration // ------
@flask_app.route('/')
def panel_app():
    return app.servable()  # This renders the Panel app

# Start the Flask app (and serve Panel via Flask)
if __name__ == "__main__":
    flask_app.run(host='0.0.0.0', port=80)  # Listen on all interfaces for Docker container access
