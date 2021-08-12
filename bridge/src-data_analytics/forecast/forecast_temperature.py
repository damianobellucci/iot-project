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

token = 'h_ePgBkIpz-64X3GZmeNrlBFiVj4rF0hDJPyupnSRSlq9XiVwoaeaWvvpjDKpDr1Tv-2EgfVvGtpLu1qJKw7NA=='
org = 'damiano'
bucket = 'agg-project'
client = InfluxDBClient(url="http://localhost:8086", token=token, org=org)
query_api = client.query_api()
write_api = client.write_api(write_options=SYNCHRONOUS)


query = 'from(bucket:"agg-project")' \
        ' |> range(start:2021-08-11T18:38:00Z)'\
        ' |> filter(fn: (r) => r._measurement == "samples")' \
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

        #stepwise_fit = auto_arima(a, trace=True, suppress_warnings=True)
        #tupla = tuple(str(stepwise_fit)[6:13])
        #parameters = (int(tupla[1]), int(tupla[3]), int(tupla[5]))

        parameters = (3, 2, 1)
        model = ARIMA(a, order=parameters)

        model_fit = model.fit()
        forecast = model_fit.predict(start=converted, end=fined)

        timestamp_forecasted_value = forecast.tail(1).index[0]
        value_forecasted = forecast.tail(1).values[0]

        new_timestamp = lastValueInDb.to_pydatetime()
        new_timestamp = new_timestamp + datetime.timedelta(seconds=10)

        # point = Point("mem").tag("host50", "host1").field("forecast_temperature", value_forecasted).time(str(timestamp_forecasted_value))
        point = Point("forecast").field(
            "temperature_forecast", value_forecasted).time(str(new_timestamp))
        write_api.write(bucket, org, point)
