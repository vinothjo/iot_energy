#!/usr/bin/python3
from werkzeug.security import generate_password_hash, \
     check_password_hash
import datetime

class User(object):

    def __init__(self, username,surname,role,email,defunct,is_active, updated_by,updated_on=str(datetime.datetime.now())):
        self.username = username
        self.surname = surname
        self.role = role
        self.email = email
        self.defunct = defunct
        self.is_active = is_active
        self.updated_by = updated_by
        self.updated_on = updated_on

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

    def set_password_hash(self, password_hash):
        self.pw_hash = password_hash

    def check_password(self, password):
       # return check_password_hash(self.pw_hash, password)
       return password
