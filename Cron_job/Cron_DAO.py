# ****************************************************
#  Filename: Iot_DAO.py
#  Created by:
#  Change history:
#  dd.mm.yyyy / developer name
#  15.01.2018 / SV
# ***************************************************
#   For Iot_DAO
# ****************************************************
import pandas as pd

import config
from Util import TABLE,Util
from Util.DateUtil import DateUtil
from config import app


class Cron_DAO():
    # Get iot_Main_table_detail Info
    def getAll_iot_Main_table_detail(self, sensor_type, from_time, to_time,device_type=Util.Util.Solar, processed_status=None,table_name=TABLE.IOT_MAIN_TABLE,mandatory_col=None):
        result = []
        _condition = {}
        if (processed_status) and processed_status.strip() != "":
            _condition.__setitem__("processed_status", processed_status)

        if (device_type) and device_type.strip() != "":
            _condition.__setitem__("device_type", device_type)

        if (sensor_type) and sensor_type.strip() != "":
            _condition.__setitem__("sensor_type", sensor_type)

        if (from_time) and (to_time):
            _condition.__setitem__("sender_timestamp", {"$gt": from_time,"$lte": to_time})

        if (mandatory_col):
            _condition.__setitem__(mandatory_col,{"$exists": 'true'})

        print(_condition)
        data = config.energy_iot_DB_RW[table_name].find(_condition)

        df = pd.DataFrame(list(data))
        return df


    def insert_one_record(self, row,table_name):
        config.energy_iot_DB_RW[table_name].insert_one(row)

    def insert_many_record(self, data,table_name):
        for row in data:
            config.energy_iot_DB_RW[table_name].insert_one(row)

    def update_record(self, set_json,table_name,_condition,multi=False):
        app.logger.info("updating user ingo")
        _update = {'$set': set_json}
        config.energy_iot_DB_RW[table_name].update(_condition, _update, multi=multi)
        return "Done"

    def upsert(self,  set_json,table_name,_condition):
        _update = {'$set': set_json}
        config.energy_iot_DB_RW[table_name].update(_condition, _update, upsert=True)
        return "Done"

    def get_batch_job_time(self,job_name):
        data = config.energy_iot_DB_RW[TABLE.IOT_CRON_JOB_TABLE].find_one({'job_name':job_name})
        if data is not None:
            start_date = data['last_run']
        else:
            start_date = DateUtil.get_current_day(add_hr=-48)
        return start_date


    def getAssert_master(self):
        data = config.energy_iot_DB_RW[TABLE.IOT_ASSET_MSTR].find()
        assert_data = {}
        for row in data:
            assert_data.__setitem__(row['sensor_id'],row['asset_capacity'])

        return assert_data

    def getLocation_IRR(self):
        data = config.energy_iot_DB_RW[TABLE.IOT_LOCATION].find()
        irr_data = {}
        for row in data:
            irr_data.__setitem__(row['resource_path'],row['irr'])
        return irr_data



