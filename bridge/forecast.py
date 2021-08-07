
from influxdb_client import InfluxDBClient, Point, WriteOptions
import pandas as pd
import time
from prophet import Prophet
from datetime import datetime


from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

token = 'h_ePgBkIpz-64X3GZmeNrlBFiVj4rF0hDJPyupnSRSlq9XiVwoaeaWvvpjDKpDr1Tv-2EgfVvGtpLu1qJKw7NA=='
org = 'damiano'
bucket = 'damiano'
client = InfluxDBClient(url="http://localhost:8086", token=token, org=org)
query_api = client.query_api()
write_api = client.write_api(write_options=SYNCHRONOUS)

query = 'from(bucket:"damiano")' \
        ' |> range(start:2021-08-04T14:00:00Z, stop:2021-08-04T21:20:00Z)'\
        ' |> filter(fn: (r) => r._measurement == "mem")' \
        ' |> filter(fn: (r) => r._field == "temperature")'

result = client.query_api().query(org=org, query=query)

raw = []
for table in result:
    for record in table.records:
        raw.append((record.get_value(), record.get_time()))
# print(raw[0:])


print("=== influxdb query into dataframe ===")

df = pd.DataFrame(raw, columns=['y', 'ds'], index=None)
for col in df.select_dtypes(['datetimetz']).columns:
    df[col] = df[col].dt.tz_convert(None)

df.head()

print(df)

m = Prophet()
m.fit(df)

future = m.make_future_dataframe(periods=2)

forecast = m.predict(future)
print("aaaa")
forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail()

print(forecast)

forecast['measurement'] = "views"

cp = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper', 'measurement']].copy()
lines = [str(cp["measurement"][d])
         + ",type=forecast"
         + " "
         + "yhat=" + str(cp["yhat"][d]) + ","
         + "yhat_lower=" + str(cp["yhat_lower"][d]) + ","
         + "yhat_upper=" + str(cp["yhat_upper"][d])
         + " " + str(int(time.mktime(cp['ds'][d].timetuple()))) + "000000000" for d in range(len(cp))]


_write_client = client.write_api(write_options=WriteOptions(batch_size=1000,
                                                            flush_interval=10_000,
                                                            jitter_interval=2_000,
                                                            retry_interval=5_000))

_write_client.write(bucket, org, lines)

_write_client.__del__()
client.__del__()
