# log-start-end
Print the first and last timestamps in a log file.

## Usage
```commandline
usage: timestamps.py [-h] [-v] [-r REGEX] [-s SORT] file [file ...]

Print first and last timestamp from log files. Default: YYYY-MM-DD HH:mm:ss,sss

positional arguments:
  file                  log file

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Verbose output
  -r REGEX, --regex REGEX
                        Timestamp regex
  -s SORT, --sort SORT  Sort order: FILENAME (default), FIRST, or LAST
```

### Output
```
FILENAME      FIRST                     LAST
system1.log   2021-08-03 11:26:17,814   2021-08-03 14:13:31,642
system2.log   2022-10-10 06:50:47,147   2022-10-13 08:47:10,208
system3.log   2022-10-12 19:52:22,264   2022-10-15 18:24:33,522
system4.log   2022-10-13 02:30:10,772   2022-10-15 23:31:03,703
```