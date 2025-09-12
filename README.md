# TSX-EDA-Forecasting

Capstone Project: Data Analysis & Forecasting for Canadian Financial Markets

## Overview

This repository provides an interactive analytics and forecasting platform for Canadian financial markets, focusing on equities listed on the TSX and TSXV, with extensions to macroeconomic indicators, cryptocurrencies, and commodities. The app leverages ETL pipelines to ingest market data, applies machine learning models (XGBoost, LSTM, ARIMA), and visualizes results using Panel and Plotly dashboards.

## Features

- **ETL Pipelines**: Automated fetching and upsertion of daily TSX/TSXV stock data from Alpha Vantage and StockAnalysis APIs.
- **Database Integration**: SQLite3 backend for storing raw and processed market data, tickers, and forecast results.
- **Forecasting Models**: Implements XGBoost, LSTM, and ARIMA models for time series forecasting of stock prices.
- **Interactive Dashboard**: Panel-based web app with:
  - Candlestick charts
  - RSI and Moving Averages
  - Forecast comparison (actual vs. predicted prices)
  - Company-level market cap and revenue display
- **Dockerized Deployment**: Ready-to-deploy with Docker and docker-compose.

## Current Data Coverage

- TSX and TSXV equities (daily OHLCV data)
- Company metadata (market cap, revenue, etc.)
- Forecast results for selected tickers

## Tech Stack

- **Python 3.10**: Core language for ETL, modeling, and dashboard
- **Panel**: Interactive dashboard framework
- **Plotly**: Data visualization (candlestick, line, RSI, moving averages, forecast comparison)
- **Flask**: Web server integration for dashboard embedding
- **SQLite3**: Local database for storing market data, tickers, and forecasts
- **Pandas**: Data manipulation and analysis
- **Scikit-learn**: Preprocessing, metrics, and train/test splitting
- **XGBoost**: Gradient boosting for time series forecasting
- **TensorFlow/Keras**: LSTM neural network models
- **Darts**: Time series modeling (LSTM, ARIMA)
- **Statsmodels**: ARIMA forecasting
- **Requests**: API calls to Alpha Vantage and StockAnalysis
- **Docker**: Containerization for deployment
- **GitHub Actions**: CI/CD workflows
- **Discord Webhooks**: ETL pipeline notifications

See [requirements.txt](requirements.txt) for full Python dependencies.

## Getting Started

1. **Clone the repo**
2. **Install dependencies** (see [requirements.txt](requirements.txt))
3. **Configure environment variables** in `utilz/.env` (API keys, Discord webhook)
4. **Run ETL scripts** to populate the database
5. **Launch the dashboard**:
   ```sh
   python app/app.py
   ```
   Or deploy using Docker:
   ```sh
   docker-compose up
   ```


## License

MIT
