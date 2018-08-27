import csv
from optparse import OptionParser

import psycopg2

DATABASE = 'postgres'
USER = 'postgres'
PORT = 5432
PASSWORD = None

parser = OptionParser()
parser.add_option("-n", "--number",
                  default=20,
                  dest="limit",
                  help="Number of fetched slowest queries. Default: 20",
                  metavar="LIMIT")
parser.add_option("-d", "--database",
                  default=None,
                  dest="database",
                  help=("Database name. If incorrect or not found, "
                        "no filter on database. Default: None"),
                  metavar="DATABASE")
parser.add_option("-f", "--FILE",
                  default='output.csv',
                  dest="file",
                  help="Output file with extension. Default: output.csv",
                  metavar="FILE")

(options, _) = parser.parse_args()

conn = psycopg2.connect(
    database=DATABASE,
    user=USER,
    port=PORT,
    password=PASSWORD,
)
cur = conn.cursor()
cur.execute("SELECT current_setting('is_superuser')")

database_id = None
if options.database:
    query = ("SELECT oid FROM pg_database WHERE datistemplate = false"
             " AND datname = '{}';".format(options.database))
    cur.execute(query)
    ret = cur.fetchone()
    if ret:
        database_id = ret[0]
    else:
        print("ERROR: Database not found. "
              "No filter on database will be applied.")

if database_id:
    query = (
        "SELECT dbid, query, calls, mean_time, min_time, max_time, total_time, "
        "rows, 100.0 * shared_blks_hit / nullif(shared_blks_hit + "
        "shared_blks_read, 0) AS hit_percent FROM pg_stat_statements "
        "WHERE dbid = {} ORDER BY mean_time DESC LIMIT {}; ".format(
            database_id, options.limit)
    )
else:
    query = (
        "SELECT pgd.datname, pgss.query, pgss.calls, pgss.mean_time, "
        "pgss.min_time, pgss.max_time, pgss.total_time, pgss.rows, 100.0 * "
        "pgss.shared_blks_hit / nullif(pgss.shared_blks_hit + "
        "pgss.shared_blks_read, 0) AS hit_percent "
        "FROM pg_stat_statements as pgss "
        "JOIN pg_database as pgd ON datistemplate = false AND "
        "pgd.oid = pgss.dbid ORDER BY mean_time DESC LIMIT {}; ".format(
            options.limit)
    )

cur.execute(query)
slowest_queries = cur.fetchall()

with open(options.file, 'w', newline='') as output:
    csv_out = csv.writer(output)
    csv_out.writerow(
        ['database', 'query', 'calls', 'mean_time', 'min_time', 'max_time',
         'total_time', 'rows', 'hit_percent'])

    for q in slowest_queries:
        csv_out.writerow(
            [options.database if database_id else q[0], q[1], q[2], q[3], q[4],
             q[5], q[6], q[7], q[8]])

