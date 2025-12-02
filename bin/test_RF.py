#!/usr/bin/env python3

import pickle
import argparse
import pandas as pd
import sys


def model_test(trained_model, test_data, predictions_file):
    df_test = pd.read_csv(test_data)

    print(df_test)
    loaded_model = pickle.load(open(trained_model, "rb"))

    # faire des prédictions en utilisant ce modèle
    predictions = loaded_model.predict(df_test.iloc[:, 1:].values)

    df=pd.DataFrame(predictions, columns=['class'])
    df.to_csv(predictions_file, index=False)
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test a final model")

    parser.add_argument("--m", required=True, type=str, help="the filename where the trained model is saved")
    parser.add_argument("--t", required=True, type=str, help="path to the test dataset")
    parser.add_argument("--f", required=True, type=str, help="name of the predictions filename")
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()
    args = parser.parse_args()
    # Test the model and generates predictions
    model_test(trained_model=args.m, test_data=args.t, predictions_file=args.f)
