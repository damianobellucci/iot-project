# rimane da mettere il nuovo dato in database
import pandas as pd
from datetime import datetime
from statsmodels.tsa.arima.model import ARIMA
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import datetime
import matplotlib.pyplot as pyplot
from math import sqrt
from pmdarima import auto_arima
from sklearn.metrics import mean_squared_error

lastValueControlled = None
lastValueInDb = None

token = '4pQidiCvurOgttstoaQIKrwUdk-9dnGxb4DBRXuqYX9JNE56KIsTSFxPaoP8RVEbxI2fFueACaP0C8U3d1iJgw=='
org = 'damiano'
bucket = 'damiano'
client = InfluxDBClient(url="http://localhost:8086", token=token, org=org)
query_api = client.query_api()
write_api = client.write_api(write_options=SYNCHRONOUS)

query = 'from(bucket:"damiano")' \
        ' |> range(start:2021-08-07T06:50:00Z)'\
        ' |> filter(fn: (r) => r._measurement == "training")' \
        ' |> filter(fn: (r) => r._field == "temperature")'

result = client.query_api().query(org=org, query=query)

raw = []
for table in result:
    for record in table.records:
        raw.append((record.get_value(), record.get_time()))
idx = [x[1] for x in raw]
vals = [x[0] for x in raw]

dataset = pd.Series(vals)


X = dataset.values
size = int(len(X) * 0.80)
train, test = X[0:size], X[size:len(X)]
history = [x for x in train]
predictions = list()


for t in range(len(test)):
    print(t)

    stepwise_fit = auto_arima(history, trace=True, suppress_warnings=True)
    tupla = tuple(str(stepwise_fit)[6:13])
    parameters = (int(tupla[1]), int(tupla[3]), int(tupla[5]))

    model = ARIMA(history, order=parameters)
    model_fit = model.fit()
    output = model_fit.forecast()
    yhat = output[0]
    predictions.append(yhat)
    obs = test[t]
    history.append(obs)

# evaluate forecasts
rmse = sqrt(mean_squared_error(test, predictions))
print('Test RMSE: %.3f' % rmse)
# plot forecasts against actual outcomes
pyplot.plot(test, label="temperature test set")
pyplot.plot(predictions, color='red', label='temperature forecast')

pyplot.legend(loc="upper left")
pyplot.show()
