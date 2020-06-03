# MongoDB Server Statistics To CSV Project

Gathers MongoDB database server statistics (especially WiredTiger statistics) over time and appends these to a CSV file. The main Python script is useful where the MongoDB servers are remote and it is not possible to access the MongoDB servers' captured "Full Time Diagnostic Data Capture" ([FTDC](https://docs.mongodb.com/manual/administration/analyzing-mongodb-performance/#full-time-diagnostic-data-capture)) statistics, which used to  be the case for end users leveraging the [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) DBaaS. Also see the MongoDB [t2](https://github.com/10gen/t2) time series visualisation tool.

For usage first ensure the '.py' script is executable and then run:
```
./mongo-stats-to-csv.py -h
```

Example to connect to an Atlas cluster to collect statistics from:
```
./mongo-stats-to-csv -u mongodb+srv://mainuser:mypswd@testcluster-abcde.mongodb.net
```

To stop the collection of statistics to the CSV file just kill the Python script process, e.g. `Ctrl-C`.

Optionally, you can load the generated CSV file into a new collection in a new MongoDB database and then use [MongoDB Charts](https://www.mongodb.com/products/charts) to better visualise its contents. Example command to import the generated CSV into a MongoDB Atlas cluster using [mongoimport](https://docs.mongodb.com/manual/reference/program/mongoimport/):
```
mongoimport --host StatsCluster-shard-0/statscluster-shard-00-00-s703u.mongodb.net:27017,statscluster-shard-00-01-s703u.mongodb.net:27017,statscluster-shard-00-02-s703u.mongodb.net:27017 --ssl --username main_user --password Password1 --authenticationDatabase admin --parseGrace=skipRow --ignoreBlanks --drop --db dbstats --collection statdata --type csv --columnsHaveTypes --fields "datetime.date(2006-01-02T15:04:05.000Z),mem_resident.double(),mem_virtual.double(),cache_bytes-dirty-in-the-cache-cumulative.double(),cache_tracked-dirty-bytes-in-the-cache.double(),cache_tracked-dirty-pages-in-the-cache.double(),cache_pages-written-requiring-in-memory-restoration.double(),cache_pages-selected-for-eviction-unable-to-be-evicted.double(),cache_pages-queued-for-urgent-eviction.double(),capacity_throttled-bytes-written-for-checkpoint.double(),capacity_throttled-bytes-written-for-eviction.double(),capacity_time-waiting-due-to-total-capacity-(usecs).double(),capacity_time-waiting-during-checkpoint-(usecs).double(),capacity_time-waiting-during-eviction-(usecs).double(),reconciliation_page-reconciliation-calls-for-eviction.double(),thread-yield_application-thread-time-evicting-(usecs).double(),thread-yield_page-acquire-eviction-blocked.double()" --file dbstats.csv
```

To see the list of default MongoDB/WiredTiger statistics gathered and generated into the CSV file, view the declared list of fields variables near the top of the Python script file. These list variables can be changed by the user, directly in the script. For all possible loggable fields see MongoDB's [serverStatus](https://docs.mongodb.com/manual/reference/command/serverStatus/) command. If you change what is logged to the CSV file, you will need to change the fields listed in the example _mongoimport_ command above, if you intend to import the generated CSV file into a MongoDB database.

