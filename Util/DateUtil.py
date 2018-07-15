# ****************************************************
#  Project : Iot
#  Filename: controllers.py
#  Created : sv
#  Change history:
#  dd.mm.yyyy / developer name
#  18.02.2018 / sv
# ***************************************************
#   creating prescription  Controller
# ****************************************************

# Import flask dependencies
import pytz
from pytz import timezone
from datetime import datetime, timedelta
import math
sg_timezone = pytz.timezone('UTC')
class DateUtil():

    @staticmethod
    def get_TodayStr(zone='UTC'):
        timezone = pytz.timezone(zone)
        dt = timezone.localize(datetime.now())
        format = "%Y-%m-%d %H:%M:%S"
        return datetime.strptime(dt.strftime(format), format)
        return tody.strftime('%Y-%m-%d 00:00')

    @staticmethod
    def get_current_day(zone='UTC',add_hr=0):
        timezone = pytz.timezone(zone)
        dt = timezone.localize(datetime.now())
        format = "%Y-%m-%d 00:00:00"
        ret_day = datetime.strptime(dt.strftime(format),format) + timedelta(hours=int(add_hr))
        return ret_day


    @staticmethod
    def getcurr_datetime_String(zone='UTC',format="%Y-%m-%dT%H:%M:%SZ"):
        timezone = pytz.timezone(zone)
        dt = timezone.localize(datetime.now())
        return dt.strftime(format)

    @staticmethod
    def getcurr_datetime(zone='UTC',add_hr=0):
        timezone = pytz.timezone(zone)
        dt = timezone.localize(datetime.now())
        format = "%Y-%m-%d %H:%M:%S"
        return datetime.strptime(dt.strftime(format),format) + timedelta(hours=int(add_hr))




    @staticmethod
    def getlowest_min_date(zone='UTC',min=60):
        timezone = pytz.timezone(zone)
        now = sg_timezone.localize(datetime.now())
        nearest_min = math.ceil(now.minute / min) - 1
        # print(nearest_min)
        if (nearest_min > 0):
            # print(now.year, now.month, now.day, now.hour, round(nearest_min * min))
            str_val = str(now.year) + "-" + str(now.month) + "-" + str(now.day) + " " + str(now.hour) + ":" + str(
                round(nearest_min * min))
            now= datetime.strptime(str_val, "%Y-%m-%d %H:%M")
        else:
            str_val = str(now.year) + "-" + str(now.month) + "-" + str(now.day) + " " + str(now.hour) + ":00"
            now = datetime.strptime(str_val, "%Y-%m-%d %H:%M")
        return now

    @staticmethod
    def week_range(date):
        """Find the first/last day of the week for the given day.
        Assuming weeks start on Sunday and end on Saturday.

        Returns a tuple of ``(start_date, end_date)``.

        """
        # isocalendar calculates the year, week of the year, and day of the week.
        # dow is Mon = 1, Sat = 6, Sun = 7
        year, week, dow = date.isocalendar()

        # Find the first day of the week.
        if dow == 7:
            # Since we want to start with Sunday, let's test for that condition.
            start_date = date
        else:
            # Otherwise, subtract `dow` number days to get the first day
            start_date = date - timedelta(dow)

        # Now, add 6 for the last day of the week (i.e., count up to Saturday)
        end_date = start_date + timedelta(6)

        return (start_date, end_date)

    @staticmethod
    def month_range(date):
        start_date = datetime(date.year, date.month, 1)
        if date.month < 12:
            end_date = datetime(date.year, date.month+1, 1)
        else :
            end_date = datetime(date.year+1, 1, 1)

        return (start_date, end_date)

    @staticmethod
    def year_range(date):
        start_date = datetime(date.year, 1, 1)
        end_date = datetime(date.year + 1, 1, 1)
        return (start_date, end_date)




