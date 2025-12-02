#!/usr/bin/env python3

import argparse
import collections.abc
import json
from pathlib import Path
import re
import sys
from typing import List

"""Concatenate all json results into a single file
"""
def update(d, u):
    """Update a dictionnary with common keys.

    Source:
    """
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = update(d.get(k, {}), v)
        else:
            d[k] = v
    return d

def concat_files(files: List[Path], output_file: Path):
    total_file = {}
    for this_file in files:
        with open(this_file) as file_reader:
            json_data = json.load(file_reader)
            update(total_file, json_data)
    with open(output_file, "w") as file_writer:
        file_writer.write(json.dumps(total_file))

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-i", "--inputs", help="Path of files to concatenate", type=Path, nargs="+", required=True)
    arg_parser.add_argument("-o", "--output", help="Path of concatenated file", type=Path, required=True)

    if len(sys.argv) == 1:
        arg_parser.print_help()
        sys.exit(0)

    args = arg_parser.parse_args()
    concat_files(files=args.inputs, output_file=args.output)
