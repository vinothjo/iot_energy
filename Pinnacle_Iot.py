#!/usr/bin/python3
import logging
from logging.handlers import RotatingFileHandler
from config import LOG_PATH, SECREAT_KEY, LEVEL, app, HOST, PORT, APP_NAME
from flask import  session, render_template
#~ from flask_googlemaps import GoogleMaps



@app.before_first_request
def init():
    app.logger.info('info INIT message')


# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.route('/')
@app.route('/SolarNova2')
def home():
    session.pop('TOKEN', None)
    return render_template('login.html',APP_NAME=APP_NAME,error="")


from Cron_job.controllers import cron_job as cron_job
app.register_blueprint(cron_job)

from Admin_Module.controllers import Admin as Admin
app.register_blueprint(Admin)

from IotSuite_Module.controllers import Iot as Iot
app.register_blueprint(Iot)

if __name__ == '__main__':
    app.secret_key = SECREAT_KEY
    # initialize the log handler
    logHandler = RotatingFileHandler('logs/energy_iot.log', maxBytes=10000000, backupCount=1)
    # set the log handler level
    logHandler.setLevel(LEVEL)
    # set the app logger level
    app.logger.setLevel(LEVEL)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logHandler.setFormatter(formatter)
    app.logger.addHandler(logHandler)

    #log = logging.getLogger('werkzeug')
    #log.setLevel(logging.INFO)
    #log.addHandler(logHandler)
    #~ app.config['GOOGLEMAPS_KEY'] = "AIzaSyBLTcvxoWpOs4cP4CbSJAkz_cuVdaNvlWs"
    #~ GoogleMaps(app)
    #~ GoogleMaps(app, key="AIzaSyBLTcvxoWpOs4cP4CbSJAkz_cuVdaNvlWs")



    app.run(host=HOST, port=PORT,threaded=True,debug=True)
    
    
