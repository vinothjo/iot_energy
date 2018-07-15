# ****************************************************
#  Project : IoT
#  Filename: controllers.py
#  Created : sv
#  Change history:
#  dd.mm.yyyy / developer name
#  14.05.2018 / sv
# ***************************************************
#   creating registration  Controller
# ****************************************************

# Import flask dependencies
import json
import numpy as np
import requests
from flask import  session
import xmltodict
from flask import Blueprint, Response, render_template, request
import plotly
from Admin_Module.controllers import requires_auth
from IotSuite_Module.Iot_DAO import Iot_DAO
from IotSuite_Module.Iot_aggregationServices import Iot_aggregationServices
from IotSuite_Module.MyEncoder import MyEncoder
from IotSuite_Module.Response_models.dashboard import Dashboard
from IotSuite_Module.iot_Service import Iot_Service
from IotSuite_Module.plot_dashboard import Plot_Dashboard
from IotSuite_Module.plot_inv import Plot_Inv
from Util.DateUtil import DateUtil
from Util.Util_Service import Util_Service
from config import app
from error_code import APP_ERRORS
import traceback
import json as simplejson
from datetime import datetime, timedelta
import csv
from Util import TABLE, Util
from flask import send_from_directory
from datetime import date

# Define the blueprint: 'registration', set its url prefix: app.url/com
Iot = Blueprint('Iot', __name__, url_prefix='/iot')

iot_service = Iot_Service()
iot_dao = Iot_DAO()
agg_Services = Iot_aggregationServices()
uti_service = Util_Service()
polt_dashboard = Plot_Dashboard()


@Iot.route('/home', methods=['GET', 'POST'])
@requires_auth
def GETDashbord_info():
    error = APP_ERRORS.NO_ERROR
    err_desc = APP_ERRORS.DESC[APP_ERRORS.NO_ERROR]
    result = Dashboard()
    try:
        filter_date = None
        filter_location_list = None
        filter_type = 'DAY'
        filter_type_nev = None
        try:
            filter_date = request.form['filter_date']
            filter_location_list = request.form.getlist('filter_location_list[]')
            filter_type = request.form['filter_type']
            filter_type_nev = request.form['filter_type_nev']
        except Exception as err:
            print(str(err))

        req_param = {'filter_date': filter_date, 'filter_location_list': filter_location_list}

        # Changing to the time format
        try:
            start_time = datetime.strptime(filter_date, '%d/%m/%Y')
            end_time = start_time + timedelta(days=int(1))
        except Exception as err:
            print(str(err))
            start_time = None
            end_time = None

        if start_time is None and start_time != "":
            start_time = DateUtil.get_current_day()
        if end_time is None and end_time != "":
            end_time = start_time + timedelta(days=int(1))

        # Change the table and time condition based on the query
        curr_day = DateUtil.get_current_day()
        if filter_type_nev == "NEXT":
            curr_day = session['last_end_time'] + timedelta(days=int(1))
            start_time = curr_day
            end_time = curr_day + timedelta(days=int(1))
        elif filter_type_nev == "PREV":
            curr_day = session['last_start_date'] - timedelta(days=int(1))
            start_time = curr_day
            end_time = curr_day + timedelta(days=int(1))

        interval = "900"  # Each 900 sec (15 min)
        device_type="Solar"
        try:

            result = agg_Services.getDashboard_info(start=start_time, end=end_time, device_type=device_type,
                                                    interval=interval, location_list=filter_location_list)

        except Exception as err:
            traceback.print_exc()
            error = APP_ERRORS.UNKNOWN
            err_desc = str(err)
            result = Dashboard()
            app.logger.error("getDashboard_info 1 >> error   " + str(err))


    except Exception as err:
        traceback.print_exc()
        result = Dashboard()
        app.logger.error("getDashboard_info 2 >> error   " + str(err))
        error = APP_ERRORS.UNKNOWN
        err_desc = str(err)

    WeatherInfo = getWeatherInfo()

    result_data = MyEncoder().encode(result)
    plot_data, layout = polt_dashboard.rander_graph(result_data);
    print(plot_data)
    print(layout)
    graphs = dict(data=plot_data, layout=layout)
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
    print('success')
    location_detail = uti_service.get_location_details()
    loc_list = []
    print(filter_location_list)
    for index, val in location_detail.items():
        val['selected'] = 'F'
        if filter_location_list:
            if (val['resource_path'] in filter_location_list):
                val['selected'] = 'Y'
        # print(val)

        loc_list.append(val)

    print(req_param)
    return render_template('home.html',menu="menu_dash", dashboard_data=result, weatherInfo=WeatherInfo, current_day_dpm=None,
                           graphJSON=graphJSON, location_detail=loc_list, filter_type=filter_type, req_param=req_param)


@Iot.route('/mapview', methods=['GET'])
@requires_auth
def Mapview():
    error = APP_ERRORS.NO_ERROR
    err_desc = APP_ERRORS.DESC[APP_ERRORS.NO_ERROR]
    result = Dashboard()
    try:
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        ty = request.args.get('type')
        values = request.args.get('values')
        device_type = request.args.get('device_type')
        loc_list = None

        if device_type is None:
            device_type = "Solar"

        if start_time is None:
            start_time = DateUtil.get_current_day()
        if end_time is None:
            end_time = start_time + timedelta(days=int(1))
        print(start_time, end_time)

        interval = "900"  # Each 900 sec (15 min)

        try:

            error, map_data = agg_Services.get15MinSummaryData_for_map(start_time, end_time)
            print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$", map_data)
            if not map_data:
                map_data = []
        except Exception as err:
            error = APP_ERRORS.UNKNOWN
            err_desc = str(err)
            app.logger.error("mapview 1 >> error   " + str(err))



    except Exception as err:
        app.logger.error("mapview 2 >> error   " + str(err))

    return render_template('Map.html',menu="menu_map" , map_data=map_data)


def getWeatherInfo():
    URL = "http://api.nea.gov.sg/api/WebAPI/?dataset=24hrs_forecast&keyref=781CF461BB6606ADD6253FC89A8B41F2742F415AA9B75B77"
    # defining a params dict for the parameters to be sent to the API
    PARAMS = {}
    # sending get request and saving the response as response object

    Country_temperature = ""
    RelativeHumidity = ""
    Forecast = ""
    Wind = ""
    try:
        r = requests.get(url=URL, params=PARAMS)
        data = json.loads(json.dumps(xmltodict.parse(r.content)))

        print(data)
        # print(str(type(data)))
        # print(data["channel"]['main']['temperature']['@high'])
        Country_temperature = data["channel"]['main']['temperature']['@high']
        RelativeHumidity = data["channel"]['main']['relativeHumidity']['@high'] + " %"
        Forecast = data["channel"]['main']['forecast']
        Wind = "Speed : " + data["channel"]['main']['wind']['@speed']
        return {"Country_temperature": Country_temperature, "RelativeHumidity": RelativeHumidity, "Forecast": Forecast,
                "Wind": Wind}
    except Exception as err:
        return {"Country_temperature": "", "RelativeHumidity": "", "Forecast": "", "Wind": ""}


@Iot.route('/Energy_info', methods=['GET'])
def getEnergy_info():
    start_time = request.args.get('start_date')
    end_time = request.args.get('to_date')
    location = request.args.get('location')
    sensor_type = request.args.get('sensor_type')
    if not sensor_type:
        sensor_type = 'DPM'

    projection = request.args.get('projection_' + sensor_type)

    req_param = {'start_date': start_time, 'to_date': end_time, 'location': location}

    try:
        start_time = datetime.strptime(start_time, '%Y-%m-%d')
        end_time = datetime.strptime(end_time, '%Y-%m-%d')
    except Exception as err:
        start_time = DateUtil.get_current_day()
        end_time = start_time + timedelta(days=int(1))

    _table = TABLE.IOT_AGG_15_MINUTES_SUMMARY_TABLE
    _projection = None
    _condition = {"sender_timestamp": {"$gte": start_time, "$lte": end_time}}
    if location and location != "ALL":
        _condition.__setitem__('resource_path', location)
    if sensor_type:
        _condition.__setitem__('sensor_type', sensor_type)

    if not projection:
        projection = 'AGGREGATE_VALUE'

    _projection = {"sender_timestamp": 1, 'resource_path': 1, 'sensor_type': 1, projection: 1}

    _sortby = "sender_timestamp"
    print(_condition)
    print(_projection)
    result = iot_dao.getrecord_from_table(_table, _condition, _projection, _sortby).reset_index()
    data_lst = []
    x = []
    y = []
    for index, row in result.iterrows():
        rw = {}
        rw.__setitem__('sender_timestamp', row['sender_timestamp'].strftime('%d-%m-%Y %H:%M'))
        x.append(row['sender_timestamp'].strftime('%H:%M-%d%b%Y '))
        rw.__setitem__('location', row['resource_path'])
        rw.__setitem__('sensor_type', row['sensor_type'])
        rw.__setitem__(projection, row[projection])
        y.append(row[projection])
        data_lst.append(rw)

    location_detail = uti_service.get_location_details()
    loc_list = []
    for index, val in location_detail.items():
        loc_list.append(val)

    plot_data, layout = polt_dashboard.rander_simplegraph(x_axies=x, y_axies_01=y, y_label_01=projection)
    print(plot_data)
    print(layout)
    graphs = dict(data=plot_data, layout=layout)
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('sub_pages/common_template.html', pagename="dyn_summary_main",menu="menu_sv", data=data_lst,
                           location_detail=loc_list, req_param=req_param,
                           graphJSON=graphJSON)


@Iot.route('/dpm_energy_production', methods=['GET', 'POST'])
def dpm_energy_production():
    print('dpm_energy_production')
    # Getting the form values
    filter_date = None
    filter_location_list = None
    filter_type = 'DAY'
    filter_type_nev = None
    try:
        filter_date = request.form['filter_date']
        filter_location_list = request.form.getlist('filter_location_list[]')
        filter_type = request.form['filter_type']
        filter_type_nev = request.form['filter_type_nev']
    except Exception as err:
        print(str(err))

    req_param = {'filter_date': filter_date, 'filter_location_list': filter_location_list}

    # Changing to the time format
    try:
        start_time = datetime.strptime(filter_date, '%d/%m/%Y')
        end_time = start_time + timedelta(days=int(1))
    except Exception as err:
        print(str(err))
        start_time = None
        end_time = None

    if start_time is None and start_time != "":
        start_time = DateUtil.get_current_day()
    if end_time is None and end_time != "":
        end_time = start_time + timedelta(days=int(1))


    # Change the table and time condition based on the query
    curr_day = DateUtil.get_current_day()
    if filter_type_nev == "NEXT":
        curr_day = session['last_end_time'] + timedelta(days=int(1))
        start_time = curr_day
        end_time = curr_day + timedelta(days=int(1))
    elif filter_type_nev == "PREV":
        curr_day = session['last_start_date'] - timedelta(days=int(1))
        start_time = curr_day
        end_time = curr_day + timedelta(days=int(1))

    time_axis_format = '%d-%b(%H:%M)'
    _table = TABLE.IOT_AGG_15_MINUTES_SUMMARY_TABLE
    if filter_type == "WEEK":
        start_time, end_time = DateUtil.week_range(curr_day)
        _table = TABLE.IOT_AGG_1_HOUR_SUMMARY_TABLE
        time_axis_format = '%d-%b(%H:%M)'
    elif filter_type == "MONTH":
        start_time, end_time = DateUtil.month_range(curr_day)
        _table = TABLE.IOT_AGG_1_HOUR_SUMMARY_TABLE
        time_axis_format = '%d-%b(%H:%M)'
    elif filter_type == "YEAR":
        start_time, end_time = DateUtil.year_range(curr_day)
        _table = TABLE.IOT_AGG_1_HOUR_SUMMARY_TABLE
        time_axis_format = '%d-%b(%H:%M)'

    session['last_start_date'] = start_time
    session['last_end_time'] = end_time
    _condition = {"sender_timestamp": {"$gte": start_time, "$lte": end_time}, 'sensor_type': "DPM"}
    print(_condition)
    if filter_location_list and "ALL" not in filter_location_list:
        _condition.__setitem__('resource_path', {'$in': filter_location_list})

    _projection = {"sender_timestamp": 1, 'resource_path': 1, 'sensor_type': 1,
                   'AGGREGATE_VALUE': 1, 'irr_value': 1, 'performance_ratio': 1}

    _sortby = "sender_timestamp"
    print("search criteria ", _condition)
    print("Projection ", _projection)
    result = iot_dao.getrecord_from_table(_table, _condition, _projection, _sortby).reset_index()
    try:
        result['AGGREGATE_VALUE'] = result['AGGREGATE_VALUE'].replace([np.NaN, ''], 0).astype(np.float64).fillna(0.0)
        result['AGGREGATE_VALUE'] = round(result['AGGREGATE_VALUE'],2)
        result['irr_value'] = result['irr_value'].replace([np.NaN, ''], 0).astype(np.float64).fillna(0.0)
        result['irr_value'] = round(result['irr_value'], 2)
    except Exception as err:
        print(str(err))

    data_lst = []
    x = []
    y1 = []
    y2 = []
    location_detail = uti_service.get_location_details()
    agg = {"AGGREGATE_VALUE": 'sum', "irr_value": 'mean'}
    if not result.empty:
        result_4_grp = result[result['AGGREGATE_VALUE'] > 0]
        result_4_grp = result_4_grp.groupby(['sender_timestamp']).agg(agg).reset_index()
        for index, row in result_4_grp.iterrows():
            x.append(row['sender_timestamp'].strftime(time_axis_format))
            y1.append(round(row['AGGREGATE_VALUE'],2))
            y2.append(round(row['irr_value'],2))

        for index, row in result.iterrows():
            rw = {}
            rw.__setitem__('SENDER_TIMESTAMP', row['sender_timestamp'].strftime('%d-%m-%Y %H:%M'))
            rw.__setitem__('Location', row['resource_path'])
            rw.__setitem__('Location Code', location_detail[row['resource_path']]['location_code'])
            #rw.__setitem__('sensor_type', row['sensor_type'])
            rw.__setitem__('Energy (kWh)', row['AGGREGATE_VALUE'])
            # print(row['AGGREGATE_VALUE'])
            rw.__setitem__('Irradiance (W/m2)', row['irr_value'])
            data_lst.append(rw)


    loc_list = []
    for index, val in location_detail.items():
        val['selected'] = 'F'
        if filter_location_list:
            if (val['resource_path'] in filter_location_list):
                val['selected'] = 'Y'

        loc_list.append(val)

    plot_data, layout = polt_dashboard.rander_simplegraph(x_axies=x, y_axies_01=y1, y_label_01="kWh",title="Time Vs Energy")
    print(plot_data)
    print(layout)
    graphs = dict(data=plot_data, layout=layout)
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('sub_pages/common_template.html', pagename="dpm_energy_production",title="Energy Production",menu="menu_e_prod", data=data_lst,
                           location_detail=loc_list, req_param=req_param,filter_type=filter_type,
                           graphJSON=graphJSON,X=x,Y1=y1,Y2=y2,y1_lable="Energy (kWh)",y2_lable="Irradiance (W/m2)")



@Iot.route('/performance_ratio', methods=['GET', 'POST'])
def performance_ratio():
    print('performance_ratio')
    # Getting the form values
    filter_date = None
    filter_location_list = None
    filter_type = 'DAY'
    filter_type_nev = None
    try:
        filter_date = request.form['filter_date']
        filter_location_list = request.form.getlist('filter_location_list[]')
        filter_type = request.form['filter_type']
        filter_type_nev = request.form['filter_type_nev']
    except Exception as err:
        print(str(err))

    req_param = {'filter_date': filter_date, 'filter_location_list': filter_location_list}

    # Changing to the time format
    try:
        start_time = datetime.strptime(filter_date, '%d/%m/%Y')
        end_time = start_time + timedelta(days=int(1))
    except Exception as err:
        print(str(err))
        start_time = None
        end_time = None

    if start_time is None and start_time != "":
        start_time = DateUtil.get_current_day()
    if end_time is None and end_time != "":
        end_time = start_time + timedelta(days=int(1))


    # Change the table and time condition based on the query
    curr_day = DateUtil.get_current_day()
    if filter_type_nev == "NEXT":
        curr_day = session['last_end_time'] + timedelta(days=int(1))
        start_time = curr_day
        end_time = curr_day + timedelta(days=int(1))
    elif filter_type_nev == "PREV":
        curr_day = session['last_start_date'] - timedelta(days=int(1))
        start_time = curr_day
        end_time = curr_day + timedelta(days=int(1))

    time_axis_format = '%d-%b(%H:%M)'
    _table = TABLE.IOT_AGG_1_HOUR_SUMMARY_TABLE
    if filter_type == "WEEK":
        start_time, end_time = DateUtil.week_range(curr_day)
        _table = TABLE.IOT_AGG_1_HOUR_SUMMARY_TABLE
        time_axis_format = '%d-%b(%H:%M)'
    elif filter_type == "MONTH":
        start_time, end_time = DateUtil.month_range(curr_day)
        _table = TABLE.IOT_AGG_1_HOUR_SUMMARY_TABLE
        time_axis_format = '%d-%b-%Y'
    elif filter_type == "YEAR":
        start_time, end_time = DateUtil.year_range(curr_day)
        _table = TABLE.IOT_AGG_1_DAY_SUMMARY_TABLE
        time_axis_format = '%d-%b(%H:%M)'

    session['last_start_date'] = start_time
    session['last_end_time'] = end_time
    _condition = {"sender_timestamp": {"$gte": start_time, "$lte": end_time}, 'sensor_type': "DPM", "irr_value": {"$exists" : 'true'}}
    if filter_location_list and "ALL" not in filter_location_list:
        _condition.__setitem__('resource_path', {'$in': filter_location_list})

    _projection = {"sender_timestamp": 1, 'resource_path': 1, 'sensor_type': 1,
                   'AGGREGATE_VALUE': 1, 'irr_value': 1, 'performance_ratio': 1,'expected_value':1}

    _sortby = "sender_timestamp"
    print("search criteria ", _condition)
    print("Projection ", _projection)
    result = iot_dao.getrecord_from_table(_table, _condition, _projection, _sortby).reset_index()
    try:
        result['AGGREGATE_VALUE'] = result['AGGREGATE_VALUE'].replace([np.NaN, ''], 0).astype(np.float64).fillna(0.0)
        result['AGGREGATE_VALUE'] = round(result['AGGREGATE_VALUE'],2)
        result['performance_ratio'] = result['performance_ratio'].replace([np.NaN, ''], 0).astype(np.float64).fillna(0.0)
        result['performance_ratio'] = round(result['performance_ratio'], 2)
        result['irr_value'] = result['irr_value'].replace([np.NaN, ''], 0).astype(np.float64).fillna(0.0)
        result['irr_value'] = round(result['irr_value'], 2)
    except Exception as err:
        print(str(err))

    agg = {"AGGREGATE_VALUE": 'sum', "performance_ratio": 'mean'}
    location_detail = uti_service.get_location_details()
    data_lst = []
    x = []
    y1 = []
    y2 = []
    if not result.empty:
        result_4_grp = result[result['AGGREGATE_VALUE'] > 0]
        result_4_grp = result_4_grp.groupby(['sender_timestamp']).agg(agg).reset_index()
        for index, row in result_4_grp.iterrows():
            x.append(row['sender_timestamp'].strftime(time_axis_format))
            if row['performance_ratio'] > 100:
                row['performance_ratio'] = 100;
            y1.append(round(row['performance_ratio']))
            y2.append(row['AGGREGATE_VALUE'])

        for index, row in result.iterrows():
            rw = {}
            rw.__setitem__('SENDER_TIMESTAMP', row['sender_timestamp'].strftime('%d-%m-%Y %H:%M'))
            rw.__setitem__('Location', row['resource_path'])
            rw.__setitem__('Location Code', location_detail[row['resource_path']]['location_code'])
            #rw.__setitem__('sensor_type', row['sensor_type'])
            rw.__setitem__('Energy (kWh)', row['AGGREGATE_VALUE'])
            # print(row['AGGREGATE_VALUE'])
            rw.__setitem__('Irradiance (W/m2)', row['irr_value'])
            rw.__setitem__('Performance Ratio (%)', row['performance_ratio'])
            rw.__setitem__('Expected Energy (kWh)', row['expected_value'])


            data_lst.append(rw)


    loc_list = []
    for index, val in location_detail.items():
        val['selected'] = 'F'
        if filter_location_list:
            if (val['resource_path'] in filter_location_list):
                val['selected'] = 'Y'

        loc_list.append(val)

    plot_data, layout = polt_dashboard.rander_simplegraph(x_axies=x, y_axies_01=y1,y_label_01="PR (%)",y_axies_02=y2 ,y_label_02="Energy (kWh)",title="Time Vs performance_ratio",type_01="Scatter",type_02="Bar")
    print(plot_data)
    print(layout)
    graphs = dict(data=plot_data, layout=layout)
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('sub_pages/common_template.html', pagename="performance_ratio_summary",title="Performance Ratio",menu="menu_pr", data=data_lst,
                           location_detail=loc_list, req_param=req_param,filter_type=filter_type,
                           graphJSON=graphJSON,X=x,Y1=y1,Y2=y2,y1_lable="Energy (kWh)",y2_lable="Performance Ratio (%)")






@Iot.route('/inverter_pr', methods=['GET', 'POST'])
def inverter_pr():
    print('inverter_pr')
    # Getting the form values
    filter_date = None
    filter_location_list = None
    filter_type = 'DAY'
    filter_type_nev = None
    try:
        filter_date = request.form['filter_date']
        filter_location_list = request.form.getlist('filter_location_list[]')
        filter_type = request.form['filter_type']
        filter_type_nev = request.form['filter_type_nev']
    except Exception as err:
        print(str(err))

    req_param = {'filter_date': filter_date, 'filter_location_list': filter_location_list}

    # Changing to the time format
    try:
        start_time = datetime.strptime(filter_date, '%d/%m/%Y')
        end_time = start_time + timedelta(days=int(1))
    except Exception as err:
        print(str(err))
        start_time = None
        end_time = None

    if start_time is None and start_time != "":
        start_time = DateUtil.get_current_day()
    if end_time is None and end_time != "":
        end_time = start_time + timedelta(days=int(1))


    # Change the table and time condition based on the query
    curr_day = DateUtil.get_current_day()
    if filter_type_nev == "NEXT":
        curr_day = session['last_end_time'] + timedelta(days=int(1))
        start_time = curr_day
        end_time = curr_day + timedelta(days=int(1))
    elif filter_type_nev == "PREV":
        curr_day = session['last_start_date'] - timedelta(days=int(1))
        start_time = curr_day
        end_time = curr_day + timedelta(days=int(1))

    time_axis_format = '%d-%b(%H:%M)'
    _table = TABLE.IOT_AGG_1_HOUR_SUMMARY_TABLE
    if filter_type == "WEEK":
        start_time, end_time = DateUtil.week_range(curr_day)
        _table = TABLE.IOT_AGG_1_HOUR_SUMMARY_TABLE
        time_axis_format = '%d-%b(%H:%M)'
    elif filter_type == "MONTH":
        start_time, end_time = DateUtil.month_range(curr_day)
        _table = TABLE.IOT_AGG_1_HOUR_SUMMARY_TABLE
        time_axis_format = '%d-%b-%Y'
    elif filter_type == "YEAR":
        start_time, end_time = DateUtil.year_range(curr_day)
        _table = TABLE.IOT_AGG_1_HOUR_SUMMARY_TABLE
        time_axis_format = '%d-%b(%H:%M)'

    session['last_start_date'] = start_time
    session['last_end_time'] = end_time
    _condition = {"sender_timestamp": {"$gte": start_time, "$lte": end_time}, 'sensor_type': "INVERTER",
                  "irr_value": {"$exists" : 'true'}}
    if filter_location_list and "ALL" not in filter_location_list:
        _condition.__setitem__('resource_path', {'$in': filter_location_list})

    _projection = {"sender_timestamp": 1, 'resource_path': 1, 'sensor_id': 1,
                   'AGGREGATE_VALUE': 1, 'performance_ratio': 1,'expected_value':1}

    print("search criteria ", _condition)
    print("Projection ", _projection)
    result = iot_dao.getrecord_from_table(_table, _condition, _projection,_sortby='resource_path').reset_index()
    try:
        result['AGGREGATE_VALUE'] = result['AGGREGATE_VALUE'].replace([np.NaN, ''], 0).astype(np.float64).fillna(0.0)
        result['AGGREGATE_VALUE'] = round(result['AGGREGATE_VALUE'],2)
        result['performance_ratio'] = result['performance_ratio'].replace([np.NaN, ''], 0).astype(np.float64).fillna(0.0)
        result['performance_ratio'] = round(result['performance_ratio'], 2)
    except Exception as err:
        print(str(err))

    agg = {"AGGREGATE_VALUE": 'sum', "performance_ratio": 'mean'}
    location_detail = uti_service.get_location_details()
    data_lst = []
    x = []
    y1 = []
    y2 = []
    if not result.empty:
        result_4_grp = result[result['AGGREGATE_VALUE'] > 0]
        result_4_grp = result_4_grp.groupby(['sensor_id']).agg(agg).reset_index()
        result_4_grp = result_4_grp.sort_values(['AGGREGATE_VALUE'], ascending=[True])
        for index, row in result_4_grp.iterrows():
            x.append(row['sensor_id'])
            if row['performance_ratio'] > 100:
                row['performance_ratio'] = 100;
            y1.append(round(row['performance_ratio']))
            y2.append(round(row['AGGREGATE_VALUE'],2))

        for index, row in result.iterrows():
            rw = {}
            rw.__setitem__('SENDER_TIMESTAMP', row['sender_timestamp'].strftime('%d-%m-%Y %H:%M'))
            rw.__setitem__('Location', row['resource_path'])
            rw.__setitem__('Location Code', location_detail[row['resource_path']]['location_code'])
            rw.__setitem__('sensor_id', row['sensor_id'])
            rw.__setitem__('Energy (kWh)', row['AGGREGATE_VALUE'])
            rw.__setitem__('Performance Ratio (%)', row['performance_ratio'])


            data_lst.append(rw)


    loc_list = []
    for index, val in location_detail.items():
        val['selected'] = 'F'
        if filter_location_list:
            if (val['resource_path'] in filter_location_list):
                val['selected'] = 'Y'

        loc_list.append(val)

    plot_data, layout = polt_dashboard.rander_simplegraph(x_axies=x, y_axies_01=y1,y_label_01="PR (%)",y_axies_02=y2 ,y_label_02="Energy (kWh)",title="Time Vs performance_ratio",type_01="Scatter",type_02="Bar")
    print(plot_data)
    print(layout)
    graphs = dict(data=plot_data, layout=layout)
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('sub_pages/common_template.html', pagename="inv_performance_ratio_summary",title="Inverter Performance Ratio",menu="menu_pr", data=data_lst,
                           location_detail=loc_list, req_param=req_param,filter_type=filter_type,
                           graphJSON=graphJSON,X=x,Y1=y1,Y2=y2,y1_lable="Energy (kWh)",y2_lable="Performance Ratio (%)")





@Iot.route('/inv_energy__gen', methods=['GET', 'POST'])
def inv_energy__gen():
    print('inv_energy__gen')
    # Getting the form values
    filter_date = None
    filter_location_list = None
    filter_type = 'DAY'
    filter_type_nev = None
    try:
        filter_date = request.form['filter_date']
        filter_location_list = request.form.getlist('filter_location_list[]')
        filter_type = request.form['filter_type']
        filter_type_nev = request.form['filter_type_nev']
    except Exception as err:
        print(str(err))

    req_param = {'filter_date': filter_date, 'filter_location_list': filter_location_list}

    # Changing to the time format
    try:
        start_time = datetime.strptime(filter_date, '%d/%m/%Y')
        end_time = start_time + timedelta(days=int(1))
    except Exception as err:
        print(str(err))
        start_time = None
        end_time = None

    if start_time is None and start_time != "":
        start_time = DateUtil.get_current_day()
    if end_time is None and end_time != "":
        end_time = start_time + timedelta(days=int(1))


    # Change the table and time condition based on the query
    curr_day = DateUtil.get_current_day()
    if filter_type_nev == "NEXT":
        curr_day = session['last_end_time'] + timedelta(days=int(1))
        start_time = curr_day
        end_time = curr_day + timedelta(days=int(1))
    elif filter_type_nev == "PREV":
        curr_day = session['last_start_date'] - timedelta(days=int(1))
        start_time = curr_day
        end_time = curr_day + timedelta(days=int(1))

    time_axis_format = '%d-%b(%H:%M)'
    _table = TABLE.IOT_AGG_1_HOUR_SUMMARY_TABLE
    if filter_type == "WEEK":
        start_time, end_time = DateUtil.week_range(curr_day)
        _table = TABLE.IOT_AGG_1_HOUR_SUMMARY_TABLE
        time_axis_format = '%d-%b(%H:%M)'
    elif filter_type == "MONTH":
        start_time, end_time = DateUtil.month_range(curr_day)
        _table = TABLE.IOT_AGG_1_HOUR_SUMMARY_TABLE
        time_axis_format = '%d-%b-%Y'
    elif filter_type == "YEAR":
        start_time, end_time = DateUtil.year_range(curr_day)
        _table = TABLE.IOT_AGG_1_HOUR_SUMMARY_TABLE
        time_axis_format = '%d-%b(%H:%M)'

    session['last_start_date'] = start_time
    session['last_end_time'] = end_time
    _condition = {"sender_timestamp": {"$gte": start_time, "$lte": end_time}, 'sensor_type': "INVERTER",
                  "irr_value": {"$exists" : 'true'}}
    if filter_location_list and "ALL" not in filter_location_list:
        _condition.__setitem__('resource_path', {'$in': filter_location_list})

    _projection = {"sender_timestamp": 1, 'resource_path': 1, 'sensor_id': 1,
                   'AGGREGATE_VALUE': 1, 'performance_ratio': 1,'expected_value':1}

    print("search criteria ", _condition)
    print("Projection ", _projection)
    result = iot_dao.getrecord_from_table(_table, _condition, _projection,_sortby='resource_path').reset_index()
    try:
        result['AGGREGATE_VALUE'] = result['AGGREGATE_VALUE'].replace([np.NaN, ''], 0).astype(np.float64).fillna(0.0)
        result['AGGREGATE_VALUE'] = round(result['AGGREGATE_VALUE'],2)
        result['performance_ratio'] = result['performance_ratio'].replace([np.NaN, ''], 0).astype(np.float64).fillna(0.0)
        result['performance_ratio'] = round(result['performance_ratio'], 2)
    except Exception as err:
        print(str(err))

    agg = {"AGGREGATE_VALUE": 'sum', "performance_ratio": 'mean'}
    location_detail = uti_service.get_location_details()
    data_lst = []

    graph_set = []
    common_x = []
    max_y = 10
    if not result.empty:
        #result_4_grp = result[result['AGGREGATE_VALUE'] > 0]
        result_4_grp = result.groupby(['sender_timestamp','sensor_id']).agg(agg).reset_index()
        result_4_grp = result_4_grp.sort_values(['sender_timestamp'], ascending=[True])




        sensor_id_list = []
        summary = []
        for sensor_id in result_4_grp['sensor_id'].unique():
            sensor_id_list.append(sensor_id)
            x = []
            y = []
            result_4_grp_tmp = result_4_grp[result_4_grp['sensor_id'] == sensor_id]
            print("sensor_id    ", sensor_id)
            summary_info = {}
            max = 0
            sum = 0
            min = 1000
            for index, row in result_4_grp_tmp.iterrows():
                print(index)
                x.append(row['sender_timestamp'].strftime('%d-%m-%Y %H:%M'))
                y.append(round(row['AGGREGATE_VALUE'],2))
                sum = sum + round(row['AGGREGATE_VALUE'],2)
                if max < round(row['AGGREGATE_VALUE'],2):
                    max = round(row['AGGREGATE_VALUE'],2)
                if row['AGGREGATE_VALUE'] != 0 and min > round(row['AGGREGATE_VALUE'],2):
                    min = row['AGGREGATE_VALUE']
                if max_y < row['AGGREGATE_VALUE']:
                    max_y = round(row['AGGREGATE_VALUE'])

            summary_info.__setitem__('sensor_id', sensor_id)
            summary_info.__setitem__('max_energy', round(max,2))
            if min == 1000:
                min = 0
            summary_info.__setitem__('min_energy', round(min,2))
            summary_info.__setitem__('energy_gen', round(sum,2))
            summary.append(summary_info)


            if len(common_x) < len(x):
                common_x = x;
            gp = {'X':x,'Y':y,'label':sensor_id,'type':'line'}
            print(gp)
            graph_set.append(gp)

        asert_info_tmp = iot_dao.getJSON_LISTrecord_from_table(TABLE.IOT_ASSET_MSTR,{"sensor_id": {'$in': sensor_id_list}}, {"asset_name":1,"resource_path":1,"asset_capacity":1,"asset_location":1,"asset_desc":1,"sensor_id":1,"sensor_type":1,"model":1,"module_efficiency":1,"serial_no":1,"total_panel_area":1,"vendor_detail":1},None)
        asert_info =[]
        for row in asert_info_tmp:
            rw = {}
            rw.__setitem__('Device Id', row['sensor_id'])
            rw.__setitem__('Location', row['resource_path'])
            rw.__setitem__('model', row['model'])
            rw.__setitem__('Device Name', row['asset_name'])
            rw.__setitem__('Device Desc', row['asset_desc'])
            rw.__setitem__('Total PV Area (SQM)', row['total_panel_area'])
            rw.__setitem__('Capacity (kWp)', row['asset_capacity'])

            asert_info.append(rw)


        for index, row in result.iterrows():
            rw = {}
            rw.__setitem__('SENDER_TIMESTAMP', row['sender_timestamp'].strftime('%d-%m-%Y %H:%M'))
            rw.__setitem__('Location', row['resource_path'])
            rw.__setitem__('Location Code', location_detail[row['resource_path']]['location_code'])
            rw.__setitem__('sensor_id', row['sensor_id'])
            rw.__setitem__('Energy (kWh)', row['AGGREGATE_VALUE'])
            rw.__setitem__('Performance Ratio (%)', row['performance_ratio'])


            data_lst.append(rw)


    loc_list = []
    for index, val in location_detail.items():
        val['selected'] = 'F'
        if filter_location_list:
            if (val['resource_path'] in filter_location_list):
                val['selected'] = 'Y'

        loc_list.append(val)

    print(max_y)
    return render_template('sub_pages/common_template.html', pagename="inv_energy_gen_summary",title="Inverter Energy Generation",menu="menu_pr", data=data_lst,
                           location_detail=loc_list, req_param=req_param,filter_type=filter_type,
                           graph_set=graph_set,X_axies=common_x,max_y=max_y,info=asert_info,summary=summary)



