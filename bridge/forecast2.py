
import pandas as pd
import time
from prophet import Prophet
from datetime import datetime
from statsmodels.tsa.arima.model import ARIMA

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

from sklearn.metrics import mean_squared_error
from math import sqrt
from matplotlib import pyplot

token = 'h_ePgBkIpz-64X3GZmeNrlBFiVj4rF0hDJPyupnSRSlq9XiVwoaeaWvvpjDKpDr1Tv-2EgfVvGtpLu1qJKw7NA=='
org = 'damiano'
bucket = 'damiano'
client = InfluxDBClient(url="http://localhost:8086", token=token, org=org)
query_api = client.query_api()
write_api = client.write_api(write_options=SYNCHRONOUS)

query = 'from(bucket:"damiano")' \
        ' |> range(start:2021-08-04T18:00:00Z, stop:2021-08-04T21:10:00Z)'\
        ' |> filter(fn: (r) => r._measurement == "mem")' \
        ' |> filter(fn: (r) => r._field == "temperature")'

result = client.query_api().query(org=org, query=query)

raw = []
for table in result:
    for record in table.records:
        raw.append((record.get_value(), record.get_time()))


idx = [x[1] for x in raw]
vals = [x[0] for x in raw]

a = pd.Series(vals, index=idx)

# split into train and test sets
X = a.values
size = int(len(X) * 0.66)
train, test = X[0:size], X[size:len(X)]
history = [x for x in train]
predictions = list()
# walk-forward validation
for t in range(len(test)):
	model = ARIMA(history, order=(5,1,0))
	model_fit = model.fit()
	output = model_fit.forecast()
	yhat = output[0]
	predictions.append(yhat)
	obs = test[t]
	history.append(obs)
	print('predicted=%f, expected=%f' % (yhat, obs))


print(ARIMA.predict(output, start=30,end=40, exog=None, typ='linear', dynamic=False))

# evaluate forecasts
rmse = sqrt(mean_squared_error(test, predictions))
print('Test RMSE: %.3f' % rmse)
# plot forecasts against actual outcomes
pyplot.plot(test)
pyplot.plot(predictions, color='red')
pyplot.show()