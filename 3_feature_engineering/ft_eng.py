"""This is an example of a feature engineering script using a "managed" (AWS-provided) sklearn container

When we use xoml_sagemaker to do feature engineering, two things happen. First, we train and save a feature
transformer object as a sagemaker model. Next, we run a bulk "inference" job with that model to transform
all of the data. That means that our script needs to provide the functions that sagemaker expects to hook into
for both training and inference.
"""

import argparse
import json
import os
from io import StringIO

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

SAVE_MODEL_NAME = "transformer.joblib"
FEATURE_COLS = ['MACHINING_CENTER_SPACE_BBOX_X_MAX', 'MACHINING_CENTER_SPACE_BBOX_Y_MAX', 'MACHINING_CENTER_SPACE_BBOX_Z_MAX', 'LATHE_LENGTH', 'LATHE_RADIUS']
OTHER_COLS = ["ACCEPTED_OR_REJECTED"]
OUTPUT_COLS = ["PCA1", "PCA2", "ACCEPTED_OR_REJECTED"]

# === begin sagemaker framework code ===
# the 4 functions defined below, `model_fn`, `input_fn`, `predict_fn`, and `output_fn`
# are used by the sagemaker framework. you can edit them as appropriate for your model,
# but don't delete or rename them!

def model_fn(model_dir):
    """
    this function is called by the sagemaker framework during on-line or batch inference

    load the saved transformer from disk. this is used when we do batch transform
    or on-line inference. the sagemaker framework provides the model_dir input, which
    is the location where the model files have been downloaded.
    """
    transformer = joblib.load(os.path.join(model_dir, SAVE_MODEL_NAME))
    return transformer


def input_fn(input_data, content_type):
    """
    this function is called by the sagemaker framework during on-line or batch inference

    process the input passed to an endpoint or a bulk inference job. you might want
    to handle multiple input formats. for example, during training, we get input as
    "text/csv", but during online inference, we might receive "application/json".

    the output from this function should be suitable to be fed directly to `predict_fn`,
    defined below.
    """
    if content_type == "text/csv":
        # Read the raw input data as CSV.
        df = pd.read_csv(StringIO(input_data), header=0)[FEATURE_COLS+OTHER_COLS]
        return df
    elif content_type == "application/json":
        return json.loads(input_data)
    else:
        err_msg = f"unsupported input content_type for model: {content_type}"
        raise NotImplementedError(err_msg)


def predict_fn(input_data, model):
    """
    this function is called by the sagemaker framework during on-line or batch inference

    this function transforms data using the model object that's returned from `model_fn`
    and the data returned from `input_fn`.
    """
    t = model.transform(input_data)
    return np.array(t)


def output_fn(output_data, content_type):
    """
    this function is called by the sagemaker framework during on-line or batch inference

    post-process the output from predict_fn that will be returned from the endpoint
    or bulk inference job. you might want to handle multiple input formats. for example,
    during training, we get input as "text/csv", but during online inference, we might
    receive "application/json".
    """
    if content_type == "text/csv":
        """return csv, serialized as a str"""
        output = StringIO()
        df = pd.DataFrame(output_data, columns=OUTPUT_COLS)
        df.to_csv(output, index=False)
        return output.getvalue()
    elif content_type == "application/json":
        return json.dumps(output_data)
    else:
        err_msg = f"unsupported input content_type for model: {content_type}"
        raise NotImplementedError(err_msg)


# === end sagemaker stuff. everything below is the user script used to train the transformer. ===
#
# the framework downloads the files from the input s3 directory we specified
# into our training container, and we can read them from disk.
#
# all the framework requires is that save an object to disk in /opt/ml/model. we can
# save whatever we like there, as long as it can be deserialized by `model_fn`
#
# besides that, you can do anything you like.

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", type=str, default="/opt/ml/input/data/train")
    args = parser.parse_args()

    # read the training data from the input location
    df = pd.read_csv(os.path.join(args.train, "train.csv"))[FEATURE_COLS + OTHER_COLS]

    # we will scale + PCA our model features, and pass through the other features unchanged
    feature_transformations = Pipeline([("scaler", StandardScaler()), ("pca", PCA(n_components=2))])

    ct = ColumnTransformer(transformers=[("feat", feature_transformations, FEATURE_COLS)], remainder="passthrough")

    ct.fit(df)

    # sagemaker copies anything written to this directory to s3
    model_dir = "/opt/ml/model"
    os.makedirs(model_dir, exist_ok=True)
    joblib.dump(ct, os.path.join(model_dir, SAVE_MODEL_NAME))
