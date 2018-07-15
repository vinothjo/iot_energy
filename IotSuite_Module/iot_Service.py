# ****************************************************
#  Project : Iot
#  Filename: Com_Service.py
#  Created : sv
#  Change history:
#  dd.mm.yyyy / developer name
#  14.01.2018 / sv\
#  18.01.2018 / Nagarajan A  Changed structure as per discussion on 170118:2100
#  19.01.2018 / Nagarajan A  Created services for blob,main,config,except
#  31.01.2018 / Nagarajan A  Created services for aggregate1,common,location and error changes
# ***************************************************
#   creating prescription  Controller
# ****************************************************

# Import flask dependencies
import json

from IotSuite_Module.Iot_DAO import Iot_DAO
from IotSuite_Module.Response_models.graph_data_graph import Graph_data_graph
from IotSuite_Module.Response_models.location import Location
from IotSuite_Module.Response_models.dashboard import Dashboard
from config import app
from error_code import APP_ERRORS
from pymongo import MongoClient
#from cassandra.cqlengine.functions import MinTimeUUID
from datetime import datetime, timedelta

iot_dao = Iot_DAO()

class Iot_Service():

    @staticmethod
    def chk_type(varFrom,varTo, var):
        print("---chking--type---")
        print(var.__class__.__name__)
        return var

    @staticmethod
    def chk_type_val(cfgMat,devType, key, var):

        if var is None:
            return None
        else:
            print(cfgMat.get(devType, {}).get(key))
            print(cfgMat.get(devType, {}).get(key).__getitem__(1), )
            print(cfgMat.get(devType, {}).get(key).__getitem__(2), )
            print(cfgMat.get(devType, {}).get(key).__getitem__(3), )
            print("---chking--type---")
            print(var.__class__.__name__)
            return var










    # get last hrs main records
    def getlastHrs_Main_Results(self, duration_limit,device_type,sensor_type):
        try:
            return APP_ERRORS.UNKNOWN, None

        except Exception as err:
            app.logger.error("getLastHrMainRecord>> error   " + str(err))
            return APP_ERRORS.UNKNOWN, None



    def getDashboard_info(self,start,end,location, area, zone):

        dash = Dashboard()
        dash.setEnergy_consumed_summary(last_hour_avg="12",last_month_avg="22",last_week_avg="11",current_value="21",
                                        current_value_uom="KW",avg_uom="KW/h")
        dash.setEnergy_generated_summary(last_hour_avg="12", last_month_avg="22", last_week_avg="11", current_value="21",
                                        current_value_uom="Kw", avg_uom="Kw/h")

        #'11-12-2018 1:30'
        gen_data = Graph_data_graph()
        gen_data.setData(time=["10:30","11:00","11:30","12:00"],expected=["10","11","11","12"],actual=["10","14","11","12"],uom="Kw/h")
        dash.energy_generated_graph_summary_data =gen_data
        con_data = Graph_data_graph()
        con_data.setData(time=["10:30", "11:00", "11:30", "12:00"], expected=["4", "5", "5", "5"],actual=["3", "4", "5", "2"], uom="Kw/h")
        dash.energy_consumed_graph_summary_data = con_data
        dash.location = Location(zone="North",area="SENGKANG",postal_code="542212",blk="212B",longitude="103.851959",latitude="1.290270",energyConsumed='8Kw/h',energygenrated="12Kw/h")
        return dash

