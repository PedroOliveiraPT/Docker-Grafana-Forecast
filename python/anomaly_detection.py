import pandas as pd
import tensorflow as tf

from settings import CORR_GROUP, AD_THRESHOLD, PRED_MODELS, INFLUXDB_DATABASE, INFLUXDB_HOST, INFLUXDB_PASSWORD, INFLUXDB_PORT, INFLUXDB_USERNAME, WORKING_DIR
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import pickle
from influxdb import InfluxDBClient
import joblib
from datetime import datetime, timedelta
import daemon
import time

import logging

db_client = InfluxDBClient(
    host=INFLUXDB_HOST,
    port=INFLUXDB_PORT, 
    username=INFLUXDB_USERNAME, 
    password=INFLUXDB_PASSWORD, 
    database=INFLUXDB_DATABASE
)

scalers = {var:joblib.load(f'scalers/{var}.scale') for var in CORR_GROUP}

def main_program():
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

def run():
    logging.basicConfig(filename='ad.log', format='%(asctime)s %(message)s', level=logging.DEBUG)

    logging.info('AD agent started')
    while True:
        main_program()
        time.sleep(10)

if __name__ == '__main__':
    with daemon.DaemonContext(chroot_directory=None, working_directory=WORKING_DIR):
        run()
