from datetime import date, datetime
from dateutil import parser

a = "2021-08-04 18:06:52.417031+00:00"

b= parser.parse(a)

print(datetime.datetime(b))