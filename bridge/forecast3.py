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
import datetime

lastValueControlled= None
lastValueInDb=None

while(True):
        
        token = 'h_ePgBkIpz-64X3GZmeNrlBFiVj4rF0hDJPyupnSRSlq9XiVwoaeaWvvpjDKpDr1Tv-2EgfVvGtpLu1qJKw7NA=='
        org = 'damiano'
        bucket = 'damiano'
        client = InfluxDBClient(url="http://localhost:8086", token=token, org=org)
        query_api = client.query_api()
        write_api = client.write_api(write_options=SYNCHRONOUS)


        query = 'from(bucket:"damiano")' \
                ' |> range(start:2021-08-04T18:00:00Z, stop:2021-08-04T18:05:00Z)'\
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
        lastValueInDb=a.tail(1).index[0]


        if lastValueControlled!=lastValueInDb:

                lastValueControlled=lastValueInDb

                a.index = pd.DatetimeIndex(a.index).to_period('S')

                converted = lastValueInDb.to_pydatetime()

                converted =converted+ datetime.timedelta(seconds=1)

                fined = converted +  datetime.timedelta(seconds=10)

                print(converted)

                model = ARIMA(a, order=(7,0,1))
                model_fit = model.fit()

                start_index = len(a)
                end_index = start_index + 20

                forecast = model_fit.predict(start=converted, end=fined)
                #forecast = model_fit.predict(start=start_index,end=end_index)


                try:
                        print(forecast.tail(1))
                except KeyError as e:
                        print("ciao")

