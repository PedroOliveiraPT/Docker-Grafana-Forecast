#!/bin/bash

python3 get_training_data.py

for i in {'P_SUM', 'U_L1_N','I_SUM','H_TDH_I_L3_N','F','ReacEc_L1','C_phi_L3','ReacEc_L3','RealE_SUM','H_TDH_U_L2_N'}
do
    python3 model_training.py $i
    sleep 5
done