from pprint import pprint

import sklearn.metrics

import autosklearn.regression
from settings import CORR_GROUP, INFLUXDB_PASSWORD, INFLUXDB_DATABASE, INFLUXDB_HOST, INFLUXDB_PORT, INFLUXDB_USERNAME
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import logging

from influxdb import InfluxDBClient

if __name__ == '__main__':
    db_client = InfluxDBClient(
        host=INFLUXDB_HOST,
        port=INFLUXDB_PORT,
        username=INFLUXDB_USERNAME, 
        password=INFLUXDB_PASSWORD,
        database=INFLUXDB_DATABASE)

    query_api = db_client.get_list_measurements()
    print(query_api)

    #automl = autosklearn.regression.AutoSklearnRegressor(
    #        time_left_for_this_task=4*3600,
    #        per_run_time_limit=1200,
    #        tmp_folder='./tmp/autosklearn_regression_'+k+'_tmp',
    #    )