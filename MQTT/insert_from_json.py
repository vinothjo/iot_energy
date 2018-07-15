import json
from datetime import date, datetime
from pymongo import MongoClient
import os




client = MongoClient()
#client = MongoClient('54.255.208.68', 27017)
client = MongoClient("13.250.37.187",27017,username='iot_prod',password='Mko09ijnbhu8',authSource='energy_iot')
db = client.energy_iot
main_table = db.iot_main_table

for file in os.listdir("D:\PycharmProjects\IOT_version_02\json\processed"):
    if file.endswith(".json"):
        file_name = os.path.join("D:\PycharmProjects\IOT_version_02\json\processed", file)
        print(file_name)

        try:
            json_data=open(file_name).read()
            data = json.loads(json_data)

            params =  data['Parameters']
            for (k, v) in params.items():
                print("Key: " + k)
                print("Value: " + str(v))
                data.__setitem__(k,v)

            del data['Parameters']

            data["sender_id"] = data["sdrid"]
            del data["sdrid"]
            data["sensor_id"] = data["scrid"]
            del data["scrid"]
            data["sensor_type"] = data["scrty"]
            del data["scrty"]
            data["resource_path"] = data["rp"]
            del data["rp"]
            data["device_id"] = data["eid"]
            del data["eid"]
            data["device_type"] = data["devty"]
            del data["devty"]
            data['sender_timestamp'] = datetime.strptime(data['dt'], "%Y%m%d%H%M%S")
            del data["dt"]
            data["blob_created_by"] = "MQTT_CLIENT"
            data["blob_created_on"] = datetime.now()
            print("insert Action Start")
            print(data)
            #main_table.insert_one(data)
            bk_file_name = os.path.join("D:\PycharmProjects\IOT_version_02\json_bk", file)
            #os.rename(file_name, bk_file_name)
            print("insert Action End ")

        except Exception as err:
            print("Error " + str(err))
            continue