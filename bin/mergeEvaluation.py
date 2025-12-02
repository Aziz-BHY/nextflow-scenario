import argparse
import json
from pathlib import Path


def merge_evaluationFiles(filename, outputFile):
    result = list()
    for f1 in filename:
        with open(f1, 'r') as infile:
            data = json.load(infile)
            result.append(data)

    with open(outputFile, 'w') as output_file:
        json.dump(result, output_file, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aggregate Results of all the algorithms in One File")
    parser.add_argument("--o", "--output", type=Path, help="Path of the final result file")
    parser.add_argument(
        "--r", "--results",
        action="store",
        help="Results of indicators evaluation to compile in json format. This option accept multiple files",
        dest="listparamsindicators",
        type=Path,
        nargs="*",
        default=[],
    )
    args = parser.parse_args()
    merge_evaluationFiles(args.listparamsindicators, args.o)