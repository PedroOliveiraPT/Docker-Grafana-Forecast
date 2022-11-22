from pprint import pprint

import sklearn.metrics

import autosklearn.regression
from settings import PRED_MODELS, LINREG_LIST, CORR_GROUP, DATA_DIR
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import argparse
import pickle

def value_with_threshold(value):
    try:
        ivalue = int(value)
    except:
        raise argparse.ArgumentTypeError(value + ' is an invalid integer, the split division must be an integer between 50\% and 95%')
    if ivalue < 50 or ivalue > 95:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return ivalue

def create_supervised_dataset(df, target, feats, n_in=1, n_out=1):
    cols, names = list(), list()
    n_vars = len(feats)
    # input sequence (t-n, ... t-1)
    for i in range(n_in, 0, -1):
        cols.append(df[feats].shift(i))
        names += [('var%d(t-%d)' % (j+1, i)) for j in range(n_vars)]
    # forecast sequence (t, t+1, ... t+n)
    for i in range(0, n_out):
        cols.append(df[target].shift(-i))
        if i == 0:
            names += [('var%d(t)' % (j+1)) for j in range(1)]
        else:
            names += [('var%d(t+%d)' % (j+1, i)) for j in range(1)]
    # put it all together
    agg = pd.concat(cols, axis=1)
    agg.columns = names
    agg.dropna(inplace=True)
    return agg.values

if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog='ModelTraining', description='Program to train models as requested')
    parser.add_argument('model', choices=CORR_GROUP.keys(),
                        help='Pick which model to train')
    parser.add_argument('-t', '--time', type=int, default=60,
                        help='Time in minutes for how much time to spend on training, defaults at one hour')
    parser.add_argument('-i', '--input', type=int, default=15,
                        help='Input size, or History window, number of entries needed to make a forecast, defaults at 15mins')
    parser.add_argument('-o', '--output', type=int, default=1,
                        help='Output size, or Prediction Window, number of entries to forecast, defaults at 1')
    parser.add_argument('-s', '--split', default=90, type=value_with_threshold,
                        help='The split between training and test data for the training of the models')                   
    
    args = parser.parse_args()

    input_df = pd.read_csv(f'{DATA_DIR}{args.model}.csv', index_col='Unnamed: 0')
    values = create_supervised_dataset(input_df, args.model, CORR_GROUP[args.model], n_in=args.input, n_out=args.output)
    len_values = values.shape[0]
    # split into train and test sets 
    n_train_seconds = int(args.split/100*len_values) 
    n_test_seconds =  int(1*len_values) 
    train = values[:n_train_seconds, :]
    test = values[n_train_seconds:n_test_seconds, :]

    # split into input and outputs
    train_X, train_y = train[:, :-args.output], train[:, -args.output:]
    test_X, test_y = test[:, :-args.output], test[:, -args.output:]
    test_predictions = None
    if args.model in LINREG_LIST:
        linreg = LinearRegression().fit(train_X, train_y)
        pickle.dump(linreg, open(f'models/{PRED_MODELS[args.model]}', 'wb'))
        test_predictions = linreg.predict(test_X)
    else:
        automl = autosklearn.regression.AutoSklearnRegressor(
            time_left_for_this_task=60*args.time,
            per_run_time_limit=6*args.time,
            tmp_folder='./tmp/autosklearn_regression_'+args.model+'_tmp',
        )
        try:
            automl.fit(train_X, train_y, dataset_name=args.model)
            pickle.dump(automl, open('models/'+PRED_MODELS[args.model], 'wb'))
            test_predictions = automl.predict(test_X)
        except Exception:
            raise Exception
    with open(f'results/{args.model}.csv', 'w') as writer:
        for i in range(args.output):
            writer.write(f'y{i+1},{str(sklearn.metrics.mean_squared_error(test_y[:,i], test_predictions[:,i], squared=False))}')