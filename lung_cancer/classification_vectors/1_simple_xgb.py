import datetime
import logging
import os

import dill
import numpy as np
from xgboost.sklearn import XGBClassifier
from sklearn.metrics import log_loss, roc_auc_score

DATA_DIR = '../data/final/vectors/'
LOG_FILE = '../log/lung_cancer_vectors_simple_xgb.log'
N_JOBS = 30
N_ESTIMATORS = 2000

# Logging setup
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(message)s')


def exists_in_log_file(term):
    try:
        with open(LOG_FILE, 'r') as f:
            return (term in f.read())
    except:
        pass
    return False


data_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.dill')]

for data_file in data_files:
    if exists_in_log_file(data_file):
        # Skip if already trained and tested
        print('Skipping {}'.format(data_file))
        continue

    print('Training on {}'.format(data_file))

    # Loading data
    data = dill.load(open(os.path.join(DATA_DIR, data_file), 'rb'))

    for months_before in data.keys():
        train_x = data[months_before]["TRAIN"]["X"]
        train_y = data[months_before]["TRAIN"]["y"]
        test_x = data[months_before]["TEST"]["X"]
        test_y = data[months_before]["TEST"]["y"]

        neg_pos_ratio = (train_y.shape[0]-train_y.sum())/train_y.sum()

        # Creating and training model
        clf = XGBClassifier(n_estimators=N_ESTIMATORS, random_state=1,
                            verbose=1, n_jobs=N_JOBS, scale_pos_weight=neg_pos_ratio)

        # Creating and training model
        clf = XGBClassifier(n_estimators=N_ESTIMATORS,random_state=1,
                            verbose=1, n_jobs=N_JOBS)
        clf.fit(train_x, train_y, verbose=True)

        # Scoring
        pred_y = clf.predict_proba(test_x)

        auc_score = roc_auc_score(test_y, pred_y[:,1])
        log_score = log_loss(test_y, pred_y)

        logging.info('{}, {}, {}, {}'.format(data_file, months_before, auc_score, log_score))

import ipdb; ipdb.set_trace()
