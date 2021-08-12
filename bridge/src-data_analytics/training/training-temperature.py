from influxdb_client import InfluxDBClient, Point, WriteOptions
import pandas as pd
import time
from prophet import Prophet
import datetime
import matplotlib.pyplot as pyplot
from math import sqrt
from scipy.sparse import data

from sklearn.metrics import mean_squared_error

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from statsmodels.tsa.statespace.mlemodel import PredictionResults

token = 'h_ePgBkIpz-64X3GZmeNrlBFiVj4rF0hDJPyupnSRSlq9XiVwoaeaWvvpjDKpDr1Tv-2EgfVvGtpLu1qJKw7NA=='
org = 'damiano'
bucket = 'agg-project'
client = InfluxDBClient(url="http://localhost:8086", token=token, org=org)
query_api = client.query_api()
write_api = client.write_api(write_options=SYNCHRONOUS)



query = 'from(bucket:"agg-project")' \
        ' |> range(start:2021-08-12T11:30:00Z)'\
        ' |> filter(fn: (r) => r._measurement == "samples")' \
        ' |> filter(fn: (r) => r._field == "temperature")'

result = client.query_api().query(org=org, query=query)



raw = []
for table in result:
    for record in table.records:
        raw.append((record.get_value(), record.get_time()+datetime.timedelta(hours=2)))

lastSample =raw[len(raw)-1]


lastChecked = lastSample
#print("=== influxdb query into dataframe ===")

df = pd.DataFrame(raw, columns=['y', 'ds'], index=None)
for col in df.select_dtypes(['datetimetz']).columns:
    df[col] = df[col].dt.tz_convert(None)


df=df[0:10]

size = int(len(df) * 0.66)

train, test = df[0:size], df[size:len(df)]

history = train


predictions= []
for t in range(len(test)):
    history.head()
    m = Prophet()
    m.fit(history)
    future = m.make_future_dataframe(periods=1,freq='10s')
    forecast = m.predict(future)
    forecast[['ds', 'yhat']].tail()
    forecast['measurement'] = "forecast"
    cp = forecast[['ds', 'yhat']].copy()
    new_value_forecasted = cp.tail(1)
    predictions.append(new_value_forecasted)
    history = pd.concat([history,test[t:t+1]])

dfForecast = pd.concat(predictions)
prediction_temperature_values =dfForecast['yhat'].values.tolist()
a = pd.Series(prediction_temperature_values, dfForecast['ds'])


test_temperature_values =test['y'].values.tolist()
real = pd.Series(test_temperature_values, test['ds'])

dataset_temperature_values =df['y'].values.tolist()
datasetValues = pd.Series(dataset_temperature_values, df['ds'])

rmse = sqrt(mean_squared_error(test_temperature_values, prediction_temperature_values))
print('Test RMSE: %.3f' % rmse)

pyplot.plot(a, label="forecast temperature")
#pyplot.plot(real, label="temperature training set")
pyplot.plot(datasetValues, label="temperature")
pyplot.legend(loc="upper left")

pyplot.show()