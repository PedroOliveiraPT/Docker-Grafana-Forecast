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
        rs = db_client.query(f"select mean(value) from {needed_var} WHERE time > '{last_ts}' - 14m and time < '{last_ts}'group by time(1m)")
        input_vector.append([i['mean'] for i in rs.get_points(needed_var)])
    tensor = np.array(input_vector).transpose().reshape(-1, 15*len(CORR_GROUP[var]))
    
    model = pickle.load(open('models/'+PRED_MODELS[var], 'rb'))
    result = model.predict(tensor)
    print(result)

print('finished')

'''
while True:
    incr = randint( 1, 5 )
    timing = randint( 100, 400 )
    metric_type = choice(['A', 'B', 'C'])
    print( f"\radding metric: type: {metric_type}, incr: {incr}, timing {timing} ms", end="")
    c.incr(f'request.successful.count,type={metric_type}', incr)  # Increment counter
    c.timing(f'request.successful.time,type={metric_type}', timing )
    sleep( randint(5, 55) / 1000 )
'''