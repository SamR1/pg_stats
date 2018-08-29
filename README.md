# pg_stats
simple script to export slowest queries on PostgreSQL database in csv file.

## Prerequisites

`pg_stat_statements` must be loaded (see [PostgreSQL documentation](https://www.postgresql.org/docs/10/static/pgstatstatements.html)).


## Usage

```shell
$ python pg_stats.py -h
Usage: pg_stats.py [options]

Options:
  -h, --help            show this help message and exit
  -n LIMIT, --number=LIMIT
                        Number of fetched slowest queries. Default: 20
  -d DATABASE, --database=DATABASE
                        Database name. If incorrect or not found, no filter on
                        database. Default: None
  -f FILE, --FILE=FILE  Output file with extension. Default: output.csv

```
