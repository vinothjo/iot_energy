#!/usr/bin/python3
from functools import partial
import pytz
import datetime
import pymongo
import requests
import collections
from pymongo import Mongocustomer
from flask_wtf import Form as FlaskForm
from flask_wtf import FlaskForm
from wtforms import TextField, IntegerField, SubmitField

customer = Mongocustomer('localhost:27017')
db = customer.iot_app_user


class Customer(object):

    def __init__(self,customer_code, customer_name, uen_no,tax_ref_no,
    legal_trading_name,effective_start_date,effective_end_date,company_logo,address_1,
    city,state_province,country,address_2,zip_code,telephone_no,mobile_no,fax_no,email_id,web_site,
    contact_person,Salutation,cus_first_name,cus_last_name,cus_email_id,cus_mobile_no,cus_telephone_no,
    remarks,no_of_useraccounts,allow_customer_portal,active_status,is_active,updated_by,updated_on=str(datetime.datetime.now())):
        
        self.customer_code = customer_code
        self.customer_name = customer_name
        self.uen_no = uen_no
        self.tax_ref_no = tax_ref_no
        self.legal_trading_name = legal_trading_name
        self.effective_start_date = effective_start_date
        self.effective_end_date = effective_end_date
        self.company_logo = company_logo
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
        self.cus_first_name = cus_first_name
        self.cus_last_name = cus_last_name
        self.cus_email_id = cus_email_id
        self.cus_mobile_no = cus_mobile_no
        self.cus_telephone_no = cus_telephone_no
        self.remarks = remarks
        self.allow_customer_portal = allow_customer_portal
        self.active_status = active_status
        self.is_active = is_active
        self.updated_by = updated_by
        self.updated_on = updated_on
        
        
   

