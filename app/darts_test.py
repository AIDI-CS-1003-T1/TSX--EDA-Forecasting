import pandas as pd
import sql3
import numpy as np
from sklearn.metrics import mean_squared_error
from xgboost import XGBRegressor
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
from keras.models import Sequential
from keras.layers import LSTM, Dense
from darts.models import ARIMA
from statsmodels.tsa.arima.model import ARIMA
from darts import TimeSeries

# Database Path
db_path = '../data/stocks.db'

# Load Data
df = sql3.db_fetch_as_frame(db_path=db_path, query='select * from tsx_data')
df['Tick'] = df['Symbol'].apply(lambda x: x.split('.')[0])

forecast_df = sql3.db_fetch_as_frame(db_path=db_path, query='select * from forecast_results')

all_ticks = df['Tick'].unique().tolist()
forecasted_ticks = forecast_df['Tick'].unique().tolist()
pending = list(set(all_ticks) - set(forecasted_ticks))
data = df[df['Tick'].isin(pending)]


# Function to Prepare Data
def prepare_data(company_symbol):
    company_data = data[data['Tick'] == company_symbol].sort_values('Date')
    company_data['Date'] = pd.to_datetime(company_data['Date'])
    company_data.set_index('Date', inplace=True)

    # Feature Engineering for XGBoost & LSTM
    company_data['Lag_1'] = company_data['Close'].shift(1)
    company_data['Lag_2'] = company_data['Close'].shift(2)
    company_data['Lag_3'] = company_data['Close'].shift(3)
    company_data['Rolling_Mean_5'] = company_data['Close'].rolling(window=5).mean()
    company_data['Rolling_Std_5'] = company_data['Close'].rolling(window=5).std()
    company_data['Exp_Moving_Avg_5'] = company_data['Close'].ewm(span=5).mean()
    company_data.dropna(inplace=True)

    X = company_data[['Lag_1', 'Lag_2', 'Lag_3', 'Rolling_Mean_5', 'Rolling_Std_5', 'Exp_Moving_Avg_5']]
    y = company_data['Close']
    
    return train_test_split(X, y, test_size=0.1, shuffle=False), company_data


# XGBoost Model
def forecast_xgb(train, test):
    xgb = XGBRegressor(n_estimators=200, learning_rate=0.1, max_depth=4, subsample=0.9, colsample_bytree=0.9)
    xgb.fit(train[0], train[1])  
    return xgb.predict(test[0])


# LSTM Model
def forecast_lstm(train, test):
    X_train = train[0].values.reshape(-1, 1, train[0].shape[1])
    y_train = train[1]
    X_test = test[0].values.reshape(-1, 1, test[0].shape[1])

    model = Sequential()
    model.add(LSTM(50, activation='relu', input_shape=(1, train[0].shape[1])))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')

    model.fit(X_train, y_train, epochs=50, batch_size=16, verbose=0)

    return model.predict(X_test).flatten()


# ARIMA Forecasting
def forecast_arima(company_data):
    series = TimeSeries.from_dataframe(company_data, 'Date', 'Close')
    train, test = series.split_after(0.9)  # 90% train, 10% test

    model = ARIMA(p=5, d=1, q=2)  # You can fine-tune p, d, q
    model.fit(train)

    forecast = model.predict(len(test))
    return forecast.values(), test.time_index


# Function to Plot Forecasts
def plot_forecasts(company_name, actual, xgb_forecast, lstm_forecast, arima_forecast, test_index):
    plt.figure(figsize=(12, 6))
    plt.plot(test_index, actual, label='Actual', color='black')
    plt.plot(test_index, xgb_forecast, label='XGB Forecast', linestyle='--', color='blue')
    plt.plot(test_index, lstm_forecast, label='LSTM Forecast', linestyle='--', color='orange')
    plt.plot(test_index, arima_forecast, label='ARIMA Forecast', linestyle='--', color='red')

    plt.title(f'Forecast Comparison for {company_name}')
    plt.xlabel('Date')
    plt.ylabel('Close Price')
    plt.legend()
    plt.grid()
    plt.show()


# Running Forecasts for All Companies
forecast_results = pd.DataFrame()

companies = data['Tick'].unique()

for company in companies: 
    (X_train, X_test, y_train, y_test), full_data = prepare_data(company)

    # XGBoost Forecast
    xgb_forecast = forecast_xgb((X_train, y_train), (X_test, y_test))
    xgb_mape = mean_absolute_percentage_error(y_test.values, xgb_forecast)

    # LSTM Forecast
    lstm_forecast = forecast_lstm((X_train, y_train), (X_test, y_test))
    lstm_mape = mean_absolute_percentage_error(y_test.values, lstm_forecast)

    # ARIMA Forecast
    arima_forecast, test_index = forecast_arima(full_data)
    arima_mape = mean_absolute_percentage_error(y_test.values, arima_forecast)

    print(f"{company} - XGB MAPE: {xgb_mape:.2f}%, LSTM MAPE: {lstm_mape:.2f}%, ARIMA MAPE: {arima_mape:.2f}%")

    temp_df = pd.DataFrame({
        'Tick': company,
        'Date': test_index,
        'Actual': y_test.values,
        'XGB_Forecast': xgb_forecast,
        'LSTM_Forecast': lstm_forecast,
        'ARIMA_Forecast': arima_forecast
    })
    forecast_results = pd.concat([forecast_results, temp_df], ignore_index=True)

    plot_forecasts(
        company,
        y_test.values, 
        xgb_forecast,
        lstm_forecast,
        arima_forecast,
        test_index  
    )

forecast_results['Date'] = forecast_results['Date'].astype('str')

# Store results in database
sql3.db_upsert(df=forecast_results, db_path=db_path, table_name='forecast_results', primary_keys=['Tick', 'Date'])
