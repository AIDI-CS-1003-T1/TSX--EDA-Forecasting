import os
import pandas as pd
from pathlib import Path
from flask import Flask, render_template_string
import panel as pn
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import perspective
import dtale
# ------// Panel App // ------

# TODO: Change layout of the app with template 
#       - use the data inside data/tsx_data.db
#       - check config for dockerization
#       - SHAP or LIME for model interpretation for LSTM
#       - ML Flow to monitor the application once deployed


df=pd.read_csv(Path('..'+'/tsx_data.csv').resolve())
df.rename(columns={'Unnamed: 0':'Date'}, inplace=True)
df['Date'] = pd.to_datetime(df['Date'])




df=df[df['Symbol'].str.contains('TSX:TD')]
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
    xaxis=dict(title='Date'))

from datetime import datetime, timedelta

# Initialize Flask app
flask_app = Flask(__name__)

# Initialize Panel extension
pn.extension('plotly', 'perspective')

# Check if the CSV file exists
csv_path = '/app/tsx_data.csv'
if not os.path.exists(csv_path):
    print("Error: tsx_data.csv not found.")
else:
    print("tsx_data.csv found. Proceeding with data loading.")

# Load and process the data
df = pd.read_csv(Path(csv_path).resolve())
df.rename(columns={'Unnamed: 0': 'Date'}, inplace=True)
df['Date'] = pd.to_datetime(df['Date'])

# Filter data for a specific stock symbol
df = df[df['Symbol'].str.contains('TSX:TD')]

# Add Moving Averages (50-day, 200-day)
df['MA50'] = df['Close'].rolling(window=50).mean()
df['MA200'] = df['Close'].rolling(window=200).mean()

# Create the candlestick chart for the last 3 months
three_months_ago = datetime.now() - timedelta(days=90)
df_last_3_months = df[df['Date'] > three_months_ago]

fig_candlestick = go.Figure(data=[go.Candlestick(
    x=df_last_3_months['Date'],
    open=df_last_3_months['Open'],
    high=df_last_3_months['High'],
    low=df_last_3_months['Low'],
    close=df_last_3_months['Close'],
    name='Price'
)])
fig_candlestick.update_layout(height=600, width=1000, title_text="Candlestick Chart - Last 3 Months")

# Create a line plot for Closing Prices with Moving Averages
fig_ma = go.Figure()
fig_ma.add_trace(go.Scatter(x=df['Date'], y=df['Close'], mode='lines', name='Close Price'))
fig_ma.add_trace(go.Scatter(x=df['Date'], y=df['MA50'], mode='lines', name='50-day MA'))
fig_ma.add_trace(go.Scatter(x=df['Date'], y=df['MA200'], mode='lines', name='200-day MA'))
fig_ma.update_layout(title='Closing Price with Moving Averages', xaxis_title='Date', yaxis_title='Price')

# Panel tabs
pane1 = pn.pane.Plotly(fig_ma, sizing_mode='stretch_both')
pane2 = pn.pane.Plotly(fig_candlestick, sizing_mode='stretch_both')
df_pane = pn.pane.Perspective(df, sizing_mode='stretch_both')

app_panel = pn.Tabs(
    ('Moving Averages', pane1),
    ('Candlestick', pane2),
    ('Data Table', df_pane)
)

# Flask route to embed Panel as an iframe
@flask_app.route('/')
def index():
    panel_url = "http://localhost:5006"  # Adjust if using a different host/port
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
    pn.serve(app_panel, port=5006, address='0.0.0.0', show=False)

    # Option 2: Run Flask app (disable this if using Panel standalone)
    flask_app.run(host='0.0.0.0', port=8080)
