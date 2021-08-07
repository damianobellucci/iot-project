# rimane da mettere il nuovo dato in database
import pandas as pd
from datetime import datetime
from statsmodels.tsa.arima.model import ARIMA
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import datetime
import matplotlib.pyplot as plt

from pmdarima import auto_arima


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

len_dataset = len(dataset)
len_test = 50

train = dataset[0:len_dataset-len_test]
len_train = len(train)
test = dataset[len(train)-1:]


#stepwise_fit = auto_arima(train, trace=True, suppress_warnings=True)
model = ARIMA(train, order=(1, 1, 2))
model_fit = model.fit()

forecast = model_fit.predict(start=len_train-1, end=len_dataset-1)


train.plot()
test.plot()
forecast.plot()
plt.ylim([0, 50])
plt.xlim([0, 1400])
plt.show()
