#!/usr/bin/env python3

import argparse
import json
from pathlib import Path
import re
import sys

import pandas as pd
import numpy as np
import sklearn.metrics as metrics

INDICATORS = ["accuracy", "f1_macro", "f1_micro", "precision_macro", "precision_micro", "recall_macro", "recall_micro"]

class AppError(Exception):
    """Handle errors in this script"""
    pass
class FilenameNotSupported(AppError):
    pass
class FileNotExist(AppError):
    pass

def verify_filename(input_file: Path) -> int:
    """Verify that the filename and return the associated index of the file.

    The filename should match .*_([0-9]+)$. The index is the number catched
    between parenthesis.
    Args:
        input_file: Path: Path of the file to verify
    Raises:
        AppError: If the file does not exist, or the filename does not match
            the pattern
    Return:
        int: The index of the file
    """
    if not input_file.exists():
        raise FileNotExist(f"{str(input_file)} does not exists")
    regex_match_file = re.compile(".*_([0-9]+)$")
    match_file = regex_match_file.search(input_file.name)
    if not match_file:
        raise FilenameNotSupported(f"The filename '{str(input_file)}' does not match the pattern {regex_match_file.pattern}")
    return int(match_file.group(1))


def calculate_indicators(true_labels: Path, predicted_labels: Path, filenameResults: Path, listIndicators, tag):

    df_true = pd.read_csv(true_labels)
    true_label=df_true.iloc[:,0].values
    df_true_label=pd.DataFrame(true_label)
   
    df_predicted = pd.read_csv(predicted_labels)
    filename_index = verify_filename(predicted_labels)


    dataJson = {}
    dataJson[filename_index] = []
    for indicator in listIndicators:
        if indicator == "accuracy":
            calculate_accuracy(df_true_label, df_predicted, indicator, metrics.accuracy_score, dataJson[filename_index])
        elif indicator == "f1_macro":
            calculate_indicator(df_true_label, df_predicted, 'macro', indicator, metrics.f1_score, dataJson[filename_index])
        elif indicator == "f1_micro":
            calculate_indicator(df_true_label, df_predicted, 'micro', indicator, metrics.f1_score, dataJson[filename_index])
        elif indicator == "precision_macro":
            calculate_indicator(df_true_label, df_predicted, 'macro', indicator, metrics.f1_score, dataJson[filename_index])
        elif indicator == "precision_micro":
            calculate_indicator(df_true_label, df_predicted, 'micro', indicator, metrics.f1_score, dataJson[filename_index])
        elif indicator == "recall_macro":
            calculate_indicator(df_true_label, df_predicted, 'macro', indicator, metrics.f1_score, dataJson[filename_index])
        elif indicator == "recall_micro":
            calculate_indicator(df_true_label, df_predicted, 'micro', indicator, metrics.f1_score, dataJson[filename_index])

    with open(filenameResults, "w") as outfile:
        data_json = {tag: dataJson}
        json.dump(data_json, outfile, indent=4)


def calculate_accuracy(true_df, predict_df, indicator, func, datadf):
    data = []
 
    computedindicator = func(true_df, predict_df)

    data.append([1, computedindicator])
    df_path = pd.DataFrame(data, columns=["predicted_labels", indicator])
    datadf.append({indicator: df_path[indicator].tolist()})


def calculate_indicator(true_df, predict_df, average, indicator, func, datadf):
    data = []
 
    computedindicator = func(true_df, predict_df, average=average)

    data.append([1, computedindicator])
    df_path = pd.DataFrame(data, columns=["predicted_labels", indicator])
    datadf.append({indicator: df_path[indicator].tolist()})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate  indicators")

    parser.add_argument("--r", "--reallabelFile", required=True, type=Path, help="File of real labels")
    parser.add_argument("--p", "--predictFile", required=True, type=Path, help="File of predictions")
    parser.add_argument("--f", required=True, type=Path, help="The name of the result file")
    parser.add_argument(
        "--i",
        action="store",
        choices=INDICATORS,
        dest="listparamsIndicators",
        type=str,
        nargs="*",
        default=[],
        help="List of indicators to calculate",
    )
    parser.add_argument("--tag", default="None", type=str, help="Tag to use in the output file like:\n\
    '{\"MY_TAG\": {\"...\": \"...\", \"...\": \"...\"}}. If no tag is provided, then the script will use the name of the predictFile")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()

    args=parser.parse_args()

    if not args.tag:
        if args.p.exist:
            args.tags = args.p.name

    try:
        calculate_indicators(
            true_labels=args.r, predicted_labels=args.p, filenameResults=args.f, listIndicators=args.listparamsIndicators, tag=args.tag
        )
    except AppError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
