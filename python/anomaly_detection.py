import statsd
from time import sleep
from random import randint, choice
import pandas as pd
import tensorflow as tf

from settings import CORR_GROUP, AD_THRESHOLD, PRED_MODELS, INFLUXDB_DATABASE, INFLUXDB_HOST, INFLUXDB_PASSWORD, INFLUXDB_PORT, INFLUXDB_USERNAME
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import pickle
from influxdb import InfluxDBClient
import joblib
import iso8601
from datetime import datetime, timedelta

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
for var in PRED_MODELS:
    input_vector = []
    for needed_var in CORR_GROUP[var]:
        rs = db_client.query(f"select mean(value) from {needed_var} WHERE time > '{last_ts}' - 15m and time < '{last_ts}' -1m group by time(1m)")
        var_scaler = joblib.load(f'scalers/{needed_var}.scale')
        x = np.array([i['mean'] for i in rs.get_points(needed_var)]).reshape(-1, 1)
        input_vector.append(var_scaler.transform(x))

    tensor = np.array(input_vector).transpose().reshape(-1, 15*len(CORR_GROUP[var]))
    
    model = pickle.load(open('models/'+PRED_MODELS[var], 'rb'))
    result = model.predict(tensor)
    var_scaler = joblib.load(f'scalers/{var}.scale')

    current_value = np.array([i['value'] for i in db_client.query(f'select * from {var} GROUP BY * ORDER BY desc LIMIT 1').get_points(var)][0]).reshape(1, 1)
    scaled_cv = var_scaler.transform(current_value)
    print(abs(scaled_cv - result) > AD_THRESHOLD[var])

print('finished')
