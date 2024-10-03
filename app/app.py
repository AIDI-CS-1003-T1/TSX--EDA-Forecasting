import panel as pn 
import pandas as pd
from pathlib import Path
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ------// Panel App // ------

# TODO: Create a Panel app for EDA on TSX data  
#       - use the data inside data/tsx_data.db
#      - create a line char

df=pd.read_csv(Path('..'+'/tsx_data.csv').resolve())
df.rename(columns={'Unnamed: 0':'Date'}, inplace=True)
df['Date'] = pd.to_datetime(df['Date'])

df=df[df['Symbol'].str.contains('TD')]


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

df



# 1. Candlestick Chart with Volume
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                    vertical_spacing=0.03, subplot_titles=('Candlestick', 'Volume'), 
                    row_width=[0.7, 0.3])

fig.add_trace(go.Candlestick(x=df['Date'],
                open=df['Open'], high=df['High'],
                low=df['Low'], close=df['Close'],
                name='Price'),
                row=1, col=1)

fig.add_trace(go.Bar(x=df['Date'], y=df['Volume'], name='Volume'),
              row=2, col=1)

fig.update_layout(height=600, width=1000, title_text="Candlestick Chart with Volume")
fig.show()

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




# Close vs. Volume Scatter Plot
fig = go.Figure()
fig.add_trace(go.Scatter(x=df['Open'], y=df['Volume'], mode='markers', name='Close vs. Volume'))
fig.update_layout(title='Close vs. Volume', xaxis_title='Close Price', yaxis_title='Volume')
# change size and color of markers
fig.update_traces(marker=dict(size=4, color='blue'))
# change   length and width of plot
fig.update_layout(width=800, height=600)
fig.show()







def main():
    pass
    return

if __name__ == "__main__":
    main()

