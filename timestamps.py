#!/usr/bin/env python3
import argparse
import os
import re
import sys
from collections import OrderedDict

from enum import Enum, auto
from pathlib import Path

class Column(Enum):
    FILENAME = auto()
    FIRST = auto()
    LAST = auto()
def main(args):
    parser = argparse.ArgumentParser(description='Print first and last timestamp from log files')
    parser.add_argument('-f' ,'--format', required=False , help='Timestamp format regex')
    parser.add_argument('-s', '--sort', required=False, help='Sort order: FILENAME (default), FIRST, or LAST')
    parser.add_argument('file', nargs='+', help='log file')
    args = parser.parse_args()

    sort_order = Column.FILENAME
    timestamp_format = r"([\d-]{10})\s([\d:,]{12})" # YYYY-MM-DD HH:mm:ss,sss

    if args.sort:
        if args.sort in Column.__members__:
            if args.sort == Column.FILENAME.name:
                sort_order = Column.FILENAME
            elif args.sort == Column.FIRST.name:
                sort_order = Column.FIRST
            elif args.sort == Column.LAST.name:
                sort_order = Column.LAST
        else:
            raise Exception('Invalid sort order. Use: FILENAME, FIRST, or LAST')
    if args.format:
        pass
        #TODO - Allow the timestamp regex to be changed
        #timestamp_format = args.format

    results = dict()

    for file in args.file:
        if os.path.isfile(file):
            file_path = Path(file)
            file_open = open(file_path, "r")
            results[file] = get_timestamps(file_open, timestamp_format)

    final_results = sort_by(results, sort_order)

    print_timestamps(final_results)

def get_timestamps(file, regex) -> list:
    timestamps = [get_first_timestamp(file, regex), get_last_timestamp(file, regex)]
    return timestamps
def get_first_timestamp(file, regex) -> str:
    first = ''
    for line in file:
        match = re.search(regex, line)
        if match:
            first = match.group(0)
            break
    return first

def get_last_timestamp(file, regex) -> str:
    last = ''
    for line in file:
        match = re.search(regex, line)
        if match:
            last = match.group(0)
    return last

def sort_by(results, column):
    if column == Column.FIRST:
        sorted_results = OrderedDict(sorted(results.items(), key=lambda kv: (kv[1][0], kv[0])))
    elif column == Column.LAST:
        sorted_results = OrderedDict(sorted(results.items(), key=lambda kv: (kv[1][1], kv[0])))
    else:
        # Default behavior
        sorted_results = OrderedDict(sorted(results.items()))
    return sorted_results

def print_timestamps(results):
    file_length = longest(results, 'file')
    first_length = longest(results, 'first')
    last_length = longest(results, 'last')
    template = '{0:<' + str(file_length) + '}   {1:<' + str(first_length) + '}   {2:<' + str(last_length) + '}'

    print(template.format('FILENAME', 'FIRST', 'LAST'))

    for k, v in results.items():
        file = k
        first = v[0]
        last = v[1]
        print(template.format(file, first, last))

def longest(results, field) -> int:
    max_length = 0
    for k, v in results.items():
        if field == 'file':
            length = len(k)
        elif field == 'first':
            length = len(v[0])
        elif field == 'last':
            length = len(v[1])
        else:
            break
        if length > max_length:
            max_length = length
    return max_length


if __name__ == '__main__':
    main(sys.argv)