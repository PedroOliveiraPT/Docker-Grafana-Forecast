import statsd
from time import sleep
from random import randint, choice
import pandas as pd
import tensorflow as tf

from settings import CORR_GROUP, AD_THRESHOLD, PRED_MODELS
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import pickle
from influxdb import InfluxDBClient


c = statsd.StatsClient('localhost', 8125, prefix='performance')
db_client = InfluxDBClient(host="127.0.0.1",port=8086, username="", password="", database='influxdb-1')

#read models
models = {}
for var in PRED_MODELS:
    models = pickle.load(open('model/'+PRED_MODELS[var], 'rb'))

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