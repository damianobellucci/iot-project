# rimane da mettere il nuovo dato in database
import pandas as pd
from datetime import datetime
from statsmodels.tsa.arima.model import ARIMA
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import datetime

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
        ' |> filter(fn: (r) => r._measurement == "mem")' \
        ' |> filter(fn: (r) => r._field == "temperature")'

while(True):
    result = client.query_api().query(org=org, query=query)

    raw = []
    for table in result:
        for record in table.records:
            raw.append((record.get_value(), record.get_time()))
    idx = [x[1] for x in raw]
    vals = [x[0] for x in raw]

    a = pd.Series(vals, index=idx)
    lastValueInDb = a.tail(1).index[0]

    if lastValueControlled != lastValueInDb:
        lastValueControlled = lastValueInDb
        a.index = pd.DatetimeIndex(a.index).to_period('S')
        converted = lastValueInDb.to_pydatetime()
        converted = converted + datetime.timedelta(seconds=1)
        fined = converted + datetime.timedelta(seconds=10)
        # print(converted)
        stepwise_fit = auto_arima(a, trace=True, suppress_warnings=True)
        model = ARIMA(a, order=(5, 0, 0))
        model_fit = model.fit()
        start_index = len(a)
        end_index = start_index + 20
        forecast = model_fit.predict(start=converted, end=fined)
        #forecast = model_fit.predict(start=start_index,end=end_index)

        print(forecast.tail(1))
        print(type(forecast.tail(1)))
        timestamp_forecasted_value = forecast.tail(1).index[0]
        value_forecasted = forecast.tail(1).values[0]

        point = Point("mem").tag("host50", "host1").field(
            "forecast_temperature", value_forecasted).time(str(timestamp_forecasted_value))
        write_api.write(bucket, org, point)
