import pandas as pd
from darts import TimeSeries
from darts.models import RNNModel
from darts.metrics import mape
from sklearn.preprocessing import MinMaxScaler

# Load the data
df = pd.read_csv('your_data.csv', parse_dates=['Date'])
df.set_index('Date', inplace=True)

# Preprocess the data
scaler = MinMaxScaler()
df['Close'] = scaler.fit_transform(df[['Close']])

# Create a TimeSeries object
series = TimeSeries.from_dataframe(df, 'Date', 'Close')

# Split the data into training and validation sets
train, val = series.split_before(0.8)

# Define the LSTM model
model = RNNModel(
    model='LSTM',
    input_chunk_length=30,
    output_chunk_length=7,
    n_epochs=100,
    random_state=42
)

# Train the model
model.fit(train)

# Make predictions
pred = model.predict(len(val))

# Evaluate the model
error = mape(val, pred)
print(f'MAPE: {error:.2f}%')

# Inverse transform the predictions
pred = scaler.inverse_transform(pred.values())
val = scaler.inverse_transform(val.values())

# Plot the results
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))
plt.plot(df.index, df['Close'], label='Actual')
plt.plot(val.time_index, pred, label='Predicted')
plt.legend()
plt.show()



df[]