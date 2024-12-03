import pandas as pd
from darts import TimeSeries
from darts.models import RNNModel
from darts.metrics import mape
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import numpy as np
from darts import TimeSeries
from darts.models import TFTModel, NBEATSModel, AutoARIMA
from darts.metrics import mape, rmse
from darts.dataprocessing.transformers import Scaler
import matplotlib.pyplot as plt
import darts
# from darts.models import LSTMModel



import pandas as pd
import numpy as np
from darts import TimeSeries
from darts.models import AutoARIMA, TFTModel, NBEATSModel
from darts.metrics import mape, rmse
from sklearn.ensemble import GradientBoostingRegressor
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

# Load the data
df = pd.read_csv('../tsx_data.csv', parse_dates=['Date'])
df['Date'] = pd.to_datetime(df['Date'])
df.set_index('Date', inplace=True)
df.reset_index(inplace=True)
data=df

# Extract symbols
symbols = data['Symbol'].unique()
results = {}

# Iterate through each symbol
for symbol in symbols:
    print(f"Processing symbol: {symbol}")
    symbol_data = data[data['Symbol'] == symbol]

    # Prepare TimeSeries for Darts
    symbol_data.index=symbol_data['Date']

    symbol_data['Date'].diff()

    ts = TimeSeries.from_dataframe(symbol_data, 'Date', 'Close', fill_missing_dates=True)

    ts_train, ts_val = ts.split_before(0.8)

    # Create temporal features for XGBRegressor
    symbol_data['day_of_week'] = symbol_data.index.dayofweek
    symbol_data['month'] = symbol_data.index.month
    symbol_data['lag_1'] = symbol_data['Close'].shift(1)
    symbol_data['lag_2'] = symbol_data['Close'].shift(2)
    symbol_data.dropna(inplace=True)

    symbol_data = symbol_data.asfreq('B', method=None)  # 'B' sets the frequency to business days
    symbol_data = symbol_data.ffill() 
    
    X = symbol_data[['day_of_week', 'month', 'lag_1', 'lag_2']]
    y = symbol_data['Close']
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, shuffle=False)

    # Scale data
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)

    # Fit XGBRegressor
    xgb_model = XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=3)
    xgb_model.fit(X_train_scaled, y_train)
    xgb_forecast = xgb_model.predict(X_val_scaled)

    # AutoARIMA Baseline
    arima_model = AutoARIMA()
    arima_model.fit(ts_train)
    arima_forecast = arima_model.predict(len(ts_val))
    
    # TFTModel (Tiny Time Mixer)
    tft_model = TFTModel(input_chunk_length=30, output_chunk_length=30, n_epochs=50)
    tft_model.fit(ts_train)
    tft_forecast = tft_model.predict(len(ts_val))

    # NBEATSModel
    nbeats_model = NBEATSModel(input_chunk_length=30, output_chunk_length=30, n_epochs=50)
    nbeats_model.fit(ts_train)
    nbeats_forecast = nbeats_model.predict(len(ts_val))

    # Evaluation Metrics
    results[symbol] = {
        "XGBoost": {"MAPE": mape(ts_val.values(), xgb_forecast), "RMSE": rmse(ts_val.values(), xgb_forecast)},
        "AutoARIMA": {"MAPE": mape(ts_val, arima_forecast), "RMSE": rmse(ts_val, arima_forecast)},
        "TFT": {"MAPE": mape(ts_val, tft_forecast), "RMSE": rmse(ts_val, tft_forecast)},
        "NBEATS": {"MAPE": mape(ts_val, nbeats_forecast), "RMSE": rmse(ts_val, nbeats_forecast)},
    }

    # Visualization
    plt.figure(figsize=(12, 6))
    ts_val.plot(label="Actual", lw=2)
    plt.plot(ts_val.time_index, xgb_forecast, label="XGBoost", linestyle='--')
    arima_forecast.plot(label="AutoARIMA")
    tft_forecast.plot(label="TFT")
    nbeats_forecast.plot(label="NBEATS")
    plt.title(f"Forecast vs Actual for {symbol}")
    plt.legend()
    plt.show()

# Print Results
for symbol, metrics in results.items():
    print(f"Symbol: {symbol}")
    for model, scores in metrics.items():
        print(f"  {model} - MAPE: {scores['MAPE']:.2f}, RMSE: {scores['RMSE']:.2f}")
