import logging
import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split

LOG = logging.getLogger(__file__)

Y_COL = 'ACCEPTED_OR_REJECTED'

# read data
df = pd.read_csv("/opt/ml/processing/input/result.csv")

#split data
#TODO: get ratios from args
y = df[Y_COL]
X = df.drop(columns=[Y_COL])

X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, random_state=42)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)

LOG.info(f"Training set size: {len(X_train)}")
LOG.info(f"Validation set size: {len(X_val)}")
LOG.info(f"Testing set size: {len(X_test)}")

train_df = X_train
train_df[Y_COL] = y_train

test_df = X_test
test_df[Y_COL] = y_test

val_df = X_val
val_df[Y_COL] = y_val

# save to disk
SAVE_PATH = "/opt/ml/processing/output/"

train_df.to_csv(os.path.join(SAVE_PATH, 'train.csv'))
test_df.to_csv(os.path.join(SAVE_PATH, 'test.csv'))
val_df.to_csv(os.path.join(SAVE_PATH, 'val.csv'))

LOG.info(f"data saved to {SAVE_PATH}")