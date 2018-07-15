# ****************************************************
#  Project : Iot
#  Filename: Admin_Service.py
#  Created : sv
#  Change history:
#  dd.mm.yyyy / developer name
#  14.01.2018 / sv
# ***************************************************
#   creating admin  Controller
# ****************************************************

# Import flask dependencies
from Admin_Module.Model.User import User
from werkzeug.security import generate_password_hash, check_password_hash
import config
from Util import TABLE,Util


from Util.Util import Util
from config import app

util = Util()
class Admin_Service():


    # User validation logic
    def Validate_Auth(self, user_id, password,ip):
        try:
            app.logger.info("Validate_Auth >>   ")
            is_valid, message = self.validate_user(user_id,password)
            if is_valid:
                return True, message
            else:
                return False , "Authentication Failed : " + message

        except Exception as err:
            app.logger.error("Auth >> error  " + str(err))
            return False, "Authentication Failed" + str(err)



    def validate_user(self, username, password):
        try:
            app.logger.info("validate user >>   ")

            if username is not None:
                data = config.energy_iot_DB_READ[TABLE.IOT_APP_USER].find_one({'username': username, 'defunct': 'N', 'is_active': 'Y'})
                if data is not None:
                    app.logger.info("record Exist " + username)
                    user = User(username=data['username'], surname=data['surname'], role=data['role'],
                                email=data['email'], defunct='N', is_active='Y', updated_by=data['updated_by'])
                    user.set_password_hash(data['password'])
                    return user.check_password(password), {'username' : username, 'role' : data['role'],'surname':data['surname']}
                else:
                    app.logger.error("record dose not exist" + username)
                    return False, None
            else:
                app.logger.error("authenticate Error >> user_name None")
                return False, None

        except Exception as err:
            app.logger.error("validate_user >> error  " + str(err))
            return False, "Not updated : " + str(err)


    def save_user(self, user):
        if user is not None:
            old = config.energy_iot_DB_READ[TABLE.IOT_APP_USER].find_one({"username": user.username , "defunct": "N"})
            if old is not None:
                app.logger.error('record already exist')
                return "Error: user_name already exist"
            else:
                config.energy_iot_DB_READ[TABLE.IOT_APP_USER].insert_one(
                    {"username": user.username, "password": user.pw_hash, "name": user.surname,
                     "role": user.role, "email": user.email, "updated_by": user.updated_by,
                     "updated_on": user.updated_on, "defunct": user.defunct})
                return "DONE"
        else:
            app.logger.error("Error in save_user")
            return "Error"


