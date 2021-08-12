from influxdb_client import InfluxDBClient, Point, WriteOptions
import pandas as pd
import time
from prophet import Prophet
import datetime


from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

token = 'h_ePgBkIpz-64X3GZmeNrlBFiVj4rF0hDJPyupnSRSlq9XiVwoaeaWvvpjDKpDr1Tv-2EgfVvGtpLu1qJKw7NA=='
org = 'damiano'
bucket = 'agg-project'
client = InfluxDBClient(url="http://localhost:8086", token=token, org=org)
query_api = client.query_api()
write_api = client.write_api(write_options=SYNCHRONOUS)


lastChecked=None

while(True):
    query = 'from(bucket:"agg-project")' \
            ' |> range(start:-1h, stop:now())'\
            ' |> filter(fn: (r) => r._measurement == "samples")' \
            ' |> filter(fn: (r) => r._field == "temperature")'

    result = client.query_api().query(org=org, query=query)



    raw = []
    for table in result:
        for record in table.records:
            raw.append((record.get_value(), record.get_time()+datetime.timedelta(hours=2)))

    lastSample =raw[len(raw)-1]

    if(lastSample!=lastChecked):
        lastChecked = lastSample
        #print("=== influxdb query into dataframe ===")

        df = pd.DataFrame(raw, columns=['y', 'ds'], index=None)
        for col in df.select_dtypes(['datetimetz']).columns:
            df[col] = df[col].dt.tz_convert(None)

        df.head()

        #print(df)

        m = Prophet()
        m.fit(df)

        future = m.make_future_dataframe(periods=1,freq='60s')

        forecast = m.predict(future)

        forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail()

        forecast['measurement'] = "forecast"
   
        cp = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper', 'measurement']].copy()



        lines = [str(cp["measurement"][d])
                + ",type=forecast"
                + " "
                + "yhat=" + str(cp["yhat"][d]) + ","
                + "yhat_lower=" + str(cp["yhat_lower"][d]) + ","
                + "yhat_upper=" + str(cp["yhat_upper"][d])
                + " " + str(int(time.mktime(cp['ds'][d].timetuple()))) + "000000000" for d in range(len(cp))]
        
        print(type(lines))
        lines=[lines[len(lines)-1]]
        _write_client = client.write_api(write_options=WriteOptions(batch_size=1000,
                                                                    flush_interval=10_000,
                                                                    jitter_interval=2_000,
                                                                    retry_interval=5_000))

        _write_client.write(bucket, org, lines)

