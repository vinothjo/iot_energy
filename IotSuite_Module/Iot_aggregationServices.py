from datetime import timedelta
from random import randint
import math
#from cassandra.auth import PlainTextAuthProvider
#from cassandra.cluster import Cluster
from pandas.core.groupby import Grouper
from pymongo import MongoClient

from Util import TABLE,Util
from IotSuite_Module.Iot_DAO import Iot_DAO
from IotSuite_Module.Response_models.graph_data_graph import Graph_data_graph
from IotSuite_Module.Response_models.location import Location
from IotSuite_Module.Response_models.dashboard import Dashboard
import pandas as pd
import numpy as np
import time
import sys

from Util.DateUtil import DateUtil
from Util.Util_Service import Util_Service
from config import app
from error_code import APP_ERRORS
dao = Iot_DAO()
uti_service = Util_Service()
tree_save_const = 0.194
co2_save_const = 0.4244

class Iot_aggregationServices():

    def getDashboard_info(self, start, end, device_type="Solar", interval="900", location_list=None):

        dash = Dashboard()

        #current day
        print('current', start, end)
        dpm_value, tree_save, irr_value, co2, X_dpm, Y_dpm, Y_irr,Y_tree,Y_perform,Y_expected = self.getSummary_data(start, end, device_type="Solar", interval="900", location_list=location_list)

        # last Hour
        end_time = DateUtil.getlowest_min_date(min=60)
        start_time = end_time - timedelta(hours=1)
        print('last_hour', start_time, end_time)
        lh_dpm_value, lh_tree_save, lh_irr_value, lh_co2, lh_X_dpm, lh_Y_dpm, lh_Y_irr,lh_Y_tree,lh_Y_perform,lh_Y_expected = self.getSummary_data(start_time, end_time, device_type="Solar", interval="900", location_list=location_list)
        #print(lh_dpm_value, lh_tree_save, lh_irr_value, lh_co2)
        #print(Y_dpm)
        #print(Y_irr)
        dash.setE_Generation_summary(last_hour=lh_dpm_value,current=dpm_value)
        dash.setE_Generation_SummaryGraph(lh_X_dpm, lh_Y_dpm, x_uom="", y_uom="Wh")
        dash.setE_Generation_Graph(X_dpm,Y_dpm, x_uom="", y_uom="Wh")
        dash.setIrr_summary(last_hour=lh_irr_value,current=irr_value,uom='W/m2')
        dash.setIrr_SummaryGraph(lh_X_dpm, lh_Y_irr, x_uom="", y_uom="W/m2")
        dash.setIrr_Graph(X_dpm,Y_irr, x_uom="", y_uom="W/m2")
        dash.setTree_save_summary(last_hour=lh_tree_save, current=tree_save, co2=co2)
        dash.setTree_save_SummaryGraph(lh_X_dpm,lh_Y_tree)
        dash.setExpected_Graph(X_dpm,Y_expected,y_uom="kWh")
        dash.setPR_Graph(X_dpm,Y_perform,y_uom='%')

        #print(X_dpm)
        return dash




    def getSummary_data(self, start, end, device_type="Solar", interval="900", location_list=None):

        _condition = {"sender_timestamp" : {"$gte": start,"$lte": end}}
        if location_list:
            _condition.__setitem__('resource_path',{"$in":location_list})
        print(_condition)
        _projection = {"sender_timestamp":1,"resource_path" : 1.0,"device_type" :1,"sensor_type":1,"AGGREGATE_VALUE":1,"irr_value":1,"performance_ratio":1,"expected_value":1}
        _sortby = [['sender_timestamp', 1], ['device_type', -1]]
        data_set = dao.getrecord_from_table(TABLE.IOT_AGG_15_MINUTES_SUMMARY_TABLE,_condition=_condition,_projection=_projection,_sortby=_sortby)
        if data_set.empty:
            print('No Record found!!')
            return 0, 0, 0,0, [], [], [],[], [], []
        else:
            data_set['AGGREGATE_VALUE'] = data_set['AGGREGATE_VALUE'].replace([np.NaN, ''], 0).astype(np.float64).fillna(0.0)
            data_set['irr_value'] = data_set['irr_value'].replace([np.NaN, ''], 0).astype(np.float64).fillna(0.0)
            data_set['performance_ratio'] = data_set['performance_ratio'].replace([np.NaN, ''], 0).astype(np.float64).fillna(0.0)
            data_set['expected_value'] = data_set['expected_value'].replace([np.NaN, ''], 0).astype(np.float64).fillna(0.0)
            data_set['AGGREGATE_VALUE'] = pd.to_numeric(data_set['AGGREGATE_VALUE'], errors='coerse')
            data_set['irr_value'] = pd.to_numeric(data_set['irr_value'], errors='coerse')
            data_set['performance_ratio'] = pd.to_numeric(data_set['performance_ratio'], errors='coerse')
            data_set['expected_value'] = pd.to_numeric(data_set['expected_value'], errors='coerse')

            agg = {'irr_value':'mean','AGGREGATE_VALUE':'sum','performance_ratio': 'mean','expected_value': 'mean'}
            summary = data_set.groupby([ 'sensor_type']).agg(agg).reset_index()

            graph_summary = data_set.groupby(['sensor_type',"sender_timestamp"]).agg(agg).reset_index()

            graph_summary_DPM = graph_summary[graph_summary['sensor_type'].notnull() & (graph_summary['sensor_type'] == Util.Util.DPM)]
            graph_summary_DPM = graph_summary_DPM.sort_values(['sender_timestamp'], ascending=[True])
            #print(graph_summary_DPM)
            X_dpm = []
            Y_dpm = []
            Y_irr = []
            Y_tree = []
            Y_perform = []
            Y_expected = []
            for index, row in graph_summary_DPM.iterrows():
                #print('row ',row)

                X_dpm.append(row['sender_timestamp'].strftime('%H:%M %d%b%Y'))
                Y_dpm.append(row['AGGREGATE_VALUE'])
                Y_irr.append(row['irr_value'])
                Y_tree.append(round(tree_save_const * row['AGGREGATE_VALUE'],2))
                if row['performance_ratio'] > 100:
                    Y_perform.append(100)
                else:
                    Y_perform.append(round(row['performance_ratio'],2))
                Y_expected.append(round(row['expected_value'], 2))

            dpm_value = 0
            irr_value = 0
            tree_save = 0
            co2 = 0

            for index, row in summary.iterrows():
                if row['sensor_type'] == 'DPM':
                    dpm_value = round(float(row['AGGREGATE_VALUE']), 2)
                    irr_value = round(float(row['irr_value']), 2)
                    tree_save = round(float(tree_save_const * dpm_value), 2)
                    co2 = round(float(co2_save_const * dpm_value), 2)

            print(dpm_value,irr_value,tree_save,co2)

        return dpm_value, tree_save, irr_value,co2, X_dpm, Y_dpm, Y_irr,Y_tree, Y_perform, Y_expected



    def get15MinSummaryData_for_map(self,startDateTime,endDateTime,sensor_type="DPM",location_list=None):
        try:
            app.logger.info("-----------------------------")
            app.logger.info(" get15MinSummaryData >>" + str(startDateTime))
            # result = []

            _condition = {"sender_timestamp": {"$gte": startDateTime, "$lte": endDateTime},'sensor_type':sensor_type}
            if location_list:
                _condition.__setitem__('resource_path', {"$in": location_list})
            print(_condition)
            _projection = {"sender_timestamp": 1, "resource_path": 1.0, "device_type": 1, "sensor_type": 1,
                           "AGGREGATE_VALUE": 1, "irr_value": 1, "performance_ratio": 1, "expected_value": 1}
            _sortby = [['sender_timestamp', 1], ['device_type', -1]]
            data_set = dao.getrecord_from_table(TABLE.IOT_AGG_15_MINUTES_SUMMARY_TABLE, _condition=_condition,
                                                _projection=_projection, _sortby=_sortby)
            if data_set.empty:
                return None, APP_ERRORS.NO_REC_FOUND
            else:
                data_set['AGGREGATE_VALUE'] = data_set['AGGREGATE_VALUE'].replace([np.NaN, ''], 0).astype(
                    np.float64).fillna(0.0)

                agg = {'AGGREGATE_VALUE': 'sum'}
                summary = data_set.groupby(['resource_path']).agg(agg).reset_index()

            #print(summary)
            LOCATION_TABLE = uti_service.get_location_details();


            result = []
            for index, row in summary.iterrows():
                loc = row['resource_path']
                res_json = {}
                try:
                    res_json.__setitem__('Location_detail',{"location_code":LOCATION_TABLE[loc]["location_code"],'longitude':str(LOCATION_TABLE[loc]["longitude"]),'latitude':str(LOCATION_TABLE[loc]["latitude"])})
                    res_json.__setitem__('AGGREGATE_VALUE',row['AGGREGATE_VALUE'])
                except Exception as err:
                    row['Location_detail'] = {}
                    app.logger.error("Map data preparation >> error   " + str(err))

                result.append(res_json)



            if (len(result) == 0):
                return APP_ERRORS.NO_REC_FOUND, result
            else:
                return APP_ERRORS.SUCCESS, result

        except Exception as err:
            app.logger.error("get15MinSummaryData_for_map>> error   " + str(err))
            return APP_ERRORS.UNKNOWN, None
