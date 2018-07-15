#!/usr/bin/env python3

import logging

log = logging.getLogger()
log.setLevel('DEBUG')
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
log.addHandler(handler)
import paho.mqtt.client as mqtt
import json
from pymongo import MongoClient
from datetime import datetime
import pytz

zone='Asia/Singapore'
class Mqtt_Sub():
    print('cur_timewwww :', datetime.now())
    client = MongoClient("13.250.37.187", 27017, username='iot_prod', password='Mko09ijnbhu8', authSource='energy_iot')
    db = client.energy_iot
    main_table = db.iot_main_table
    print('cur_timewwww :', datetime.now())



    def on_connect(self,client, userdata, flags, rc):
        if rc == 0:

            print("Connected to broker")
            print("Connected with result code " + str(rc))
            client.subscribe("solrpnl_01")

            global Connected  # Use global variable
            Connected = True  # Signal connection
        else:
            print("Connection failed")


    def on_message(self,client, userdata, msg):
        message = msg.payload.decode()
        try:
            data = json.loads(message)
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
            data["blob_created_on"] = self.getcurr_datetime(zone=zone)
            data["processed_status"] = 'N'
            print("insert Action Start")
            self.main_table.insert_one(data)
            print("insert Action End ")

        except Exception as err:
            print("Error " + str(err))
        #client.disconnect()


    def run(self):
        #self.main_table.insert_one({"test":123})
        client = mqtt.Client("", True, None, mqtt.MQTTv31)
        client.username_pw_set("iot_mqtt", password="Team2Work")
        client.connect("10.2.5.222", 1883, 60)
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.loop_forever()

    def getcurr_datetime_String(self,zone='Asia/Singapore',format="%Y-%m-%dT%H:%M:%SZ"):
        timezone = pytz.timezone(zone)
        dt = timezone.localize(datetime.now())
        return dt.strftime(format)

    def getcurr_datetime(self,zone='Asia/Singapore'):
        timezone = pytz.timezone(zone)
        dt = timezone.localize(datetime.now())
        format = "%Y-%m-%d %H:%M:%S"
        return datetime.strptime(dt.strftime(format),format)






if __name__ == '__main__':
    obj = Mqtt_Sub()
    obj.run()