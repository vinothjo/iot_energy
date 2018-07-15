# ****************************************************
#  Filename: Iot_DAO.py
#  Created by:
#  Change history:
#  dd.mm.yyyy / developer name
#  15.01.2018 / Nagarajan A
# ***************************************************
#   For Iot_DAO
# ****************************************************
#import cassandra
from pymongo import MongoClient
import pytz
import time
from datetime import datetime
import pandas as pd
from datetime import datetime, timedelta
import sys
import numpy as np
import json
import plotly
from Util import TABLE,Util
from config import app
import config

class Iot_DAO():



    @staticmethod
    def isNone(obj,key,default=None):
        if key in obj:
            return obj[key]
        else:
            return default

    @staticmethod
    def toStr(obj, key, default=""):
        if key in obj:
            return str(obj[key])
        else:
            return str(default)


    def getrecord_from_table(self,_table, _condition,_projection,_sortby=None):
        try:
            app.logger.info("getrecord_from_table >> ")
            if _sortby:
                data = config.energy_iot_DB_READ[_table].find(_condition, _projection).sort(_sortby)
            else:
                data = config.energy_iot_DB_READ[_table].find(_condition, _projection)
            df = pd.DataFrame(list(data))
            return df

        except Exception as err:
            app.logger.error("getrecord_from_table >> error   " + str(err))
            return None

    def getJSON_LISTrecord_from_table(self,_table, _condition,_projection,_sortby=None):
        try:
            app.logger.info("getrecord_from_table >> ")
            if _sortby:
                data = config.energy_iot_DB_READ[_table].find(_condition, _projection).sort(_sortby)
            else:
                data = config.energy_iot_DB_READ[_table].find(_condition, _projection)

            _data = []
            for row in data:
                del row['_id']
                _data.append(row)

            return _data

        except Exception as err:
            app.logger.error("getrecord_from_table >> error   " + str(err))
            return None


