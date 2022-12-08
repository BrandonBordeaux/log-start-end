#!/usr/bin/env python3
import argparse
import mmap
import os
import re
import sys

from collections import OrderedDict
from enum import Enum, auto
from pathlib import Path

verbose = False


class Column(Enum):
    FILENAME = auto()
    FIRST = auto()
    LAST = auto()


def main(args):
    parser = argparse.ArgumentParser(description='Print first and last timestamp from log files')
    parser.add_argument('-v', '--verbose', action="store_true", help="Verbose output")
    parser.add_argument('-f', '--format', required=False, help='Timestamp format regex')
    parser.add_argument('-s', '--sort', required=False, help='Sort order: FILENAME (default), FIRST, or LAST')
    parser.add_argument('file', nargs='+', help='log file')
    args = parser.parse_args()

    sort_order = Column.FILENAME
    timestamp_format = re.compile(rb"([\d-]{10})\s([\d:,]{12})")  # YYYY-MM-DD HH:mm:ss,sss

    if args.verbose:
        global verbose
        verbose = True
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
        # TODO - Allow the timestamp regex to be changed
        # timestamp_format = args.format

    results = dict()

    for file in args.file:
        if os.path.isfile(file):
            results.update(parse_file(file, timestamp_format))

    print('Sorting....') if verbose else None
    final_results = sort_by(results, sort_order)

    print('Printing results...') if verbose else None
    print_timestamps(final_results)


def parse_file(file, timestamp_format) -> dict:
    if os.path.isfile(file):
        results = dict()
        file_path = Path(file)
        with open(file_path, "r") as file_open:
            with mmap.mmap(file_open.fileno(), length=0, access=mmap.ACCESS_READ) as file_mmap:
                results[file] = get_timestamps(file_mmap, timestamp_format)
        print('Finished: {}'.format(file)) if verbose else None
        return results


def get_timestamps(file, regex) -> list:
    timestamps = [get_first_timestamp(file, regex), get_last_timestamp(file, regex)]
    return timestamps


def get_first_timestamp(file, regex) -> str:
    first = ''
    for line in iter(file.readline, b""):
        match = regex.search(line)
        if match:
            first = match.group(0)
            break
    return first.decode()


def get_last_timestamp(file, regex) -> str:
    last = ''
    # Initialize starting position
    position = -2
    looking = True

    while looking:
        # Seek to position relative to EOF
        file.seek(position, os.SEEK_END)
        while file.read(1) != b"\n":
            # We're reading 1 byte to check for newline. If False, we go back 2 bytes. Overall we're stepping pos
            # by -1
            position += -1
            file.seek(-2, os.SEEK_CUR)

        # Increment position by 1 to move to the start of the next line.
        # We also need to seek relative to end of file as the while loop readline() advanced our position
        file.seek(position + 1, os.SEEK_END)
        match = regex.search(file.readline())
        if match:
            last = match.group(0)
            looking = False
        else:
            # Move the byte back one to avoid reading the same newline again, causing infinite loop
            position += -1
    return last.decode()


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
