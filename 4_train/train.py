import argparse
import logging
import os
import pickle as pkl

import xgboost as xgb

LOG = logging.getLogger()
LOG.addHandler(logging.StreamHandler())
LOG.setLevel(logging.INFO)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # Hyperparameters are described here
    parser.add_argument("--num_round", type=int)
    parser.add_argument("--max_depth", type=int)
    parser.add_argument("--eta", type=float)
    parser.add_argument("--objective", type=str)
    parser.add_argument("--gamma", type=int)

    # SageMaker specific arguments. Defaults are set in the environment variables.
    parser.add_argument("--model_dir", type=str, default=os.environ.get("SM_MODEL_DIR"))
    parser.add_argument("--train", type=str, default=os.environ["SM_CHANNEL_TRAIN"])

    args = parser.parse_args()

    train_hp = {
        "max_depth": args.max_depth,
        "eta": args.eta,
        "gamma": args.gamma,
        "objective": args.objective,
    }

    dtrain = xgb.DMatrix(args.train)
    watchlist = [(dtrain, "train")]

    bst = xgb.train(
        params=train_hp,
        dtrain=dtrain,
        evals=watchlist,
        num_boost_round=args.num_round,
    )

    # Save the model to the location specified by ``model_dir``
    model_location = args.model_dir + "/xgboost-model"
    pkl.dump(bst, open(model_location, "wb"))
    LOG.info(f"Stored trained model at {model_location}")