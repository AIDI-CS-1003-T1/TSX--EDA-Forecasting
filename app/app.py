import panel as pn 
import pandas as pd
from pathlib import Path
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import perspective
import dtale
# ------// Panel App // ------

# TODO: Create a Panel app for EDA on TSX data  
#       - use the data inside data/tsx_data.db
#      - create a line char

df=pd.read_csv(Path('..'+'/tsx_data.csv').resolve())
df.rename(columns={'Unnamed: 0':'Date'}, inplace=True)
df['Date'] = pd.to_datetime(df['Date'])


perspective.open_browser()

df.memory_usage(deep=True)/(1024 * 1024)

df=df[df['Symbol'].str.contains('TSX:TD')]

dir(dtale.show(df).open_browser())

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

fig.show()

from datetime import datetime, timedelta

# Calculate the date 3 months ago
three_months_ago = datetime.now() - timedelta(days=90)

# Filter the DataFrame to include only the last 3 months
df_last_3_months = df[df['Date'] > three_months_ago]

fig = go.Figure(data=[go.Candlestick(x=df_last_3_months['Date'],
                open=df_last_3_months['Open'], high=df_last_3_months['High'],
                low=df_last_3_months['Low'], close=df_last_3_months['Close'],
                name='Price')])

fig.update_layout(height=600, width=1000, title_text="Candlestick Chart - Last 3 Months")
fig.show()

pane2=pn.pane.Plotly(fig)


# 2. Line Plot for Closing Prices
fig = go.Figure()
fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], mode='lines', name='Close Price'))
fig.update_layout(title='Closing Price Over Time', xaxis_title='Date', yaxis_title='Price')
fig.show()

# 3. Area Plot for Price Range
fig = go.Figure()
fig.add_trace(go.Scatter(x=df['Date'], y=df['High'], fill=None, mode='lines', line_color='rgba(0,100,80,0.2)', name='High'))
fig.add_trace(go.Scatter(x=df['Date'], y=df['Low'], fill='tonexty', mode='lines', line_color='rgba(0,100,80,0.2)', name='Low'))
fig.update_layout(title='Price Range Over Time', xaxis_title='Date', yaxis_title='Price')
fig.show()

# 4. Moving Averages
df['MA50'] = df['Close'].rolling(window=50).mean()
df['MA200'] = df['Close'].rolling(window=200).mean()

fig = go.Figure()
fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], mode='lines', name='Close Price'))
fig.add_trace(go.Scatter(x=df['Date'], y=df['MA50'], mode='lines', name='50-day MA'))
fig.add_trace(go.Scatter(x=df['Date'], y=df['MA200'], mode='lines', name='200-day MA'))
fig.update_layout(title='Closing Price with Moving Averages', xaxis_title='Date', yaxis_title='Price')
fig.show()

pane1 = pn.pane.Plotly(fig,sizing_mode='stretch_both')

# 5. Relative Strength Index (RSI)
def compute_rsi(data, time_window):
    '''
    Compute the Relative Strength Index (RSI) for a given time window.

    Parameters:
    data (pd.Series): The time series data.
    time_window (int): The time window for calculating RSI.

    Returns:
    pd.Series: The RSI values.

    
    '''
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

fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                    vertical_spacing=0.03, subplot_titles=('Closing Price', 'RSI'), 
                    row_width=[0.7, 0.3])

fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], mode='lines', name='Close Price'),
              row=1, col=1)
fig.add_trace(go.Scatter(x=df['Date'], y=df['RSI'], mode='lines', name='RSI'),
              row=2, col=1)

fig.update_layout(height=600, width=1000, title_text="Closing Price and RSI")
fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
fig.show()




df_pane = pn.pane.Perspective(df, sizing_mode='stretch_both')



# serve the panel app
# df_pane = pn.pane.Perspective(df, height='100%', width='100%')
app = pn.Tabs(('Pane 1', pane1), ('Pane 2', pane2), ('Data', df_pane))


app


app.show(host='0.0.0.0')



# ------// Panel App // ------pip install --upgrade pip setuptools wheel

def main():
    pass
    return

if __name__ == "__main__":
    main()


    