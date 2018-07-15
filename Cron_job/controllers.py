from flask import  render_template, request , Blueprint

import config
from Cron_job.CronServices import CronServices
from config import app
import traceback

cron_services = CronServices()
cron_job = Blueprint('cron_job', __name__, url_prefix='/cron')

# Flask views
@cron_job.route('/')
def index():
    return render_template('index.html')

@cron_job.route("/db_test")
def db_test():
    print('/db_test')
    data = config.energy_iot_DB_RW.iot_test.find_one()
    return (str(data['stored_time']))


# Cron Job Service 01
# Purpose : insert in to aggregation_15_min_Max table from Main table groub by time(15 min)
@cron_job.route('/insert_aggregation_15_min_Max', methods=['GET'])
def aggregate_15_min_Max():
    device_type = request.args.get('device_type')
    sensor_type = request.args.get('sensor_type')
    duration_limit = request.args.get('duration_limit')
    if duration_limit is None:
        duration_limit = 10

    interval = "900"

    try:
        data = cron_services.insert_aggregation_15_min_Max(duration_limit=duration_limit, interval=interval, device_type=device_type,sensor_type=sensor_type)
        return str(data) + " record inserted!"

    except Exception as err:
        app.logger.error("insert_aggregation_15_min_Max >> error   " + str(err))
    return "No Record Found"


# Cron Job Service 02
# Purpose : insert in to insert_aggregation_15_minutes_summary table from 15 Minutes Max table groub by time(15 min)
@cron_job.route('/insert_aggregation_15_minutes_summary', methods=['GET'])
def aggregate_15_minutes_Summary():
    duration_limit = request.args.get('duration_limit')
    if duration_limit is None:
        duration_limit = 5

    try:
        data = cron_services.insert_aggregation_15_minutes_summary(duration_limit=duration_limit)
        return str(data) + " record inserted!"

    except Exception as err:
        app.logger.error("insert_aggregation_15_minutes_summary >> error   " + str(err))
    return "No Record Found"


# Cron Job Service 03
# Purpose : calculate the performance ratio
@cron_job.route('/aggregation_15_minutes_summary_PR_Calculation', methods=['GET'])
def PR_Calculation():
    duration_limit = request.args.get('duration_limit')
    if duration_limit is None:
        duration_limit = 5
    try:
        data = cron_services.pr_calculation(duration_limit=duration_limit)
        return str(data) + " record inserted!"

    except Exception as err:
        app.logger.error("aggregation_15_minutes_summary_PR_Calculation >> error   " + str(err))
    return "No Record Found"




# Cron Job Service 04
# Purpose : insert in to aggregation_1 hr summary table from 15 minutes summary by time(15 min)
@cron_job.route('/insert_aggregation_1_hour_summary', methods=['GET'])
def insert_aggregation_1_hour_summary():
    duration_limit = request.args.get('duration_limit')
    if duration_limit is None:
        duration_limit = 10

    try:
        data = cron_services.insert_1hour_summary(duration_limit=duration_limit)
        return str(data) + " record inserted!"

    except Exception as err:
        app.logger.error("insert_aggregation_1_hour_summary >> error   " + str(err))
        traceback.print_exc()
    return "No Record Found"


# Cron Job Service 04
# Purpose : insert in to aggregation_1 hr summary table from 15 minutes summary by time(15 min)
@cron_job.route('/insert_aggregation_1_day_summary', methods=['GET'])
def insert_aggregation_1_day_summary():
    duration_limit = request.args.get('duration_limit')
    if duration_limit is None:
        duration_limit = 3

    try:
        data = cron_services.insert_1day_summary(duration_limit=duration_limit)
        return str(data) + " record inserted!"

    except Exception as err:
        app.logger.error("insert_aggregation_1_day_summary >> error   " + str(err))
        traceback.print_exc()
    return "No Record Found"


