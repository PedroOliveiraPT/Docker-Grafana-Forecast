CORR_GROUP = {
    'P_SUM': #Var to Predict
        ['S_SUM',
        'H_TDH_I_L1_N',
        'C_phi_L1',
        'P_L2',
        'P_L1',
        'P_L3',
        'C_phi_L2',
        'Q_SUM',
        'P_SUM',
        'Q_L2',
        'Q_L3',
        'Q_L1',
        'I_L1',
        'I_L2',
        'I_L3',
        'H_TDH_I_L2_N',
        'S_L3',
        'S_L2',
        'S_L1'],
    'U_L1_N':
        ['U_L1_L2', # Voltage L1_l2
        'U_L3_L1', # Voltage L3_l1
        'U_L3_N', # Voltage L3_N
        'U_L2_L3', # Voltage L2_l3
        'U_L2_N', # Voltage L2_N
        'U_L1_N'], # VOltage L1_N 
    'I_SUM': 
        ['I_SUM'], # Current Sum 
    'H_TDH_I_L3_N': 
        ['H_TDH_I_L3_N'],
    'F': 
        ['F'], # Measured Freq
    'ReacEc_L1': ['ReacEc_L1'],
    'C_phi_L3': ['C_phi_L3'],
    'ReacEc_L3': ['ReacEc_L3', 'ReacEc_SUM'],
    'RealE_SUM': ['ReacEc_L2',
    'ReacEi_SUM',
    'RealEc_SUM',
    'ReacEi_L1',
    'ReacEi_L3',
    'ReacEi_L2',
    'RealEc_L1',
    'RealEc_L2',
    'RealEc_L3',
    'RealE_L2',
    'RealE_L3',
    'RealE_L1',
    'AE_L1',
    'AE_L2',
    'AE_L3',
    'ReacE_L3',
    'ReacE_L2',
    'ReacE_L1',
    'RealE_SUM',
    'AE_SUM',
    'ReacE_SUM'],
    'H_TDH_U_L2_N': ['H_TDH_U_L2_N', 'H_TDH_U_L3_N', 'H_TDH_U_L1_N'],
    
}

PRED_MODELS = {
    'P_SUM': 'autosklearn_P_SUM',
    'U_L1_N': 'autosklearn_U_L1_N',
    'I_SUM': 'autosklearn_I_SUM',
    'H_TDH_I_L3_N': 'autosklearn_H_TDH_I_L3_N',
    'F': 'autosklearn_F',
    'ReacEc_L1': 'ReacEc_L1_model.sav',
    'RealE_SUM': 'ReacE_SUM_model.sav',
    'C_phi_L3': 'autosklearn_C_phi_L3',
    'ReacEc_L3': 'ReacEc_L3_model.sav',
    'H_TDH_U_L2_N': 'autosklearn_H_TDH_U_L2_N'
}

AD_THRESHOLD = {
    'P_SUM': 0.4,
    'U_L1_N': 0.1,
    'I_SUM': 0.3,
    'H_TDH_I_L3_N': 0.5,
    'F': 0.3,
    'ReacEc_L1': 0.3,
    'RealE_SUM': 0.3,
    'C_phi_L3': 0.3,
    'ReacEc_L3': 0.4,
    'H_TDH_U_L2_N': 0.3
}

INFLUXDB_DATABASE = 'influxdb-1'
INFLUXDB_USERNAME = ''
INFLUXDB_PASSWORD = ''
INFLUXDB_HOST = '127.0.0.1'
INFLUXDB_PORT = 8086