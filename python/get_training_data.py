from settings import CORR_GROUP, INFLUXDB_PASSWORD, INFLUXDB_DATABASE, INFLUXDB_HOST, INFLUXDB_PORT, INFLUXDB_USERNAME, DATA_DIR
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler 
from influxdb import InfluxDBClient
import joblib

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

rs = db_client.query(f"select mean(value) from P_SUM WHERE time < '{last_ts}' group by time(1m)")
points = list(rs.get_points())
counter = 0
break_date = None
for i in range(len(points)-1, -1, -1):
    if points[i]['mean'] is None: 
        if counter == 0: break_date = points[i+1]["time"]
        counter += 1
        if counter > 5: break

for predictor in CORR_GROUP:
    pred_data = pd.DataFrame()
    pred_data_rs = None
    if break_date is None:
        pred_data_rs = db_client.query(f"select mean(value) from {','.join(CORR_GROUP[predictor])} WHERE time < '{last_ts}' group by time(1m)")
    else:
        pred_data_rs = db_client.query(f"select mean(value) from {','.join(CORR_GROUP[predictor])} WHERE time > '{break_date}' and time < '{last_ts}' group by time(1m)")
    
    if pred_data_rs is None: raise Exception('Query failed')
    for var in CORR_GROUP[predictor]:
        if len(pred_data.index) == 0:
            time_values = pred_data_rs.get_points(var)
            pred_data.index = [i['time'] for i in time_values]
        influx_values = pred_data_rs.get_points(var)
        scaler = MinMaxScaler()
        norm_influx_value = scaler.fit_transform(np.array([i['mean'] for i in influx_values]).reshape(-1, 1))
        joblib.dump(scaler, f'new_scalers/{var}.scale')
        pred_data[var] = norm_influx_value
    
    pred_data.to_csv(DATA_DIR + predictor + '.csv')