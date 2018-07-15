#!/usr/bin/python3
from functools import partial
import pytz
import datetime
import pymongo
import requests
import collections
from pymongo import MongoClient
from flask_wtf import Form as FlaskForm
from flask_wtf import FlaskForm
from wtforms import TextField, IntegerField, SubmitField

client = MongoClient('localhost:27017')
db = client.iot_app_user


class Client(object):

    def __init__(self,client_code, client_name, uen_no,tax_ref_no,
    legal_trading_name,contract_start_date,preferred_currency,client_logo,address_1,
    city,state_province,country,address_2,zip_code,telephone_no,mobile_no,fax_no,email_id,web_site,
    contact_person,Salutation,person_first_name,person_last_name,person_email_id,person_mobile_no,person_telephone_no,
    header_info,footer_info,remarks,no_of_useraccounts,allow_user_creation,active_status,is_active,updated_by,updated_on=str(datetime.datetime.now())):
        
        self.client_code = client_code
        self.client_name = client_name
        self.uen_no = uen_no
        self.tax_ref_no = tax_ref_no
        self.legal_trading_name = legal_trading_name
        self.contract_start_date = contract_start_date
        self.preferred_currency = preferred_currency
        self.client_logo = client_logo
        self.address_1 = address_1
        self.city = city
        self.state_province = state_province
        self.country = country
        self.address_2 = address_2
        self.zip_code = zip_code
        self.telephone_no = telephone_no
        self.mobile_no = mobile_no
        self.fax_no = fax_no
        self.email_id = email_id
        self.web_site = web_site
        self.contact_person = contact_person
        self.Salutation = Salutation
        self.person_first_name = person_first_name
        self.person_last_name = person_last_name
        self.person_email_id = person_email_id
        self.person_mobile_no = person_mobile_no
        self.person_telephone_no = person_telephone_no
        self.header_info = header_info
        self.footer_info = footer_info
        self.remarks = remarks
        self.no_of_useraccounts = no_of_useraccounts
        self.allow_user_creation = allow_user_creation
        self.active_status = active_status
        self.is_active = is_active
        self.updated_by = updated_by
        self.updated_on = updated_on
        
        
   

