# ****************************************************
#  Project : Iot
#  Filename: Reg_Service.py
#  Created : sv
#  Change history:
#  dd.mm.yyyy / developer name
#  10.04.2017 / sv
# ***************************************************
#   creating Util  Services
# ****************************************************

# Import flask dependencies
from Util import TABLE
from config import app
from Util.Util import  Util
import config


class Util_Service():

    @staticmethod
    def get_Config_matrix():
        app.logger.info("get_Config_matrix")
        config_data = config.energy_iot_DB_RW[TABLE.CONFIG_TABLE].find()
        Config_matrix = {}
        for d in config_data:
            key = d["device_type"] + "#" + d["sensor_type"]
            if Config_matrix.get(key, None) is None:
                Config_matrix[key] = [Util().toJson(d)]
            else:
                Config_matrix[key].append(Util().toJson(d))
        #app.logger.info(Config_matrix)
        return Config_matrix

    @staticmethod
    def get_location_details(lodation_filter=None,user_role=None):
        try:
            app.logger.info("getLocationDetails >> ")
            _condition = {}
            if lodation_filter:
                _condition={'resource_path':{'$in':lodation_filter}}
            if user_role:
                location_det = config.energy_iot_DB_READ[TABLE.IOT_ROLE].find_one({'role_name':user_role})
                _condition = {'resource_path': {'$in': location_det.access_location}}

            data = config.energy_iot_DB_READ[TABLE.IOT_LOCATION].find(_condition)
            loc_data = {}
            for row in data:
                loc_data.__setitem__(row['resource_path'], row)
            return loc_data

        except Exception as err:
            app.logger.error("getLocationDetails>> error   " + str(err))
            return None
