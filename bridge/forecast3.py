#rimane da mettere il nuovo dato in database
import pandas as pd
from datetime import datetime
from statsmodels.tsa.arima.model import ARIMA
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import datetime


lastValueControlled= None
lastValueInDb=None

token = 'h_ePgBkIpz-64X3GZmeNrlBFiVj4rF0hDJPyupnSRSlq9XiVwoaeaWvvpjDKpDr1Tv-2EgfVvGtpLu1qJKw7NA=='
org = 'damiano'
bucket = 'damiano'
client = InfluxDBClient(url="http://localhost:8086", token=token, org=org)
query_api = client.query_api()
write_api = client.write_api(write_options=SYNCHRONOUS)

query = 'from(bucket:"damiano")' \
        ' |> range(start:2021-08-06T12:00:00Z)'\
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
        lastValueInDb=a.tail(1).index[0]

        if lastValueControlled!=lastValueInDb:
                lastValueControlled=lastValueInDb
                a.index = pd.DatetimeIndex(a.index).to_period('S')
                converted = lastValueInDb.to_pydatetime()
                converted =converted+ datetime.timedelta(seconds=1)
                fined = converted +  datetime.timedelta(seconds=10)
                #print(converted)
                model = ARIMA(a, order=(7,0,1))
                model_fit = model.fit()
                start_index = len(a)
                end_index = start_index + 20
                forecast = model_fit.predict(start=converted, end=fined)
                #forecast = model_fit.predict(start=start_index,end=end_index)

                print(forecast.tail(1))
                print(type(forecast.tail(1)))
                timestamp_forecasted_value = forecast.tail(1).index[0]
                value_forecasted = forecast.tail(1).values[0]
              
                point = Point("mem").tag("host50", "host1").field("forecast_temperature",value_forecasted).time(str(timestamp_forecasted_value))
                write_api.write(bucket, org, point)
