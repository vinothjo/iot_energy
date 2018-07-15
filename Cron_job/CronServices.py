import json

from Cron_job.Cron_DAO import Cron_DAO
from Util.DateUtil import DateUtil
from Util.Util_Service import Util_Service
from config import app
import pandas as pd
from pandas.core.groupby import Grouper
from datetime import datetime, timedelta
from Util import TABLE,Util
import numpy as np
dao = Cron_DAO()
util_service = Util_Service()
class CronServices():



    def insert_aggregation_15_min_Max(self, duration_limit, interval,device_type,sensor_type):
        app.logger.info("****get_aggregation_tableFrom_main***")


        total_inserted_rows = 0

        CONFIG_TABLE = util_service.get_Config_matrix()
        #print(CONFIG_TABLE)

        #frm = DateUtil().getcurr_datetime(add_hr=-duration_limit)
        to = DateUtil().getlowest_min_date(min=15)
        frm = to - timedelta(hours=int(duration_limit))
        app.logger.info('insert_aggregation_15_min_Max :: ' + str(frm) + " <  t >= " + str(to))
        df = dao.getAll_iot_Main_table_detail(sensor_type=None, from_time=frm, to_time=to,processed_status=None,table_name=TABLE.IOT_MAIN_TABLE)
        print('Total No of Records', df.shape)
        if df is None:
            app.logger.info("************************  No record available ************************  ")
            return 0
        for device_type in df['device_type'].unique():
            for sensor_type in df['sensor_type'].unique():
                agg_columns = CONFIG_TABLE[device_type + '#' + sensor_type]
                agg = {}
                for col in agg_columns:
                    if col['is_aggr'] == 'Y':
                        fun = col['aggr_funct']
                        col_name = col['column_ref']
                        #logger.info(col_name + " : " + fun)
                        df[col_name] = pd.to_numeric(df[col_name], errors='coerse')
                        #logger.info(col_name + "$" + fun)
                        if fun == "SUM":
                            df[col_name] = df[col_name].replace([np.NaN, ''], 0).astype(np.float64).fillna(0.0)
                            agg.__setitem__(col_name,'sum')
                        elif fun == "AVG":
                            df[col_name] = df[col_name].replace([np.NaN, ''], 0).astype(np.float64).fillna(0.0)
                            agg.__setitem__(col_name,'mean')
                        elif fun == "DIFF":
                            df[col_name] = df[col_name].replace([np.NaN, ''], 0).astype(np.float64).fillna(0.0)
                            agg.__setitem__(col_name,'max')
                app.logger.info(agg)

                data = df[df['sensor_type'].notnull() & (df['sensor_type'] == sensor_type) & df['device_type'].notnull() & (df['device_type'] == device_type)]

                data = data.groupby(['resource_path' ,'device_type','sender_id','device_id','sensor_type','sensor_id',
                                   Grouper(key='sender_timestamp', freq=interval+'s')]).agg(agg).reset_index()

                data = data.sort_values(['resource_path','sensor_type','sender_timestamp'], ascending=[True,True, True])

                # to change the group by tome to lower limit
                # e.g if 12:15 - 12:30 => group by function return 12:15. But that should be 12:30 value
                data['sender_timestamp'] = data['sender_timestamp'] + timedelta(seconds=int(interval))

                print(sensor_type,data.shape)
                batch_no =  DateUtil().getcurr_datetime_String(format='%Y%m%d%H%M%S')
                app.logger.info("-------------------------------------------------------------------------------------------")
                app.logger.info("************************  Insert record into Aggregation table  ************************  ")
                app.logger.info("device_type " + device_type)
                app.logger.info("sensor_type " + sensor_type)
                app.logger.info("No of Rows " + str(len(data.index)))
                app.logger.info("-------------------------------------------------------------------------------------------")

                for index, row in data.iterrows():
                    #print(1)
                    row['batch_no'] = batch_no
                    json_res = {}
                    json_res['Created_on'] = DateUtil.getcurr_datetime()
                    for i in row.keys():
                        try:
                            json_res.__setitem__(i, row[i])
                        except Exception as err:
                            print(row)
                    try:
                        #dao.insert_one_record(row=json_res,table_name=TABLE.IOT_AGG_MAX_TABLE)
                        _json = json_res
                        _cond = {"device_type": json_res.__getitem__('device_type'),
                                 "sender_timestamp": json_res.__getitem__('sender_timestamp'),
                                 "sender_id": json_res.__getitem__('sender_id'),
                                 "sensor_type": json_res.__getitem__('sensor_type'),
                                 "device_id": json_res.__getitem__('device_id'),
                                 "resource_path": json_res.__getitem__('resource_path')}
                        dao.upsert(table_name=TABLE.IOT_AGG_MAX_TABLE, set_json=_json, _condition=_cond)
                    except Exception as err:
                        error_rec = {"Error:": "Error in insert_aggregation_15_min_Max (insert )", "Error Desc": str(err), "batchjob_time": {'from': frm, 'to': to},'created_on': DateUtil.getcurr_datetime()}
                        dao.insert_one_record(row=error_rec,table_name=TABLE.IOT_CRON_EXCEPTION)
                    #print(3)
                total_inserted_rows += len(data.index)

                app.logger.info("-------------------------------------------------------------------------------------------")
                app.logger.info("************************  Update status into Main table  ************************  ")
                app.logger.info("-------------------------------------------------------------------------------------------")

                _json = {'last_run' : to}
                _cond = {"job_name" : 'insert_aggregation_15_min_Max'}
                dao.upsert(table_name=TABLE.IOT_CRON_JOB_TABLE,set_json=_json,_condition=_cond)

        '''
        app.logger.info("insert_aggregation_15_min_Max (Update processed_status)")
        for index, row1 in df.iterrows():
            try:
                set_json = {'processed_status': 'Y'}
                _condition = {'_id': row1['_id']}
                result_up = dao.update_record(set_json, TABLE.IOT_MAIN_TABLE, _condition, multi=False)
                #print("Update", _condition)
            except Exception as err:
                error_rec = {"Error:": "Error in insert_aggregation_15_min_Max (Update processed_status)", "Error Desc": str(err), "batchjob_time": {'from': frm, 'to': to},'created_on': DateUtil.getcurr_datetime()}
                dao.insert_one_record(row=error_rec,table_name=TABLE.IOT_CRON_EXCEPTION)

        '''




        app.logger.info("-------------------------------------------------------------------------------------------")
        app.logger.info("************************  Completed Aggregation table  15_max ************************  ")
        app.logger.info("total_inserted_rows: " + str(total_inserted_rows))
        app.logger.info("-------------------------------------------------------------------------------------------")
        #return data
        return total_inserted_rows



    def insert_aggregation_15_minutes_summary(self, duration_limit=5):
        app.logger.info("****insert_aggregation_15_minutes_summary***")

        total_inserted_rows = 0

        CONFIG_TABLE = util_service.get_Config_matrix()
        #print(CONFIG_TABLE)

        #frm = DateUtil.get_current_day(add_hr=-duration_limit)
        to = DateUtil.getlowest_min_date(min=30)
        frm = to - timedelta(hours=int(duration_limit))
        app.logger.info('insert_aggregation_15_minutes_summary :: ' + str(frm) + " <  t >= " +str(to))
        #frm = DateUtil().getcurr_datetime(add_hr=-10)
        #to = DateUtil().getcurr_datetime(add_hr=-1)
        #print(frm,to)
        df = dao.getAll_iot_Main_table_detail(sensor_type=None, from_time=frm, to_time=to,table_name=TABLE.IOT_AGG_MAX_TABLE)
        print('Total No of Records', df.shape)
        if df is None:
            app.logger.info("************************  No record available ************************  ")
            return 0

        res_data = []
        for device_type in df['device_type'].unique():
            for sensor_type in df['sensor_type'].unique():
                agg_columns = CONFIG_TABLE[device_type + '#' + sensor_type]
                agg = {}
                for col in agg_columns:
                    if col['is_aggr'] == 'Y':
                        fun = col['aggr_funct']
                        col_name = col['column_ref']
                        #logger.info(col_name + " : " + fun)
                        df[col_name] = pd.to_numeric(df[col_name], errors='coerse')
                        #logger.info(col_name + "$" + fun)
                        if fun == "SUM":
                            agg.__setitem__(col_name,'sum')
                            df[col_name] = df[col_name].replace([np.NaN, ''], 0).astype(np.float64).fillna(0.0)
                        elif fun == "AVG":
                            agg.__setitem__(col_name,'mean')
                            df[col_name] = df[col_name].replace([np.NaN, ''], 0).astype(np.float64).fillna(0.0)
                        elif fun == "DIFF":
                            agg.__setitem__(col_name,'max')
                            df[col_name] = df[col_name].replace([np.NaN, ''], 0).astype(np.float64).fillna(0.0)
                app.logger.info(agg)


                for resource_path in df['resource_path'].unique():
                    data = df[df['sensor_type'].notnull() & (df['sensor_type'] == sensor_type) &
                              df['device_type'].notnull() & (df['device_type'] == device_type) &
                              df['resource_path'].notnull() & (df['resource_path'] == resource_path)]

                    data = data.groupby(['resource_path' ,'device_type','sender_id','device_id',
                                       'sensor_type','sensor_id','sender_timestamp']).agg(agg).reset_index()
                    data = data.sort_values(['resource_path','sensor_type','sender_timestamp'], ascending=[True,True, True])
                    #logger.info("No of data " + str(len(data.index)))
                    dpm__previous_reading = 0
                    inv__previous_reading = {}
                    for sensor_id in data['resource_path'].unique():
                        inv__previous_reading.__setitem__(sensor_id,0)

                    for index, row in data.iterrows():
                        agg_value = '0'
                        if sensor_type == Util.Util.DPM:
                            if 'Act_Energy_Del' in row.keys():
                                dpm__current_reading = row['Act_Energy_Del']
                                #print('DPM__previous_reading', dpm__previous_reading)
                                #print('DPM__current_reading', dpm__current_reading)

                                if index > 0 :
                                    try:
                                        agg_value = round(float(dpm__current_reading - dpm__previous_reading), 2)
                                        # if Reset happend
                                        if dpm__current_reading <= 0:
                                            agg_value = 0;
                                    except Exception as err:
                                        app.logger.error(str(err))
                                        agg_value = 0
                                    #print('DPM_aggregated_value', agg_value)
                                dpm__previous_reading = dpm__current_reading

                        elif sensor_type == Util.Util.INV:
                            if 'E_DAY' in row.keys():
                                current_reading = row['E_DAY']
                                #print('INV_previous_reading', inv__previous_reading)
                                #print('INV_current_reading', current_reading)
                                if index > 0 :
                                    try:
                                        agg_value = round(float(current_reading- inv__previous_reading.get(row['sensor_id'])),2)

                                        # if Reset happend
                                        if agg_value < 0:
                                            agg_value = current_reading;
                                    except Exception as err:
                                        app.logger.error(str(err))
                                    #print('INV_aggregated_value', agg_value)
                                inv__previous_reading.__setitem__(row['sensor_id'],current_reading)
                        elif sensor_type == Util.Util.IRR:
                            if 'irr' in row.keys():
                                agg_value = row['irr']


                        if index > 0 :
                            row.__setitem__('AGGREGATE_VALUE', agg_value)
                            res_data.append(row)

        batch_no = DateUtil().getcurr_datetime_String(format='%Y%m%d%H%M%S')
        for row in res_data:
            # print(1)
            row['batch_no'] = batch_no
            json_res = {}
            json_res['Created_on'] = DateUtil.getcurr_datetime()
            for i in row.keys():
                try:
                    json_res.__setitem__(i, row[i])
                except Exception as err:
                    print(row)
            try:
                #print(json_res)
                total_inserted_rows +=1
                #dao.insert_one_record(row=json_res, table_name=TABLE.IOT_AGG_15_MINUTES_SUMMARY_TABLE)
                _json = json_res
                _cond = {"device_type": json_res.__getitem__('device_type'),"sender_timestamp": json_res.__getitem__('sender_timestamp'),
                         "sender_id": json_res.__getitem__('sender_id'),"sensor_type": json_res.__getitem__('sensor_type'),
                         "device_id": json_res.__getitem__('device_id'),"resource_path": json_res.__getitem__('resource_path')}
                dao.upsert(table_name=TABLE.IOT_AGG_15_MINUTES_SUMMARY_TABLE, set_json=_json, _condition=_cond)
            except Exception as err:
                error_rec = {"Error:": "Error in IOT_AGG_15_MINUTES_SUMMARY_TABLE (insert )", "Error Desc": str(err),
                             "batchjob_time": {'from': frm, 'to': to}, 'created_on': DateUtil.getcurr_datetime()}
                dao.insert_one_record(row=error_rec, table_name=TABLE.IOT_CRON_EXCEPTION)

        _json = {'last_run': to}
        _cond = {"job_name": 'insert_aggregation_15_minutes_summary'}
        dao.upsert(table_name=TABLE.IOT_CRON_JOB_TABLE, set_json=_json, _condition=_cond)
        app.logger.info("-------------------------------------------------------------------------------------------")
        app.logger.info("************************  Completed Aggregation table  15_max ************************  ")
        app.logger.info("total_inserted_rows: " + str(total_inserted_rows))
        app.logger.info("-------------------------------------------------------------------------------------------")
        #return data
        return total_inserted_rows

    def pr_calculation(self,duration_limit=5):
        assert_det = dao.getAssert_master()
        loc_irr_det = dao.getLocation_IRR()
        to = DateUtil.getlowest_min_date(min=30)
        frm = to - timedelta(hours=int(duration_limit))
        app.logger.info('pr_calculation :: ' + str(frm) + " <  t >= " + str(to))
        data_set = dao.getAll_iot_Main_table_detail(sensor_type=None,device_type=Util.Util.Solar,from_time=frm, to_time=to,table_name=TABLE.IOT_AGG_15_MINUTES_SUMMARY_TABLE)

        irr_data = data_set[data_set['sensor_type'].notnull() & (data_set['sensor_type'] == Util.Util.IRR)]
        if irr_data.empty:
            return 0
        else:
            irr_summary = {}
            for index, row in irr_data.iterrows():
                sensor_id= row['sensor_id']
                sender_timestamp = row['sender_timestamp'].strftime("%Y-%m-%d:%H:%M")
                irr_val = row['irr']
                irr_summary.__setitem__(sensor_id+"#"+sender_timestamp,irr_val)
            print(irr_summary)

            other_data = data_set[data_set['sensor_type'].notnull() & (data_set['sensor_type'] != Util.Util.IRR)]

            for index, row1 in other_data.iterrows():
                expected_value = 0;
                performance_ratio = 0
                irr_value = 0
                blk_sensor_capacity = 0
                try:
                    agg_value = row1['AGGREGATE_VALUE']
                    resource_path = row1['resource_path']
                    sender_timestamp = row1['sender_timestamp'].strftime("%Y-%m-%d:%H:%M")
                    irr_sensor = loc_irr_det[resource_path]
                    irr_value = irr_summary.get(irr_sensor + "#" + sender_timestamp)
                    if not irr_value:
                        irr_value=0
                    sensor_id = row1['sensor_id']
                    blk_sensor_capacity = assert_det[sensor_id]
                    #print(agg_value, resource_path, irr_sensor, sender_timestamp, irr_value, irr_capacity)

                    # 0.25 because of 15 minutes interval
                    # to convert to W  multiply by 1000
                    expected_value = round(float(irr_value * 0.001 * blk_sensor_capacity * 0.25),2)
                    # for percentage calculation multiply by 100
                    performance_ratio = round(float(((agg_value)/expected_value)* 100),2)
                except Exception as err:
                    expected_value = 0
                    performance_ratio = 0
                #print('expected_value ',expected_value,'performance_ratio ', performance_ratio)

                try:
                    set_json = {'expected_value': expected_value,'performance_ratio':performance_ratio,
                                'irr_value':irr_value,'sensor_capacity':blk_sensor_capacity,
                                'updated_on': DateUtil.getcurr_datetime()}
                    _condition = {'_id': row1['_id']}
                    result_up = dao.update_record(set_json, TABLE.IOT_AGG_15_MINUTES_SUMMARY_TABLE, _condition, multi=False)
                    #print("Update", result_up)
                except Exception as err:
                    error_rec = {"Error:": "Error in pr_calculation (Update performance_ratio)",
                                 "Error Desc": str(err), "batchjob_time": {'from': frm, 'to': to},
                                 'created_on': DateUtil.getcurr_datetime()}
                    dao.insert_one_record(row=error_rec, table_name=TABLE.IOT_CRON_EXCEPTION)


            #dpm_data = data_set[data_set['sensor_type'].notnull() & (data_set['sensor_type'] == Util.Util.DPM)]


        return "Done"


    def insert_1hour_summary(self,duration_limit=5):
        total_inserted_rows = 0
        assert_det = dao.getAssert_master()
        loc_irr_det = dao.getLocation_IRR()
        to = DateUtil.getlowest_min_date(min=30)
        frm = to - timedelta(hours=int(duration_limit))
        app.logger.info('pr_calculation :: ' + str(frm) + " <  t >= " + str(to))
        data_set = dao.getAll_iot_Main_table_detail(sensor_type=None,device_type=Util.Util.Solar,from_time=frm, to_time=to,table_name=TABLE.IOT_AGG_15_MINUTES_SUMMARY_TABLE,mandatory_col='irr_value')

        CONFIG_TABLE = util_service.get_Config_matrix()
        print(CONFIG_TABLE)
        if data_set is None:
            app.logger.info("************************  No record available ************************  ")
            return 0
        for device_type in data_set['device_type'].unique():
            for sensor_type in data_set['sensor_type'].unique():
                agg_columns = CONFIG_TABLE[device_type + '#' + sensor_type]
                agg = {}
                for col in agg_columns:
                    if col['is_aggr'] == 'Y':
                        fun = col['aggr_funct']
                        col_name = col['column_ref']
                        print(sensor_type,col_name, fun)
                        data_set[col_name] = pd.to_numeric(data_set[col_name], errors='coerse')
                        #logger.info(col_name + "$" + fun)
                        if fun == "SUM":
                            data_set[col_name] = data_set[col_name].replace([np.NaN, ''], 0).astype(np.float64).fillna(0.0)
                            agg.__setitem__(col_name,'sum')
                        elif fun == "AVG":
                            data_set[col_name] = data_set[col_name].replace([np.NaN, ''], 0).astype(np.float64).fillna(0.0)
                            agg.__setitem__(col_name,'mean')
                        elif fun == "DIFF":
                            data_set[col_name] = data_set[col_name].replace([np.NaN, ''], 0).astype(np.float64).fillna(0.0)
                            agg.__setitem__(col_name,'max')

                agg.__setitem__('sensor_capacity', 'mean')
                data_set['sensor_capacity'] = data_set['sensor_capacity'].replace([np.NaN, ''], 0).astype(np.float64).fillna(0.0)
                agg.__setitem__('irr_value', 'mean')
                data_set['irr_value'] = data_set['irr_value'].replace([np.NaN, ''], 0).astype(np.float64).fillna(0.0)
                agg.__setitem__('AGGREGATE_VALUE', 'sum')
                data_set['AGGREGATE_VALUE'] = data_set['AGGREGATE_VALUE'].replace([np.NaN, ''], 0).astype(np.float64).fillna(0.0)
                app.logger.info(agg)
                print(agg)

                data = data_set[data_set['sensor_type'].notnull() & (data_set['sensor_type'] == sensor_type) & data_set['device_type'].notnull() & (data_set['device_type'] == device_type)]

                data = data.groupby(['resource_path' ,'device_type','sender_id','device_id','sensor_type','sensor_id',
                                   Grouper(key='sender_timestamp', freq='1h')]).agg(agg).reset_index()

                data = data.sort_values(['resource_path','sensor_type','sender_timestamp'], ascending=[True,True, True])

                # to change the group by tome to lower limit
                # e.g if 12:15 - 12:30 => group by function return 12:15. But that should be 12:30 value
                data['sender_timestamp'] = data['sender_timestamp'] + timedelta(hours=1)

                print(sensor_type, data.shape)
                batch_no = DateUtil().getcurr_datetime_String(format='%Y%m%d%H%M%S')
                app.logger.info(
                    "-------------------------------------------------------------------------------------------")
                app.logger.info(
                    "************************  Insert record into Aggregation table  ************************  ")
                app.logger.info("device_type " + device_type)
                app.logger.info("sensor_type " + sensor_type)
                app.logger.info("No of Rows " + str(len(data.index)))
                app.logger.info(
                    "-------------------------------------------------------------------------------------------")

                for index, row in data.iterrows():
                    # print(1)
                    row['batch_no'] = batch_no
                    json_res = {}
                    json_res['Created_on'] = DateUtil.getcurr_datetime()
                    for i in row.keys():
                        try:
                            json_res.__setitem__(i, row[i])
                        except Exception as err:
                            print(row)
                    if sensor_type != Util.Util.IRR:
                        expected_value = 0
                        performance_ratio = 0
                        try:
                            irr_value = row['irr_value']
                            blk_sensor_capacity = row['sensor_capacity']
                            agg_value = row['AGGREGATE_VALUE']
                            # 0.25 because of 15 minutes interval
                            # to convert to W  multiply by 1000
                            expected_value = round(float(irr_value * 0.001 * blk_sensor_capacity ), 2)
                            # for percentage calculation multiply by 100
                            performance_ratio = round(float(((agg_value) / expected_value) * 100), 2)
                        except Exception as err:
                            app.logger.error(str(err))
                        json_res.__setitem__('expected_value', expected_value)
                        json_res.__setitem__('performance_ratio', performance_ratio)

                    try:
                        # dao.insert_one_record(row=json_res,table_name=TABLE.IOT_AGG_MAX_TABLE)
                        _json = json_res
                        _cond = {"device_type": json_res.__getitem__('device_type'),
                                 "sender_timestamp": json_res.__getitem__('sender_timestamp'),
                                 "sender_id": json_res.__getitem__('sender_id'),
                                 "sensor_type": json_res.__getitem__('sensor_type'),
                                 "device_id": json_res.__getitem__('device_id'),
                                 "resource_path": json_res.__getitem__('resource_path')}
                        dao.upsert(table_name=TABLE.IOT_AGG_1_HOUR_SUMMARY_TABLE, set_json=_json, _condition=_cond)
                    except Exception as err:
                        error_rec = {"Error:": "Error in IOT_AGG_1_HOUR_SUMMARY_TABLE (insert )",
                                     "Error Desc": str(err), "batchjob_time": {'from': frm, 'to': to},
                                     'created_on': DateUtil.getcurr_datetime()}
                        dao.insert_one_record(row=error_rec, table_name=TABLE.IOT_CRON_EXCEPTION)
                    # print(3)
                total_inserted_rows += len(data.index)

                app.logger.info(
                    "-------------------------------------------------------------------------------------------")
                app.logger.info("************************  Update status into Main table  ************************  ")
                app.logger.info(
                    "-------------------------------------------------------------------------------------------")

                _json = {'last_run': to}
                _cond = {"job_name": 'insert_1hour_summary'}
                dao.upsert(table_name=TABLE.IOT_CRON_JOB_TABLE, set_json=_json, _condition=_cond)

        return "Done"


    def insert_1day_summary(self,duration_limit=5):
        total_inserted_rows = 0
        assert_det = dao.getAssert_master()
        loc_irr_det = dao.getLocation_IRR()
        to = DateUtil.get_current_day()
        frm  = DateUtil.get_current_day() - timedelta(days=int(duration_limit))
        app.logger.info('pr_calculation :: ' + str(frm) + " <  t >= " + str(to))
        data_set = dao.getAll_iot_Main_table_detail(sensor_type=None,device_type=Util.Util.Solar,from_time=frm, to_time=to,table_name=TABLE.IOT_AGG_1_HOUR_SUMMARY_TABLE,mandatory_col='irr_value')

        CONFIG_TABLE = util_service.get_Config_matrix()
        print(CONFIG_TABLE)
        if data_set is None:
            app.logger.info("************************  No record available ************************  ")
            return 0
        for device_type in data_set['device_type'].unique():
            for sensor_type in data_set['sensor_type'].unique():
                agg_columns = CONFIG_TABLE[device_type + '#' + sensor_type]
                agg = {}
                for col in agg_columns:
                    if col['is_aggr'] == 'Y':
                        fun = col['aggr_funct']
                        col_name = col['column_ref']
                        print(sensor_type,col_name, fun)
                        data_set[col_name] = pd.to_numeric(data_set[col_name], errors='coerse')
                        #logger.info(col_name + "$" + fun)
                        if fun == "SUM":
                            data_set[col_name] = data_set[col_name].replace([np.NaN, ''], 0).astype(np.float64).fillna(0.0)
                            agg.__setitem__(col_name,'sum')
                        elif fun == "AVG":
                            data_set[col_name] = data_set[col_name].replace([np.NaN, ''], 0).astype(np.float64).fillna(0.0)
                            agg.__setitem__(col_name,'mean')
                        elif fun == "DIFF":
                            data_set[col_name] = data_set[col_name].replace([np.NaN, ''], 0).astype(np.float64).fillna(0.0)
                            agg.__setitem__(col_name,'max')

                agg.__setitem__('sensor_capacity', 'mean')
                data_set['sensor_capacity'] = data_set['sensor_capacity'].replace([np.NaN, ''], 0).astype(np.float64).fillna(0.0)
                agg.__setitem__('irr_value', 'sum')
                data_set['irr_value'] = data_set['irr_value'].replace([np.NaN, ''], 0).astype(np.float64).fillna(0.0)
                agg.__setitem__('AGGREGATE_VALUE', 'sum')
                data_set['AGGREGATE_VALUE'] = data_set['AGGREGATE_VALUE'].replace([np.NaN, ''], 0).astype(np.float64).fillna(0.0)
                app.logger.info(agg)
                print(agg)

                data = data_set[data_set['sensor_type'].notnull() & (data_set['sensor_type'] == sensor_type) & data_set['device_type'].notnull() & (data_set['device_type'] == device_type)]

                data = data.groupby(['resource_path' ,'device_type','sender_id','device_id','sensor_type','sensor_id',
                                   Grouper(key='sender_timestamp', freq='1D')]).agg(agg).reset_index()

                data = data.sort_values(['resource_path','sensor_type','sender_timestamp'], ascending=[True,True, True])

                # to change the group by tome to lower limit
                # e.g if 12:15 - 12:30 => group by function return 12:15. But that should be 12:30 value
                #data['sender_timestamp'] = data['sender_timestamp'] + timedelta(hours=24)

                print(sensor_type, data.shape)
                batch_no = DateUtil().getcurr_datetime_String(format='%Y%m%d%H%M%S')
                app.logger.info(
                    "-------------------------------------------------------------------------------------------")
                app.logger.info(
                    "************************  Insert record into Aggregation table  ************************  ")
                app.logger.info("device_type " + device_type)
                app.logger.info("sensor_type " + sensor_type)
                app.logger.info("No of Rows " + str(len(data.index)))
                app.logger.info(
                    "-------------------------------------------------------------------------------------------")

                for index, row in data.iterrows():
                    # print(1)
                    row['batch_no'] = batch_no
                    json_res = {}
                    json_res['Created_on'] = DateUtil.getcurr_datetime()
                    for i in row.keys():
                        try:
                            json_res.__setitem__(i, row[i])
                        except Exception as err:
                            print(row)
                    if sensor_type != Util.Util.IRR:
                        expected_value = 0
                        performance_ratio = 0
                        try:
                            irr_value = row['irr_value']
                            blk_sensor_capacity = row['sensor_capacity']
                            agg_value = row['AGGREGATE_VALUE']
                            # 0.25 because of 15 minutes interval
                            # to convert to W  multiply by 1000
                            expected_value = round(float(irr_value * 0.001 * blk_sensor_capacity ), 2)
                            # for percentage calculation multiply by 100
                            performance_ratio = round(float(((agg_value) / expected_value) * 100), 2)
                        except Exception as err:
                            app.logger.error(str(err))
                        json_res.__setitem__('expected_value', expected_value)
                        json_res.__setitem__('performance_ratio', performance_ratio)

                    try:
                        # dao.insert_one_record(row=json_res,table_name=TABLE.IOT_AGG_MAX_TABLE)
                        _json = json_res
                        _cond = {"device_type": json_res.__getitem__('device_type'),
                                 "sender_timestamp": json_res.__getitem__('sender_timestamp'),
                                 "sender_id": json_res.__getitem__('sender_id'),
                                 "sensor_type": json_res.__getitem__('sensor_type'),
                                 "device_id": json_res.__getitem__('device_id'),
                                 "resource_path": json_res.__getitem__('resource_path')}
                        print(json_res)
                        dao.upsert(table_name=TABLE.IOT_AGG_1_DAY_SUMMARY_TABLE, set_json=_json, _condition=_cond)
                    except Exception as err:
                        error_rec = {"Error:": "Error in IOT_AGG_1_HOUR_SUMMARY_TABLE (insert )",
                                     "Error Desc": str(err), "batchjob_time": {'from': frm, 'to': to},
                                     'created_on': DateUtil.getcurr_datetime()}
                        dao.insert_one_record(row=error_rec, table_name=TABLE.IOT_CRON_EXCEPTION)
                    # print(3)
                total_inserted_rows += len(data.index)

                app.logger.info(
                    "-------------------------------------------------------------------------------------------")
                app.logger.info("************************  Update status into Main table  ************************  ")
                app.logger.info(
                    "-------------------------------------------------------------------------------------------")

                _json = {'last_run': to}
                _cond = {"job_name": 'insert_1day_summary'}
                dao.upsert(table_name=TABLE.IOT_CRON_JOB_TABLE, set_json=_json, _condition=_cond)

        return "Done"


