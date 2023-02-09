from random import randint, choice
import pandas as pd
import tensorflow as tf

from settings import CORR_GROUP, PRED_MODELS, INFLUXDB_DATABASE, INFLUXDB_HOST, INFLUXDB_PASSWORD, INFLUXDB_PORT, INFLUXDB_USERNAME, WORKING_DIR
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import pickle
from influxdb import InfluxDBClient
import joblib
import iso8601
from datetime import datetime, timedelta
import time
import daemon

import logging

def ad_program():
    db_client = InfluxDBClient(
        host=INFLUXDB_HOST,
        port=INFLUXDB_PORT, 
        username=INFLUXDB_USERNAME, 
        password=INFLUXDB_PASSWORD, 
        database=INFLUXDB_DATABASE
    )

    scalers = {var:joblib.load(f'scalers/{var}.scale') for var in CORR_GROUP}
    last_ts = list(db_client.query('select last(*) from P_SUM'))[0][0]['time']
    current_values = db_client.query(f'select last(value) from {",".join(CORR_GROUP.keys())}')
    last_ts = datetime.strptime(last_ts, "%Y-%m-%dT%H:%M:%S.%fZ")
    rounded_last_ts = last_ts - timedelta(minutes=last_ts.minute % 10,
                                            seconds=last_ts.second,
                                            microseconds=last_ts.microsecond)
    forward_ts = rounded_last_ts + timedelta(minutes=1)
    forecasted_values = db_client.query(f'select last(value) from \"{",".join(CORR_GROUP.keys())}\" where time <= \'{forward_ts}\' and time >= \'{rounded_last_ts}\'')
    points = []
    for var in CORR_GROUP:
        current_var_list = list(current_values.get_points(var))
        fc_var_list = list(forecasted_values.get_points(var))
        if len(current_var_list) > 0 and len(fc_var_list) > 0:
            curr_var_val = np.array(current_var_list[0]['last']).reshape(1,1)
            fc_var_val = np.array(current_var_list[0]['last']).reshape(1,1)
            scaled_curr_val = scalers[var].transform(curr_var_val)
            scaled_fr_val = scalers[var].transform(fc_var_val)
            diff = np.abs(scaled_curr_val - scaled_fr_val)[0][0]
            points.append({
                "measurement": f"{var} Difference",
                "time": last_ts,
                "fields": {"value": diff}
            })
    logging.info(db_client.write_points(points))

def prediction_program():
    db_client = InfluxDBClient(
        host=INFLUXDB_HOST,
        port=INFLUXDB_PORT, 
        username=INFLUXDB_USERNAME, 
        password=INFLUXDB_PASSWORD, 
        database=INFLUXDB_DATABASE
    )
    # Get Last Timestamp, remove when deploying
    last_ts = list(db_client.query('select * from P_SUM GROUP BY * ORDER BY desc LIMIT 1'))[0][0]['time']

    #uncomment when deploying
    #last_ts = 'now()'

    #read models
    points = []
    for var in PRED_MODELS:
        forecast_ts = iso8601.parse_date(last_ts) + timedelta(minutes=1)
        input_vector = []
        for needed_var in CORR_GROUP[var]:
            rs = db_client.query(f"select mean(value) from {needed_var} WHERE time > '{last_ts}' - 14m and time < '{last_ts}'group by time(1m)")
            var_scaler = joblib.load(f'scalers/{needed_var}.scale')
            x = np.array([i['mean'] for i in rs.get_points(needed_var)]).reshape(-1, 1)
            input_vector.append(var_scaler.transform(x))

        tensor = np.array(input_vector).transpose().reshape(-1, 15*len(CORR_GROUP[var]))
        
        model = pickle.load(open('models/'+PRED_MODELS[var], 'rb'))
        result = model.predict(tensor)
        var_scaler = joblib.load(f'scalers/{var}.scale')
        result = var_scaler.inverse_transform(result.reshape(-1,1))
        for r in result:
            points.append({
                "measurement": f"{var} Forecast",
                "time": forecast_ts.isoformat(),
                "fields": {"value": r[0]}
            })
            forecast_ts = forecast_ts + timedelta(minutes=1)
        
    logging.info(db_client.write_points(points))

def run():
    logging.basicConfig(filename='forecaster.log', format='%(asctime)s %(message)s', level=logging.DEBUG)

    logging.info('Forecasting agent started')
    while True:
        main_program()
        time.sleep(50)

if __name__ == '__main__':
    with daemon.DaemonContext(chroot_directory=None, working_directory=WORKING_DIR) as context:
        run()
