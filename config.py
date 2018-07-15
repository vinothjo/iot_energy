#!/usr/bin/python3
# ****************************************************
#  Project : iPharm Analytics
#  Filename: app.py
#  Created : varun Selva
#  Change history:
#  dd.mm.yyyy / developer name
#  17.01.2018 / varun selva
# ***************************************************
#   creating app file
# ****************************************************
from datetime import datetime

from werkzeug.contrib.cache import SimpleCache
from pymongo import MongoClient
import logging
from flask import Flask

global APP_NAME
APP_NAME = "Energy IOT Suite"
cache = SimpleCache()



SECREAT_KEY = "key_pinnacle"
SECURITY_TOKEN_MAX_AGE = 60 * 15

HOST = '0.0.0.0'
PORT = 5000

LOG_PATH = 'logs'
# INFO | ERROR | DEBUG
LEVEL = logging.INFO
print('cur_time:', datetime.now())
EXPORT_FOLDER = "/IOT/EXPORT_FOLDER/"
database_names = 'iot_app_user'
#client_read_write  = MongoClient("13.250.37.187", 27017, username='iot_prod', password='Mko09ijnbhu8', authSource=DB_Name)
#client_readonly  = MongoClient("13.250.107.208", 27017, username='iot_prod', password='Mko09ijnbhu8', authSource=DB_Name)
client_read_write  = MongoClient("localhost", 27017, authSource=database_names)
client_readonly  = MongoClient("localhost", 27017, authSource=database_names)



energy_iot_DB_RW = client_read_write[database_names]
energy_iot_DB_READ = client_readonly[database_names]

USER_ROLES = ["TESTER", "DEV","ADMIN", "SUPER_ADMIN"]
#UPLOAD_FOLDER = 'E:\images'
UPLOAD_FOLDER = '/home/oscorp/Desktop/iot_energy/images'
TEMP_FOLDER = '/home/oscorp/Desktop/iot_energy/TEMP'



LOG_PATH = '/logs'
# INFO | ERROR | DEBUG
LEVEL = logging.INFO

app = Flask(__name__)


