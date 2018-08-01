#!/usr/bin/python3
# ****************************************************
#  Project : IoT
#  Filename: controllers.py
#  Created : sv
#  Update : Vinoth
#  Change history:
#  dd.mm.yyyy / developer name
#  14.01.2018 / sv
#  26.06.2018  /vinoth
# ***************************************************
#   creating registration  Controller
# ****************************************************
 # <script async defer src="https://maps.googleapis.com/maps/api/js?key=AIzaSyBLTcvxoWpOs4cP4CbSJAkz_cuVdaNvlWs&callback=initMap"
 # type="text/javascript"></script>
# Import flask dependencies
#import json as simplejson

from flask import Blueprint, request,Response, jsonify as jsfy
import requests
import os
import json
import jsonify
from flask import request, render_template
from flask import Flask, session, render_template, redirect, url_for
import uuid

#~ from gridfs import GridFS
#~ from flask import Flask, make_response


UPLOAD_FOLDER = os.path.basename('uploads')
UPLOAD_FOLDER = '/home/oscorp/Desktop/iot_energy/Source/images/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])




from pymongo import MongoClient
from flask_wtf import Form as FlaskForm
from flask_wtf import FlaskForm
from wtforms import TextField, BooleanField, PasswordField, TextAreaField, validators
import mongo
import Admin_Module.Model.User
import Admin_Module.Model.Client
from Admin_Module.admin_Service import Admin_Service
from Util import TABLE,Util
from Util.Util_Service import Util_Service
#~ import Admin_Module.DataTables
import config
from config import app, APP_NAME
from error_code import APP_ERRORS
# Define the blueprint: 'registration', set its url prefix: app.url/com
Admin = Blueprint('Admin', __name__, url_prefix='/admin')
from functools import wraps
Admin_service = Admin_Service()
uti_service = Util_Service()
import pprint
from werkzeug.utils import secure_filename


from bson.objectid import ObjectId

from mongo_datatables import DataTables



from werkzeug.routing import BaseConverter, ValidationError
from bson.errors import InvalidId
from base64 import urlsafe_b64encode, urlsafe_b64decode

from geopy.geocoders import Nominatim
from urllib.request import Request


class ObjectIDConverter(BaseConverter):
    def to_python(self, value):
        try:
            Value = urlsafe_b64decode(value.encode('utf-8'))
            if not type(Value) is str:
                Value = str(Value.decode('utf-8'))
            return ObjectId(Value)
        except (InvalidId, ValueError, TypeError):
            raise ValidationError()
    def to_url(self, value):
        Value = urlsafe_b64encode(value.encode('utf-8'))
        if not type(Value) is str:
            Value = str(Value.decode('utf-8'))
        return Value

def objectid(value):
    try:
        return ObjectId(str(value))
    except (InvalidId, ValueError, TypeError):
        return None


#~ app = Flask(__name__)
#~ mongo_client = MongoClient('mongodb://localhost:5000/')
#~ db = mongo_client['iot_app_user']
#~ grid_fs = GridFS(db)

app.url_map.converters['ObjectID'] = ObjectIDConverter

# Set the route and accepted methods
@Admin.route('/login', methods=['POST'])
def login():
    try:
        app.logger.info("Controller login >>   ")
        ip = request.remote_addr
        print("client_ip", str(ip))
        username = request.form['username']
        password = request.form["password"]
        isSuccess, resp = Admin_service.Validate_Auth(username, password, ip)
        print(isSuccess)
        print(resp)
        if isSuccess:
            session['USER'] = resp
            session['APP_NAME'] = APP_NAME
            return redirect('/iot/home')
        else:
            session.pop('USER', None)
            return render_template('login.html', APP_NAME=APP_NAME,error=APP_ERRORS.DESC[APP_ERRORS.AUTH_ERROR])
    except Exception as err:
        app.logger.error("login >> error  " + str(err))
        session.pop('TOKEN', None)
        return render_template('login.html', APP_NAME=APP_NAME,error=APP_ERRORS.DESC[APP_ERRORS.AUTH_ERROR])

@Admin.route('/create_user', methods=['GET'])
def create_user():
    user = User(username='admin123', surname='iot Admin', role='ADMIN',email='abc@gmail.vom', defunct='N', is_active='Y', updated_by='Vs')
    user.set_password('admin123')
    Admin_service.save_user(user)



def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            ip = request.remote_addr
            TOKEN = session['USER']
            print("requires_auth",TOKEN)
            #logger.info("requires_auth " + str(ip) + " " + str(user_id) + " " +  str(auth_token))
            #token_id = token_service.get_tokenid(ip, user_id)
            if not TOKEN :#or token_id != auth_token:
                #~ app.logger.error('fail authlongitude = api_response_dict['results'][0]['geometry']')
                app.logger.error('fail auth')
                return render_template('login.html', APP_NAME=APP_NAME, error=APP_ERRORS.DESC[APP_ERRORS.AUTH_ERROR])
                app.logger.info('success token auth')
            #token_service.extend_token(ip, user_id, token_id)
            return f(*args, **kwargs)
        except Exception as err:
            return render_template('login.html', APP_NAME=APP_NAME, error=APP_ERRORS.DESC[APP_ERRORS.AUTH_ERROR])


    return decorated


# Set the route and accepted methods
@Admin.route('/register_user', methods=['POST'])
def register_user():
    try:
        app.logger.info("Controller register_user >>   ")
        username = request.form['username']
        password = request.form["password"]
        surname = request.form["surname"]
        othername = request.form["othername"]
        role = request.form["role"]
        email = request.form["email"]
        contact_no = request.form["contact_no"]
        isSuccess, message = Admin_service.register_user(username=username,password=password,surname=surname,othername=othername,role=role,email=email,contact_no=contact_no)
        if isSuccess:
            return Response(simplejson.dumps({"ERROR": APP_ERRORS.NO_ERROR, "ERROR_DESC": APP_ERRORS.DESC[APP_ERRORS.NO_ERROR],
                                   "Response" : message}), mimetype='application/json')
        else:
            return Response(
                simplejson.dumps({"ERROR": APP_ERRORS.ERROR_PARAM, "ERROR_DESC": APP_ERRORS.DESC[APP_ERRORS.ERROR_PARAM],
                                  "Response": message}), mimetype='application/json')
    except Exception as err:
        app.logger.error("register_user >> error  " + str(err))
        return Response(simplejson.dumps(
            {"ERROR": APP_ERRORS.UNKNOWN, "ERROR_DESC": APP_ERRORS.DESC[APP_ERRORS.UNKNOWN]}), mimetype='application/json')




# Set the route and accepted methods
@Admin.route('/update_user', methods=['POST'])
def update_user():
    try:
        app.logger.info("Controller update_user >>   ")
        username = request.form['username']
        surname = request.form["surname"]
        othername = request.form["othername"]
        role = request.form["role"]
        email = request.form["email"]
        contact_no = request.form["contact_no"]
        remark = request.form["remark"]
        is_active = request.form["is_active"]
        defunct = request.form["defunct"]
        updated_by = request.form["updated_by"]
        isSuccess, message = Admin_service.update_user_info(username=username, surname=surname,
                                                         othername=othername, role=role, email=email,
                                                         contact_no=contact_no,remark=remark,is_active=is_active,
                                                            defunct=defunct,updated_by=updated_by)
        if isSuccess:
            return Response(simplejson.dumps({"ERROR": APP_ERRORS.NO_ERROR, "ERROR_DESC": APP_ERRORS.DESC[APP_ERRORS.NO_ERROR],
                                   "Response" : message}), mimetype='application/json')
        else:
            return Response(
                simplejson.dumps({"ERROR": APP_ERRORS.ERROR_PARAM, "ERROR_DESC": APP_ERRORS.DESC[APP_ERRORS.ERROR_PARAM],
                                  "Response": message}), mimetype='application/json')
    except Exception as err:
        app.logger.error("update_user >> error  " + str(err))
        return Response(simplejson.dumps(
            {"ERROR": APP_ERRORS.UNKNOWN, "ERROR_DESC": APP_ERRORS.DESC[APP_ERRORS.UNKNOWN]}), mimetype='application/json')



# Set the route and accepted methods
@Admin.route('/get_user', methods=['GET'])
def get_user():
    try:
        app.logger.info("Controller get_user >>   ")
        username = request.args.get('username')
        isSuccess, message = Admin_service.get_userinfo(username=username)
        if isSuccess:
            return Response(simplejson.dumps({"ERROR": APP_ERRORS.NO_ERROR, "ERROR_DESC": APP_ERRORS.DESC[APP_ERRORS.NO_ERROR],
                                   "Response" : message}), mimetype='application/json')
        else:
            return Response(
                simplejson.dumps({"ERROR": APP_ERRORS.ERROR_PARAM, "ERROR_DESC": APP_ERRORS.DESC[APP_ERRORS.ERROR_PARAM],
                                  "Response": message}), mimetype='application/json')
    except Exception as err:
        app.logger.error("update_user >> error  " + str(err))
        return Response(simplejson.dumps(
            {"ERROR": APP_ERRORS.UNKNOWN, "ERROR_DESC": APP_ERRORS.DESC[APP_ERRORS.UNKNOWN]}), mimetype='application/json')



# Set the route and accepted methods
@Admin.route('/user_change_password', methods=['POST'])
def user_change_password():
    try:
        app.logger.info("Controller update_user >>   ")
        username = request.form['username']
        cur_password = request.form["cur_password"]
        new_password = request.form["new_password"]
        isSuccess, message = Admin_service.Change_password(username=username,old_password=cur_password,new_password=new_password)
        if isSuccess:
            return Response(simplejson.dumps({"ERROR": APP_ERRORS.NO_ERROR, "ERROR_DESC": APP_ERRORS.DESC[APP_ERRORS.NO_ERROR],
                                   "Response" : message}), mimetype='application/json')
        else:
            return Response(
                simplejson.dumps({"ERROR": APP_ERRORS.ERROR_PARAM, "ERROR_DESC": APP_ERRORS.DESC[APP_ERRORS.ERROR_PARAM],
                                  "Response": message}), mimetype='application/json')
    except Exception as err:
        app.logger.error("update_user >> error  " + str(err))
        return Response(simplejson.dumps(
            {"ERROR": APP_ERRORS.UNKNOWN, "ERROR_DESC": APP_ERRORS.DESC[APP_ERRORS.UNKNOWN]}), mimetype='application/json')
            
            
            
####################################
#This controllers for Create Client#
#collection name is client#
#we declear the veriable db = config.database_names#
#######################################################

#Client Table
if config.energy_iot_DB_READ[TABLE.Client].find({'client_name': 'test'}).count() <= 0:
    print("client_id Not found, creating....")
    config.energy_iot_DB_READ[TABLE.Client].insert_one({'client_name':'test', 'value':0})

#Menu Table
if config.energy_iot_DB_READ[TABLE.Menu].find({'menu_name': 'menu'}).count() <= 0:
    print("menu_id Not found, creating....")
    config.energy_iot_DB_READ[TABLE.Menu].insert_one({'menu_name':'menu', 'value':0})
    
#Role Table
if config.energy_iot_DB_READ[TABLE.Role].find({'role_name': 'User'}).count() <= 0:
    print("role_id Not found, creating....")
    config.energy_iot_DB_READ[TABLE.Role].insert_one({'role_name':'User', 'value':0})
    
#Menu Table
if config.energy_iot_DB_READ[TABLE.Form].find({'form_name': 'form'}).count() <= 0:
    print("form_id Not found, creating....")
    config.energy_iot_DB_READ[TABLE.Form].insert_one({'form_name':'form', 'value':0})
    
#privileges Table
if config.energy_iot_DB_READ[TABLE.privileges].find({'privileges_name': 'privileges'}).count() <= 0:
    print("privileges_id Not found, creating....")
    config.energy_iot_DB_READ[TABLE.privileges].insert_one({'privileges_name':'privileges', 'value':0})
    
#Customer Table
if config.energy_iot_DB_READ[TABLE.Customer].find({'customer_name': 'Pinnacal'}).count() <= 0:
    print("customer_id Not found, creating....")
    config.energy_iot_DB_READ[TABLE.Customer].insert_one({'customer_name':'Pinnacal', 'value':0})
    
#Location Table
if config.energy_iot_DB_READ[TABLE.Location].find({'location_name': 'Chennai'}).count() <= 0:
    print("Location_id Not found, creating....")
    config.energy_iot_DB_READ[TABLE.Location].insert_one({'location_name':'Chennai', 'value':0})
    
#Location_Group Table
if config.energy_iot_DB_READ[TABLE.locationgroup].find({'location_group_name': 'Chennai'}).count() <= 0:
    print("Location_Group_id Not found, creating....")
    config.energy_iot_DB_READ[TABLE.locationgroup].insert_one({'location_group_name':'Chennai', 'value':0})
    
#Location_Group Table
if config.energy_iot_DB_READ[TABLE.asset].find({'asset_name': 'IOT'}).count() <= 0:
    print("asset_id Not found, creating....")
    config.energy_iot_DB_READ[TABLE.asset].insert_one({'asset_name':'IOT', 'value':0})
    


#update asset id
def updateassetID(value):
    asset_id = config.energy_iot_DB_READ[TABLE.asset].find_one()['value']
    asset_id += value
    config.energy_iot_DB_READ[TABLE.asset].update_one(
        {'asset_name':'IOT'},
        {'$set':
            {'value':asset_id}
        })
        
        
#update client id
def updateClientID(value):
    client_id = config.energy_iot_DB_READ[TABLE.Client].find_one()['value']
    client_id += value
    config.energy_iot_DB_READ[TABLE.Client].update_one(
        {'client_name':'test'},
        {'$set':
            {'value':client_id}
        })
        
#update form  id
def updateFormID(value):
    form_id = config.energy_iot_DB_READ[TABLE.Form].find_one()['value']
    form_id += value
    config.energy_iot_DB_READ[TABLE.Form].update_one(
        {'form_name':'form'},
        {'$set':
            {'value':form_id}
        })
        
#update menu id
def updateMenuID(value):
    menu_id = config.energy_iot_DB_READ[TABLE.Menu].find_one()['value']
    menu_id += value
    config.energy_iot_DB_READ[TABLE.Menu].update_one(
        {'menu_name':'menu'},
        {'$set':
            {'value':menu_id}
        })

#update role id
def updateRoleID(value):
    role_id = config.energy_iot_DB_READ[TABLE.Role].find_one()['value']
    role_id += value
    config.energy_iot_DB_READ[TABLE.Role].update_one(
        {'role_name':'User'},
        {'$set':
            {'value':role_id}
        })
        
#update customer id
def updateCustomerID(value):
    customer_id = config.energy_iot_DB_READ[TABLE.Customer].find_one()['value']
    customer_id += value
    config.energy_iot_DB_READ[TABLE.Customer].update_one(
        {'customer_name':'Pinnacal'},
        {'$set':
            {'value':customer_id}
        })
        
        
#update Location id
def updateLocationID(value):
    customer_id = config.energy_iot_DB_READ[TABLE.Location].find_one()['value']
    customer_id += value
    config.energy_iot_DB_READ[TABLE.Location].update_one(
        {'location_name':'Chennai'},
        {'$set':
            {'value':location_id}
        })
        
        
#User table Create
def UserID(value):
    user_id = config.energy_iot_DB_READ[TABLE.User].find_one()['value']
    user_id += value
    config.energy_iot_DB_READ[TABLE.User].update_one(
        {'user_name':'Admin'},
        {'$set':
            {'value':user_id}
        })
    
    


#Client Setup
@Admin.route('/client_setup', methods=['POST'])
def createClient():
    clicked=None
    db=config.energy_iot_DB_READ[TABLE.Client]
    id=request.values.get("client_id")
    print(id, "QQQQQQQQQQQQQQ")
    #~ sal=request.form['Salutation']
    #~ print(sal,"=============>")
    
    if request.method=='POST':
        location_name = config.energy_iot_DB_READ[TABLE.Location].find({"_id":ObjectId(request.form['location_name'])})
        location_code = config.energy_iot_DB_READ[TABLE.Location].find({"_id":ObjectId(request.form['location_code'])})
        client_code = request.form['client_code']
        client_name = request.form['client_name']
        uen_no = request.form['uen_no']
        tax_ref_no = request.form['tax_ref_no']
        legal_trading_name = request.form['legal_trading_name']
        contract_start_date = request.form['contract_start_date']
        contract_end_date = request.form['contract_end_date']
        preferred_currency = request.form['preferred_currency']
        time_zone = request.form['time_zone']
        client_logo = request.form['client_logo']
        address_1 = request.form['address_1']
        city = request.form['city']
        state_province = request.form['state_province']
        country = request.form['country']
        address_2 = request.form['address_2']
        zip_code = request.form['zip_code']
        telephone_no = request.form['telephone_no']
        mobile_no = request.form['mobile_no']
        fax_no = request.form['fax_no']
        email_id = request.form['email_id']
        web_site = request.form['web_site']
        contact_person = request.form['contact_person']
        #~ Salutation = request.form['Salutation']
        #~ person_first_name = request.form['person_first_name']
        #~ person_last_name = request.form['person_last_name']
        #~ person_email_id = request.form['person_email_id']
        #~ person_mobile_no = request.form['person_mobile_no']
        #~ person_telephone_no = request.form['person_telephone_no']
        Salutation = request.form.get('Salutation',type=str)
        person_first_name = request.form.get('person_first_name',type=str)
        person_last_name = request.form.get('person_last_name',type=str)
        person_email_id = request.form.get('person_email_id',type=str)
        person_mobile_no = request.form.get('person_mobile_no',type=str)
        person_telephone_no = request.form.get('person_telephone_no',type=str)
        header_info = request.form['header_info']
        footer_info = request.form['footer_info']
        remarks = request.form['remarks']
        no_of_useraccounts = request.form['no_of_useraccounts']
        allow_user_creation = request.form['allow_user_creation']
        active_status = request.form['active_status']
        #~ client_id = config.energy_iot_DB_READ[TABLE.Client].find_one()['value']

        if not id:
            print("wwwwwwwwwwwwwwwww")
            clients={
            'location_name':location_name, 'location_code':location_code, 
            'client_code':client_code, 'client_name':client_name, 'uen_no':uen_no, 'tax_ref_no':tax_ref_no,
            'legal_trading_name':legal_trading_name, 'contract_start_date':contract_start_date, 'contract_end_date':contract_end_date,
            'preferred_currency':preferred_currency,
            'client_logo':client_logo,'address_1':address_1,'city':city,'state_province':state_province,
            'country':country,'address_2':address_2,'zip_code':zip_code,'telephone_no':telephone_no,
            'mobile_no':mobile_no,'fax_no':fax_no,'email_id':email_id,'web_site':web_site,
            'contact_person':contact_person,
            'Salutation':Salutation,'person_first_name':person_first_name,'person_last_name':person_last_name,
            'person_email_id':person_email_id,'person_mobile_no':person_mobile_no,'person_telephone_no':person_telephone_no,
            'header_info':header_info,'footer_info':footer_info,'remarks':remarks,'no_of_useraccounts':no_of_useraccounts,
            'allow_user_creation':allow_user_creation,'active_status':active_status}

            data = config.energy_iot_DB_READ[TABLE.Client].insert_one(clients)
            finddata = config.energy_iot_DB_READ[TABLE.Client].find(clients)
            #~ updateClientID(1)
            print (finddata)
            return redirect('/admin/client_setup')
        else:
            print('SSSSSSSSSSSS')
            config.energy_iot_DB_READ[TABLE.Client].update_one({"_id": ObjectId(id)},
                                                                            {
                                                                            "$set": {
                                                                                #~ "location_name":location_name,
                                                                                #~ "location_code":location_code,
                                                                                "location_name":config.energy_iot_DB_READ[TABLE.Location].find({"_id":ObjectId(request.form['location_name'])}),
                                                                                "location_code":config.energy_iot_DB_READ[TABLE.Location].find({"_id":ObjectId(request.form['location_code'])}),
                                                                                "client_code":client_code,
                                                                                "client_name":client_name,
                                                                                "uen_no":uen_no, 
                                                                                "tax_ref_no":tax_ref_no,
                                                                                "legal_trading_name":legal_trading_name,
                                                                                "contract_start_date":contract_start_date, 
                                                                                "contract_end_date":contract_end_date,
                                                                                "preferred_currency":preferred_currency,
                                                                                "client_logo":client_logo,
                                                                                "address_1":address_1,
                                                                                "city":city,
                                                                                "state_province":state_province,
                                                                                "country":country,
                                                                                "address_2":address_2,
                                                                                "zip_code":zip_code,
                                                                                "telephone_no":telephone_no,
                                                                                "mobile_no":mobile_no,
                                                                                "fax_no":fax_no,
                                                                                "email_id":email_id,
                                                                                "web_site":web_site,
                                                                                "contact_person":contact_person,
                                                                                "Salutation":Salutation,
                                                                                "person_first_name":person_first_name,
                                                                                "person_last_name":person_last_name,
                                                                                "person_email_id":person_email_id,
                                                                                "person_mobile_no":person_mobile_no,
                                                                                "person_telephone_no":person_telephone_no,
                                                                                "header_info":header_info,
                                                                                "footer_info":footer_info,
                                                                                "remarks":remarks,
                                                                                "no_of_useraccounts":no_of_useraccounts,
                                                                                "allow_user_creation":allow_user_creation,
                                                                                "active_status":active_status
                                                                            }
                                                                            })
            return redirect('/admin/client_setup')
            
            
#Asset Setup
@Admin.route('/asset_setup', methods=['POST'])
def createAsset():
    #~ clicked=None
    db=config.energy_iot_DB_READ[TABLE.asset]
    id=request.values.get("asset_id")
    
    if request.method=='POST':
        location_name = config.energy_iot_DB_READ[TABLE.Location].find_one({"_id":ObjectId(request.form['location_name'])})
        sensor_id = request.form['sensor_id']
        devicetype = request.form['devicetype']
        model = request.form['model']
        assetcode = request.form['assetcode']
        assetname = request.form['assetname']
        assetdescription = request.form['assetdescription']
        serialno = request.form['serialno']
        partno = request.form['partno']
        quantity = request.form['quantity']
        uom = request.form['uom']
        person_incharge = request.form['person_incharge']
        active_status = request.form['active_status']
        warranty_detail = request.form['warranty_detail']
        warranty_start_date = request.form['warranty_start_date']
        warranty_expiry_date = request.form['warranty_expiry_date']
        installation_date = request.form['installation_date']
        technical_info = request.form['technical_info']
        pv_module_capacity = request.form['pv_module_capacity']
        pv_panel_type = request.form['pv_panel_type']
        pv_panel_qty = request.form['pv_panel_qty']
        pv_panel_area = request.form['pv_panel_area']
        total_panel_qty = request.form['total_panel_qty']
        
        event_required = request.form['event_required']
        alarm_required = request.form['alarm_required']
        header = request.form['header']
        communication = request.form['communication']
        parameter_name = request.form['parameter_name']

        if not id:
            asset={
            'location_name':location_name,  
            'sensor_id':sensor_id, 'devicetype':devicetype, 'model':model, 'assetcode':assetcode,
            'assetname':assetname, 'assetdescription':assetdescription, 'serialno':serialno,
            'partno':partno,
            'quantity':quantity,'uom':uom,'person_incharge':person_incharge,'active_status':active_status,
            'warranty_detail':warranty_detail,'warranty_start_date':warranty_start_date,'warranty_expiry_date':warranty_expiry_date,
            'installation_date':installation_date,
            'technical_info':technical_info,'pv_module_capacity':pv_module_capacity,
            'pv_panel_type':pv_panel_type,'pv_panel_qty':pv_panel_qty,
            'pv_panel_area':pv_panel_area,
            'total_panel_qty':total_panel_qty,'event_required':event_required,
            'alarm_required':alarm_required,
            'header':header,'communication':communication,'parameter_name':parameter_name}

            data = config.energy_iot_DB_READ[TABLE.asset].insert_one(asset)
            finddata = config.energy_iot_DB_READ[TABLE.Client].find(asset)
            print (finddata)
            return redirect('/admin/asset_setup')
        else:
            print('assettttttttttttt')
            
            return redirect('/admin/asset_setup')
        
        
#~ #Client Setup
#~ @Admin.route('/location_group', methods=['POST'])
#~ def location_group():
    #~ clicked=None
    #~ db=config.energy_iot_DB_READ[TABLE.locationgroup]
    #~ id=request.values.get("location_group_id")
    
    #~ if request.method=='POST':
        #~ location = config.energy_iot_DB_READ[TABLE.Location].find()
        
        
#Menu Setup
@Admin.route('/menu_setup', methods=['POST'])
def createMenu():
    #~ clicked=None
    db=config.energy_iot_DB_READ[TABLE.Menu]
    id=request.values.get("menu_id")
    print(id, "etrytgvuhybikjnlk;")
    
    if request.method=='POST':
        menu_name = request.form['menu_name']
        menu_description = request.form['menu_description']
        menu_url = request.form['menu_url']
        active_status = request.form['active_status']

        if not id:
            menu={
            'menu_name':menu_name, 'menu_description':menu_description, 
            'menu_url':menu_url, 'active_status':active_status
            }

            data = config.energy_iot_DB_READ[TABLE.Menu].insert_one(menu)
            finddata = config.energy_iot_DB_READ[TABLE.Menu].find(menu)
            return redirect('/admin/menu_setup')
        else:
            config.energy_iot_DB_READ[TABLE.Menu].update_one({"_id": ObjectId(id)},
                                                                            {
                                                                            "$set": {
                                                                                "menu_name":menu_name,
                                                                                "menu_description":menu_description,
                                                                                "menu_url":menu_url,
                                                                                "active_status":active_status
                                                                            }
                                                                            })
            return redirect('/admin/menu_setup')
            
            
            
#Form Setup
@Admin.route('/form', methods=['POST'])
def createForm():
    #~ clicked=None
    db=config.energy_iot_DB_READ[TABLE.Form]
    id=request.values.get("form_id")
    print(id, "11111111111111;")
    
    if request.method=='POST':
        menu_name = config.energy_iot_DB_READ[TABLE.Menu].find_one({"_id":ObjectId(request.form['menu_name'])})
        form_name = request.form['form_name']
        form_description = request.form['form_description']
        form_url = request.form['form_url']
        active_status = request.form['active_status']

        if not id:
            form={
            'menu_name':menu_name,
            'form_name':form_name, 'form_description':form_description, 
            'form_url':form_url, 'active_status':active_status
            }

            data = config.energy_iot_DB_READ[TABLE.Form].insert_one(form)
            finddata = config.energy_iot_DB_READ[TABLE.Form].find(form)
            return redirect('/admin/form')
        else:
            config.energy_iot_DB_READ[TABLE.Form].update_one({"_id": ObjectId(id)},
                                                                            {
                                                                            "$set": {
                                                                                "menu_name":menu_name,
                                                                                "form_name":form_name,
                                                                                "form_description":form_description,
                                                                                "form_url":form_url,
                                                                                "active_status":active_status
                                                                            }
                                                                            })
            return redirect('/admin/form')
        
        
        
        
        

#User Create From HTML Form
@Admin.route('/application_user', methods=['POST'])
def createUser():
    db=config.energy_iot_DB_READ[TABLE.User]
    id=request.values.get("user_id")
    if request.method=='POST':
        client_name = config.energy_iot_DB_READ[TABLE.Client].find_one({"_id":ObjectId(request.form['client_name'])})
        customer_name = config.energy_iot_DB_READ[TABLE.Customer].find_one({"_id":ObjectId(request.form['customer_name'])})
        customer_code = request.form['customer_code']
        user_name = request.form['user_name']
        password = request.form['password']
        password_confirm = request.form['password_confirm']
        effective_start_date = request.form['effective_start_date']
        effective_end_date = request.form['effective_end_date']
        active_status = request.form['active_status']
        account_status = request.form['account_status']
        email_id = request.form['email_id']
        contact_no = request.form['contact_no']
        mobile_no = request.form['mobile_no']
        salutation = request.form['salutation']
        given_name = request.form['given_name']
        sur_name = request.form['sur_name']
        gender = request.form['gender']
        security_question = request.form['security_question']
        security_answer = request.form['security_answer']
        

        if not id:
            users={'client_name':client_name, 'customer_name':customer_name, 
            'customer_code':customer_code, 'user_name':user_name, 'password':password, 
            'password_confirm':password_confirm, 'effective_start_date':effective_start_date,
            'effective_end_date':effective_end_date, 'active_status':active_status,
            'account_status':account_status, 'email_id':email_id,
            'contact_no':contact_no, 'mobile_no':mobile_no,
            'salutation':salutation, 'given_name':given_name,
            'sur_name':sur_name, 'gender':gender,
            'security_question':security_question, 'security_answer':security_answer
            }

            data = config.energy_iot_DB_READ[TABLE.User].insert_one(users)
            finddata = config.energy_iot_DB_READ[TABLE.User].find(users)
            return redirect('/admin/application_user')
        else:
            print('SSSSSSSSSSSS')
            config.energy_iot_DB_READ[TABLE.User].update_one({"_id": ObjectId(id)},
                                                                            {
                                                                            "$set": {
                                                                                "client_name":client_name, 
                                                                                "customer_name":customer_name, 
                                                                                "customer_code":customer_code, 
                                                                                "user_name":user_name, 
                                                                                "password":password, 
                                                                                "password_confirm":password_confirm, 
                                                                                "effective_start_date":effective_start_date,
                                                                                "effective_end_date":effective_end_date, 
                                                                                "active_status":active_status,
                                                                                "account_status":account_status, 
                                                                                "email_id":email_id,
                                                                                "contact_no":contact_no, 
                                                                                "mobile_no":mobile_no,
                                                                                "salutation":salutation, 
                                                                                "given_name":given_name,
                                                                                "sur_name":sur_name, 
                                                                                "gender":gender,
                                                                                "security_question":security_question, 
                                                                                "security_answer":security_answer
                                                                            }
                                                                            })
            return redirect('/admin/application_user')
            


#Role Setup
@Admin.route('/role', methods=['POST'])
def createRole():
    clicked=None
    db=config.energy_iot_DB_READ[TABLE.Role]
    id=request.values.get("role_id")    
    if request.method=='POST':
        role_name = request.form['role_name']
        role_description = request.form['role_description']
        active_status = request.form['active_status']
        if not id:
            role={
            'role_name':role_name, 'role_description':role_description, 
            'active_status':active_status}
            data = config.energy_iot_DB_READ[TABLE.Role].insert_one(role)
            findrole = config.energy_iot_DB_READ[TABLE.Role].find(role)
            print (findrole)
            return redirect('/admin/role')
        else:
            config.energy_iot_DB_READ[TABLE.Role].update_one({"_id": ObjectId(id)},
                                                                            {
                                                                            "$set": {
                                                                                "role_name":role_name,
                                                                                "role_description":role_description,
                                                                                "active_status":active_status
                                                                            }
                                                                            })
            return redirect('/admin/role')



            
            
@Admin.route('/customer_setup', methods=['POST'])
def createCustomer():
    db=config.energy_iot_DB_READ[TABLE.Customer]
    id=request.values.get("customer_id")
    print(id, "=====================>customerID")
    if request.method=='POST':        
        client_name = config.energy_iot_DB_READ[TABLE.Client].find_one({"_id":ObjectId(request.form['client_name'])})
        customer_name = request.form['customer_name']
        uen_no = request.form['uen_no']
        tax_ref_no = request.form['tax_ref_no']
        legal_trading_name = request.form['legal_trading_name']
        effective_start_date = request.form['effective_start_date']
        effective_end_date = request.form['effective_end_date']
        time_zone = request.form['time_zone']
        company_logo = request.form['company_logo']
        address_1 = request.form['address_1']
        city = request.form['city']
        state_province = request.form['state_province']
        country = request.form['country']
        address_2 = request.form['address_2']
        zip_code = request.form['zip_code']
        telephone_no = request.form['telephone_no']
        mobile_no = request.form['mobile_no']
        fax_no = request.form['fax_no']
        email_id = request.form['email_id']
        web_site = request.form['web_site']
        contact_person = request.form['contact_person']
        #~ Salutation = request.form['Salutation']
        #~ cus_first_name = request.form['cus_first_name']
        #~ cus_last_name = request.form['cus_last_name']
        #~ cus_email_id = request.form['cus_email_id']
        #~ cus_mobile_no = request.form['cus_mobile_no']
        #~ cus_telephone_no = request.form['cus_telephone_no']
        Salutation = request.form.get('Salutation',type=str)
        cus_first_name = request.form.get('cus_first_name',type=str)
        cus_last_name = request.form.get('cus_last_name',type=str)
        cus_email_id = request.form.get('cus_email_id',type=str)
        cus_mobile_no = request.form.get('cus_mobile_no',type=str)
        cus_telephone_no = request.form.get('cus_telephone_no',type=str)
        remarks = request.form['remarks']
        allow_customer_portal = request.form['allow_customer_portal']
        active_status = request.form['active_status']

        if not id:
            print("")
            customers={'client_name':client_name,'customer_name':customer_name, 'uen_no':uen_no, 'tax_ref_no':tax_ref_no,
            'legal_trading_name':legal_trading_name, 'effective_start_date':effective_start_date, 'effective_end_date':effective_end_date,
            'company_logo':company_logo,'address_1':address_1,'city':city,'state_province':state_province,
            'country':country,'address_2':address_2,'zip_code':zip_code,'telephone_no':telephone_no,
            'mobile_no':mobile_no,'fax_no':fax_no,'email_id':email_id,'web_site':web_site,
            'contact_person':contact_person,'Salutation':Salutation,'cus_first_name':cus_first_name,'cus_last_name':cus_last_name,
            'cus_email_id':cus_email_id,'cus_mobile_no':cus_mobile_no,'cus_telephone_no':cus_telephone_no,
            'remarks':remarks,
            'allow_customer_portal':allow_customer_portal,'active_status':active_status }

            data = config.energy_iot_DB_READ[TABLE.Customer].insert_one(customers)
            finddata = config.energy_iot_DB_READ[TABLE.Customer].find(customers)
            #~ updatecustomerID(1)
            print (finddata)
            return redirect('/admin/customer_setup')
        else:
            print('CcCCCCCCCCCCCCCCCCCCCCCC')
            config.energy_iot_DB_READ[TABLE.Customer].update_one({"_id": ObjectId(id)},
                                                                            {
                                                                            "$set": {
                                                                                "client_name":client_name,
                                                                                "customer_name":customer_name,
                                                                                "uen_no":uen_no, 
                                                                                "tax_ref_no":tax_ref_no,
                                                                                "legal_trading_name":legal_trading_name,
                                                                                "effective_start_date":effective_start_date, 
                                                                                "effective_end_date":effective_end_date,
                                                                                "company_logo":company_logo,
                                                                                "address_1":address_1,
                                                                                "city":city,
                                                                                "state_province":state_province,
                                                                                "country":country,
                                                                                "address_2":address_2,
                                                                                "zip_code":zip_code,
                                                                                "telephone_no":telephone_no,
                                                                                "mobile_no":mobile_no,
                                                                                "fax_no":fax_no,
                                                                                "email_id":email_id,
                                                                                "web_site":web_site,
                                                                                "contact_person":contact_person,
                                                                                "Salutation":Salutation,
                                                                                "cus_first_name":cus_first_name,
                                                                                "cus_last_name":cus_last_name,
                                                                                "cus_email_id":cus_email_id,
                                                                                "cus_mobile_no":cus_mobile_no,
                                                                                "cus_telephone_no":cus_telephone_no,
                                                                                "remarks":remarks,
                                                                                "allow_customer_portal":allow_customer_portal,
                                                                                "active_status":active_status
                                                                            }
                                                                            })
            return redirect('/admin/customer_setup')
 


@Admin.route('/location_setup', methods=['POST'])
def locationCustomer():
    #~ field_form = GetFieldForm()
    #~ URL = "http://maps.googleapis.com/maps/api/geocode/json"
    db=config.energy_iot_DB_READ[TABLE.Location]
    id=request.values.get("location_id")
    print(id, "=====================>LocationID")
    if request.method=='POST':
        location_code = request.form['location_code']
        location_name = request.form['location_name']
        location_description = request.form['location_description']
        resource_path = request.form['resource_path']
        area_name = request.form['area_name']
        block_code = request.form['block_code']
        city = request.form["city"]
        country = request.form['country']
        geo_code = request.form['geo_code']
        unit_no = request.form['unit_no']
        postal_code = request.form['postal_code']
        latitude = request.form['latitude']
        longitude = request.form['longitude']
        suplier_code = request.form['suplier_code']
        supplier_name = request.form['supplier_name']
        #~ file = request.form['file']
        f = request.files['file']
        f.save(secure_filename(f.filename))
        #~ f = os.path.join(app.config[UPLOAD_FOLDER], logo.filename)
        #~ logo.save(f)
       
            

        if not id:
            print("")
            locations={'location_code':location_code,'location_name':location_name, 'location_description':location_description, 
            'resource_path':resource_path, 'area_name':area_name, 'block_code':block_code,
            'city':city,'country':country,'geo_code':geo_code,'unit_no':unit_no,
            #~ 'file':file,
            'postal_code':postal_code,'latitude':latitude,'longitude':longitude,'suplier_code':suplier_code,
            'supplier_name':supplier_name }

            data = config.energy_iot_DB_READ[TABLE.Location].insert_one(locations)
            finddata = config.energy_iot_DB_READ[TABLE.Location].find(locations)
            #~ updatecustomerID(1)
            print (finddata)
            return render_template("sub_pages/common_template.html", pagename="location_setup",title="location", 
                                menu="menu_location_setup")
        else:
            print('llllllllllllllllllllllllll')
            config.energy_iot_DB_READ[TABLE.Location].update_one({"_id": ObjectId(id)},
                                                                            {
                                                                            "$set": {
                                                                                "location_code":location_code,
                                                                                "location_name":location_name, 
                                                                                "location_description":location_description,
                                                                                "resource_path":resource_path,
                                                                                "area_name":area_name,
                                                                                "block_code":block_code,
                                                                                "city":city,
                                                                                "country":country,
                                                                                "geo_code":geo_code,
                                                                                "unit_no":unit_no,
                                                                                #~ "logo":logo,
                                                                                "postal_code":postal_code,
                                                                                "latitude":latitude,
                                                                                "longitude":longitude,
                                                                                "suplier_code":suplier_code,
                                                                                "supplier_name":supplier_name
                                                                            }
                                                                            })
            return redirect('/admin/location_setup')




#Deleting a client with key references
@Admin.route("/remove")
def remove ():
    key=request.values.get("_id")
    client=config.energy_iot_DB_READ[TABLE.Client]
    client.remove({"_id":ObjectId(key)})
    print(client)
    return render_template("sub_pages/common_template.html", pagename="client_setup",title="Client", 
                                menu="menu_gl",client_details=config.energy_iot_DB_READ[TABLE.Client].find())
#Deleting Menu
@Admin.route("/menu_remove")
def menu_remove ():
    key=request.values.get("_id")
    menu=config.energy_iot_DB_READ[TABLE.Menu]
    menu.remove({"_id":ObjectId(key)})
    print(menu)
    return render_template("sub_pages/common_template.html", pagename="menu",title="Menu",
                            menu="menu_menumgt",menu_details=config.energy_iot_DB_READ[TABLE.Menu].find())
                                
#Deleting Form
@Admin.route("/form_remove")
def form_remove ():
    key=request.values.get("_id")
    form=config.energy_iot_DB_READ[TABLE.Form]
    form.remove({"_id":ObjectId(key)})
    print(form)
    return render_template("sub_pages/common_template.html", pagename="form",title="Form",
                               menu="menu_form",form_details=config.energy_iot_DB_READ[TABLE.Form].find())
                                
                                
#Deleting Role
@Admin.route("/role_remove")
def role_remove ():
    key=request.values.get("_id")
    role=config.energy_iot_DB_READ[TABLE.Role]
    role.remove({"_id":ObjectId(key)})
    print(role)
    return render_template("sub_pages/common_template.html", pagename="user_role",title="Role", 
                                menu="menu_au",role_details=config.energy_iot_DB_READ[TABLE.Role].find())


#Deleting a Customer with key references
@Admin.route("/customer_remove")
def customer_remove ():
    key=request.values.get("_id")
    customer=config.energy_iot_DB_READ[TABLE.Customer]
    customer.remove({"_id":ObjectId(key)})
    print(customer)
    return render_template("sub_pages/common_template.html", pagename="customer_setup",title="Customer", 
                                menu="menu_cussetup",customer_details=config.energy_iot_DB_READ[TABLE.Customer].find())

#Deleting a Location with key references
@Admin.route("/location_remove")
def location_remove ():
    key=request.values.get("_id")
    location=config.energy_iot_DB_READ[TABLE.Location]
    location.remove({"_id":ObjectId(key)})
    print(location)
    return render_template("sub_pages/common_template.html", pagename="location_setup",title="location", 
                                menu="menu_location_setup",location_details=config.energy_iot_DB_READ[TABLE.Location].find())
                                
#Deleting a User with key references
@Admin.route("/user_remove")
def user_remove ():
    key=request.values.get("_id")
    user=config.energy_iot_DB_READ[TABLE.User]
    user.remove({"_id":ObjectId(key)})
    return render_template("sub_pages/common_template.html", pagename="application_user",title="User", 
                                menu="menu_au",user_details=config.energy_iot_DB_READ[TABLE.User].find())
                                
                                


#data finding for client
@Admin.route("/client_setup_update/<client_id>")
def client_setup_update(client_id):
    client = config.energy_iot_DB_READ[TABLE.Client].find_one({"_id":ObjectId(client_id)})
    location = config.energy_iot_DB_READ[TABLE.Client].find({"_id":ObjectId(client_id)})
    #~ locations = config.energy_iot_DB_READ[TABLE.Client].find({"_id":ObjectId(request.form['location_name'])})
    return render_template("sub_pages/common_template.html", pagename="client_setup",title="Client",
                            menu="menu_gl", client_code=client.get('client_code'), client_id=client_id,
                           #~ location_name = config.energy_iot_DB_READ[TABLE.Location].find_all(),
                           #~ location_code = config.energy_iot_DB_READ[TABLE.Location].find_all(),
                           location_name=client.get('location_name'),location_code=client.get('location_code'),
                           client_name=client.get('client_name'),uen_no=client.get('uen_no'),
                           tax_ref_no=client.get('tax_ref_no'),legal_trading_name=client.get('legal_trading_name'),
                           contract_start_date=client.get('contract_start_date'),contract_end_date=client.get('contract_end_date'),
                           preferred_currency=client.get('preferred_currency'),time_zone=client.get('time_zone'),
                           client_logo=client.get('client_logo'),address_1=client.get('address_1'),
                           city=client.get('city'),state_province=client.get('state_province'),
                           country=client.get('country'),address_2=client.get('address_2'),
                           zip_code=client.get('zip_code'),mobile_no=client.get('mobile_no'),fax_no=client.get('fax_no'),
                           email_id=client.get('email_id'),web_site=client.get('web_site'),contact_person=client.get('contact_person'),
                           Salutation=client.get('Salutation'),person_first_name=client.get('person_first_name'),
                           person_last_name=client.get('person_last_name'),person_email_id=client.get('person_email_id'),
                           person_mobile_no=client.get('person_mobile_no'),person_telephone_no=client.get('person_telephone_no'),
                           header_info=client.get('header_info'),footer_info=client.get('footer_info'),
                           remarks=client.get('remarks'),no_of_useraccounts=client.get('no_of_useraccounts'),
                           allow_user_creation=client.get('allow_user_creation'),active_status=client.get('active_status'))
                           
#data finding for User
@Admin.route("/user_setup_update/<user_id>")
def user_setup_update(user_id):
    user = config.energy_iot_DB_READ[TABLE.User].find_one({"_id":ObjectId(user_id)})
    client = config.energy_iot_DB_READ[TABLE.Client].find_one({"_id":ObjectId(user_id)})
    print(user)
    return render_template("sub_pages/common_template.html", pagename="application_user",title="User",
                            menu="menu_au", client_name=user.get('client_name'), user_id=user_id,
                            customer_name=user.get('customer_name'),customer_code=user.get('customer_code'),
                            user_name=user.get('user_name'),password=user.get('password'),
                            password_confirm=user.get('password_confirm'),effective_start_date=user.get('effective_start_date'),
                            effective_end_date=user.get('effective_end_date'),active_status=user.get('active_status'),
                            account_status=user.get('account_status'),email_id=user.get('email_id'),
                            contact_no=user.get('contact_no'),mobile_no=user.get('mobile_no'),
                            salutation=user.get('salutation'),given_name=user.get('given_name'),
                            sur_name=user.get('sur_name'),gender=user.get('gender'),
                            security_question=user.get('security_question'),security_answer=user.get('security_answer')
                            )
                            
                           
                           
#data finding for menu
@Admin.route("/menu_setup_update/<menu_id>")
def menu_setup_update(menu_id):
    menu = config.energy_iot_DB_READ[TABLE.Menu].find_one({"_id":ObjectId(menu_id)})
    return render_template("sub_pages/common_template.html", pagename="menu",title="Menu",
                           menu="menu_menumgt",menu_id=menu_id,
                           menu_name=menu.get('menu_name'), 
                           menu_description=menu.get('menu_description'),
                           menu_url=menu.get('menu_url'),
                           active_status=menu.get('active_status'))

#data finding for form
@Admin.route("/form_setup_update/<form_id>")
def form_setup_update(form_id):
    form = config.energy_iot_DB_READ[TABLE.Form].find_one({"_id":ObjectId(form_id)})
    return render_template("sub_pages/common_template.html", pagename="form",title="Form",
                               menu="menu_form",
                           menus = config.energy_iot_DB_READ[TABLE.Menu].find(),
                           form_id=form_id,
                           form_name=menu.get('form_name'), 
                           form_description=menu.get('form_description'),
                           form_url=menu.get('form_url'),
                           active_status=menu.get('active_status'))


                           
                           
#data finding for Role
@Admin.route("/role_setup_update/<role_id>")
def role_setup_update(role_id):
    role = config.energy_iot_DB_READ[TABLE.Role].find_one({"_id":ObjectId(role_id)})
    print(role)
    return render_template("sub_pages/common_template.html", pagename="user_role",title="Role",
                            menu="menu_au", role_name=role.get('role_name'), role_id=role_id,
                            role_description=role.get('role_description'),active_status=role.get('active_status')
                            )

#data finding for customer
@Admin.route("/customer_setup_update/<customer_id>")
def customer_setup_update(customer_id):
    customer = config.energy_iot_DB_READ[TABLE.Customer].find_one({"_id":ObjectId(customer_id)})
    return render_template("sub_pages/common_template.html", pagename="customer_setup",title="customer",
                            menu="menu_cussetup",
                           clients = config.energy_iot_DB_READ[TABLE.Client].find(),
                           #~ clients=customer.get('client_name'),
                           customer_id=customer_id,
                           customer_name=customer.get('customer_name'),uen_no=customer.get('uen_no'),
                           tax_ref_no=customer.get('tax_ref_no'),legal_trading_name=customer.get('legal_trading_name'),
                           effective_start_date=customer.get('effective_start_date'),effective_end_date=customer.get('effective_end_date'),
                           time_zone=customer.get('time_zone'),
                           company_logo=customer.get('company_logo'),address_1=customer.get('address_1'),
                           city=customer.get('city'),state_province=customer.get('state_province'),
                           country=customer.get('country'),address_2=customer.get('address_2'),
                           zip_code=customer.get('zip_code'),mobile_no=customer.get('mobile_no'),fax_no=customer.get('fax_no'),
                           email_id=customer.get('email_id'),web_site=customer.get('web_site'),contact_person=customer.get('contact_person'),
                           Salutation=customer.get('Salutation'),cus_first_name=customer.get('cus_first_name'),
                           cus_last_name=customer.get('cus_last_name'),cus_email_id=customer.get('cus_email_id'),
                           cus_mobile_no=customer.get('cus_mobile_no'),cus_telephone_no=customer.get('cus_telephone_no'),
                           remarks=customer.get('remarks'),
                           allow_customer_portal=customer.get('allow_customer_portal'),active_status=customer.get('active_status'))
                           
#data finding for location
@Admin.route("/location_setup_update/<location_id>")
def location_setup_update(location_id):
    print (location_id, "DDDDDDDDDDDDDDDDDDDDD")
    print(config.energy_iot_DB_READ[TABLE.Location].find_one({"_id":ObjectId(location_id)}))
    location = config.energy_iot_DB_READ[TABLE.Location].find_one({"_id":ObjectId(location_id)})
    return render_template("sub_pages/common_template.html", pagename="location_setup",title="location",
                            menu="menu_location_setup", location_code=location.get('location_code'),location_id=location_id,
                           location_name=location.get('location_name'),location_description=location.get('location_description'),
                           resource_path=location.get('resource_path'),area_name=location.get('area_name'),
                           block_code=location.get('block_code'),city=location.get('city'),
                           country=location.get('country'),
                           geo_code=location.get('geo_code'),unit_no=location.get('unit_no'),
                           #~ logo=location.get('logo'),
                           postal_code=location.get('postal_code'),latitude=location.get('latitude'),
                           longitude=location.get('longitude'),suplier_code=location.get('suplier_code'),
                           supplier_name=location.get('supplier_name'))
                           

@Admin.route('/client_setup' )
def client_setup():
        print('Client Setup')
        for i in config.energy_iot_DB_READ[TABLE.Client].find():
            print(i, '##############')
        return render_template('sub_pages/common_template.html', pagename="client_setup",title="Client",
                               menu="menu_gl",client_details=config.energy_iot_DB_READ[TABLE.Client].find(),
                               location_name=config.energy_iot_DB_READ[TABLE.Location].find(),location_code=config.energy_iot_DB_READ[TABLE.Location].find())

@Admin.route('/customer_setup')
def customer_setup():
        print('Customer Setup')
        for i in config.energy_iot_DB_READ[TABLE.Client].find():
            pprint.pprint(i)
        return render_template('sub_pages/common_template.html', pagename="customer_setup",title="Customer",
                               menu="menu_cussetup",customer_details=config.energy_iot_DB_READ[TABLE.Customer].find(),
                               clients=config.energy_iot_DB_READ[TABLE.Client].find()) 


@Admin.route('/application_user')
def application_user():
        print('Application User')
        #~ for i in config.energy_iot_DB_READ[TABLE.Client].find():
            #~ pprint.pprint(i,"22222222222222222222222222")
        return render_template('sub_pages/common_template.html', pagename="application_user",title="Application User",
                               menu="menu_au",user=config.energy_iot_DB_READ[TABLE.User].find(),
                               client_name=config.energy_iot_DB_READ[TABLE.Client].find(),
                               customer_name=config.energy_iot_DB_READ[TABLE.Customer].find())


@Admin.route('/location_setup')
def location_setup():
        print('Location Setup')
        return render_template('sub_pages/common_template.html', pagename="location_setup",title="Location Setup",
                               menu="menu_location_setup",
                               location_details=config.energy_iot_DB_READ[TABLE.Location].find())


@Admin.route('/asset_summary')
def asset_summary():
        print('Asset Summary')
        return render_template('sub_pages/common_template.html', pagename="asset_summary",title="Asset Summary",
                               menu="menu_assetsummary")


@Admin.route('/asset_setup')
def asset_setup():
        print('Asset Setup')
        return render_template('sub_pages/common_template.html', pagename="asset_setup",title="Asset Setup",
                               menu="menu_assetsetup",asset_name=config.energy_iot_DB_READ[TABLE.asset].find(),
                               locations=config.energy_iot_DB_READ[TABLE.Location].find())
                               
@Admin.route('/menu_setup')
def menu_setup():
        print('Menu Setup')
        for i in config.energy_iot_DB_READ[TABLE.Menu].find():
            pprint.pprint(i)
        return render_template('sub_pages/common_template.html', pagename="menu",title="Menu",
                               menu="menu_menumgt",menu_details=config.energy_iot_DB_READ[TABLE.Menu].find())


@Admin.route('/form')
def form():
        print('Form Setup')
        for i in config.energy_iot_DB_READ[TABLE.Form].find():
            pprint.pprint(i)
        return render_template('sub_pages/common_template.html', pagename="form",title="Form",
                               form="menu_form",form_details=config.energy_iot_DB_READ[TABLE.Form].find(),
                               menus=config.energy_iot_DB_READ[TABLE.Menu].find())

@Admin.route('/role')
def user_role():
        print('Role')
        return render_template('sub_pages/common_template.html', pagename="user_role",title="Role",
                               menu="menu_au",role_details=config.energy_iot_DB_READ[TABLE.Role].find())


@Admin.route('/_get_geocode', methods=['GET', 'POST'])
def _get_geocode():    
    city = request.args.get('city')
    postal_code = request.args.get('postal_code')
    geolocator = Nominatim()
    if city:
        location = geolocator.geocode(city)
    elif postal_code:
        location = geolocator.geocode(postal_code)
    if location:        
        return jsfy(result=[location.latitude, location.longitude])
    else:
        return jsfy(result=[0, 0])


#~ @app.route('/download/<file_name>')
#~ def index(file_name):
    #~ grid_fs_file = grid_fs.find_one({'filename': file_name})
    #~ response = make_response(grid_fs_file.read())
    #~ response.headers['Content-Type'] = 'application/octet-stream'
    #~ response.headers["Content-Disposition"] = "attachment; filename={}".format(file_name)
    #~ return response

@Admin.route('/privileges_setting', methods=['GET', 'POST'])
def privileges_setting():
        print('Privileges Settings')
        return render_template('sub_pages/common_template.html', pagename="privileges_settings",title="Privileges Settings",
                               menu="menu_privilegessetting")

@Admin.route('/irr_assignment', methods=['GET', 'POST'])
def irr_assignment():
        print('IRR Assignments')
        return render_template('sub_pages/common_template.html', pagename="irr_assignment",title="IRR Assignment",
                               menu="menu_irrassign")

@Admin.route('/location_group', methods=['GET', 'POST'])
def location_group():
        print('Location Group')
        return render_template('sub_pages/common_template.html', pagename="location_group",title="Location Group",
                               menu="menu_locgroup")

