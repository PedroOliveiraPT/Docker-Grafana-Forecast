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

forecast_ts = iso8601.parse_date(last_ts) + timedelta(minutes=1)
forecast_ts = forecast_ts.isoformat()

#read models
points = []
for var in PRED_MODELS:
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
    points.append({
        "measurement": f"{var} Forecast",
        "time": forecast_ts,
        "fields": {"value": var_scaler.inverse_transform(result.reshape(1,1))[0][0]}
    })
print(points)

print(db_client.write_points(points))

print('finished')
