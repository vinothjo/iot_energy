from datetime import timedelta

import pytz
#from cassandra.cqlengine import columns
#from cassandra.util import Date
import datetime


def monthdelta(date, delta):
    m, y = (date.month+delta) % 12, date.year + ((date.month)+delta-1) // 12
    if not m: m = 12
    d = min(date.day, [31,
        29 if y%4==0 and not y%400==0 else 28,31,30,31,30,31,31,30,31,30,31][m-1])
    return date.replace(day=d,month=m, year=y)

def getcurr_datetime_String(zone='Asia/Singapore', format="%Y-%m-%dT%H:%M:%SZ"):
    timezone = pytz.timezone(zone)
    dt = timezone.localize(datetime.datetime.now())
    return dt.strftime(format)


def getcurr_datetime( zone='Asia/Singapore'):
    timezone = pytz.timezone(zone)
    dt = timezone.localize(datetime.datetime.now())
    format = "%Y-%m-%d %H:%M:%S"
    return datetime.datetime.strptime(dt.strftime(format), format)

def getcurr_datetime1(zone='Asia/Singapore',add_hr=0):
    timezone = pytz.timezone(zone)
    dt = timezone.localize(datetime.datetime.now())
    format = "%Y-%m-%d %H:%M:%S"
    print(dt)
    return datetime.datetime.strptime(dt.strftime(format),format) + timedelta(hours=int(add_hr))

today = datetime.date.today()

cur_month = today.month
cur_date = today.day
cur_year = today.year
cur_week_day = today.weekday()

print(cur_month)
print(cur_date)
print(cur_year)
print(cur_week_day)

month_end_point = datetime.datetime.strptime("01-" + str(cur_month) + "-" + str(cur_year), '%d-%m-%Y')#+  " 00:00:00.00"

#datetime_object = datetime.datetime.strptime("01-" + str(cur_month) + "-" + str(cur_year), '%d-%m-%Y')
print(monthdelta(month_end_point, -1).strftime("%d-%m-%Y %H:%M:%S"))

today = datetime.date.today()
cur_week_day = today.weekday()
last_hour_date_time = datetime.datetime.now() - timedelta(days=cur_week_day)
cur_hour_date_time = datetime.datetime.now() - timedelta(days=(cur_week_day+7))
print(last_hour_date_time.strftime("%d-%m-%Y %H"))
print(cur_hour_date_time.strftime("%d-%m-%Y %H"))

print(datetime.datetime.strptime("20180219184000000", "%Y%m%d%H%M%S%f").strftime("%Y-%m-%dT%H:%M:%SZ"))
sg_timezone = pytz.timezone('Asia/Singapore')
d = sg_timezone.localize(datetime.datetime.now())
print(d)
print(datetime.datetime.utcnow())

print(getcurr_datetime_String())
print(getcurr_datetime())
print(getcurr_datetime1(add_hr=-1))
print(str(type(getcurr_datetime_String())))
print(str(type(getcurr_datetime())))


