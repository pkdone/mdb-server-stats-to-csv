#!/usr/bin/env python3
##
# Gathers MongoDB database server statistics (especially WiredTiger statistics) over time and
# appends these to a CSV file. This script is useful where the MongoDB servers are remote and it
# is not possible to access the MongoDB servers' captured "Full Time Diagnostic Data Capture"
# (FTDC) statistics, which will be the case for end users leveraging the MongoDB Atlas DBaaS.
#
# Also see the MongoDB 't2' time series visualisation tool: https://github.com/10gen/t2
#
# For usage first ensure the '.py' script is executable and then run:
#   $ ./mongo-stats-to-csv.py -h
#
# Example (connecting to an Atlas cluster):
#   $ ./mongo-stats-to-csv -u mongodb+srv://mainuser:mypswd@testcluster-abcde.mongodb.net
##
import sys
import os
import time
import argparse
import contextlib
from datetime import datetime
from pymongo import MongoClient


# Core DB and WiredTiger server stats fields to log. For all possible loggable fields see MongoDB's
# "serverStatus" command https://docs.mongodb.com/manual/reference/command/serverStatus/
CORE_LOG_FIELDS = {
    'mem': ['resident', 'virtual']
}
WT_LOG_FIELDS = {
    'cache': ['bytes dirty in the cache cumulative', 'tracked dirty bytes in the cache',
              'tracked dirty pages in the cache', 'pages written requiring in-memory restoration',
              'pages selected for eviction unable to be evicted',
              'pages queued for urgent eviction'],
    'capacity': ['throttled bytes written for checkpoint', 'throttled bytes written for eviction',
                 'time waiting due to total capacity (usecs)',
                 'time waiting during checkpoint (usecs)',
                 'time waiting during eviction (usecs)'],
    'reconciliation': ['page reconciliation calls for eviction'],
    'thread-yield': ['application thread time evicting (usecs)', 'page acquire eviction blocked']
}


##
# Main function to gather stats and append to CSV file
##
def main():
    argparser = argparse.ArgumentParser(description='Logs DB & WiredTiger statistics periodically '
                                                    'to a local CSV file')
    argparser.add_argument('-u', '--url', default=DEFAULT_MONGODB_URL,
                           help=f'MongoDB Cluster URL (default: {DEFAULT_MONGODB_URL})')
    argparser.add_argument('-c', '--csvfile', default=DEFAULT_CSV_FILENAME,
                           help=f'Name of csv to log stats to (default: {DEFAULT_CSV_FILENAME})')
    argparser.add_argument('-p', '--period', default=DEFAULT_PERIODICITY_SECS, type=int,
                           help=f'The periodicity in seconds for polling for stats (default:'
                                f'{DEFAULT_PERIODICITY_SECS})')
    args = argparser.parse_args()
    print(f'Generating stats for: "{args.url}" to {args.csvfile}')

    with contextlib.suppress(FileNotFoundError):
        os.remove(args.csvfile)

    connection = MongoClient(host=args.url)
    db = connection['nodb']

    try:
        with open(args.csvfile, 'w') as f:
            f.write('datetime,')

            for category in CORE_LOG_FIELDS.keys():
                f.write(','.join([f'{category}_{key.replace(" ", "-")}'
                                  for key in CORE_LOG_FIELDS[category]]))
                f.write(',' if len(CORE_LOG_FIELDS[category]) > 0 else '')

            for category in WT_LOG_FIELDS.keys():
                f.write(','.join([f'{category}_{key.replace(" ", "-")}'
                                  for key in WT_LOG_FIELDS[category]]))
                f.write(',' if len(WT_LOG_FIELDS[category]) > 0 else '')

            f.write("\n")
            f.flush()

            while True:
                stats = db.command("serverStatus")
                wt_stats = stats['wiredTiger']
                f.write(f'{datetime.utcnow().isoformat()[:-3]}Z,')

                for category in CORE_LOG_FIELDS.keys():
                    f.write(','.join([str(stats[category][key])
                                      for key in CORE_LOG_FIELDS[category]]))
                    f.write(',' if len(CORE_LOG_FIELDS[category]) > 0 else '')

                for category in WT_LOG_FIELDS.keys():
                    f.write(','.join([str(wt_stats[category][key])
                                      for key in WT_LOG_FIELDS[category]]))
                    f.write(',' if len(WT_LOG_FIELDS[category]) > 0 else '')

                f.write("\n")
                f.flush()
                time.sleep(args.period)
    except KeyboardInterrupt:
        shutdown()


##
# Swallow the verbiage that is spat out when using 'Ctrl-C' to kill the script
##
def shutdown():
    print()

    try:
        sys.exit(0)
    except SystemExit as e:
        os._exit(0)


# Constants
DEFAULT_MONGODB_URL = 'mongodb://localhost:27017'
DEFAULT_CSV_FILENAME = 'dbstats.csv'
DEFAULT_PERIODICITY_SECS = 10


##
# Main
##
if __name__ == '__main__':
    main()
