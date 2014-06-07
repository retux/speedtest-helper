speedtest-helper are a set of scripts which run with speedtest-cli (https://github.com/sivel/speedtest-cli).

speedtst-hist.py read data from its stdin (sent from speedtest-cli) and stores download and upload speeds
as well as a timestamp and a few more data to csv file or sqlite3 database.
See speedtst-hist.py --help for options.

example:

speedtest-cli | speedtst-hist.py -w /var/speedstats/historytest.csv

or:

speedtest-cli | speedtst-hist.py --write=/var/speedstats/historytest.csv

This both ways data are appended to defined csv file.


speedtest-cli | speedtst-hist.py -s /var/speedstats/historytest.sql

This way data will be stored in a sqlite database.

Soon a second script will allow to make graph, using gnuplot. Coming soon.


Dependencies:
	python
	sqlite3
	speedtest-cli (https://github.com/sivel/speedtest-cli).

