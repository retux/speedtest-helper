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
	python-magic
	speedtest-cli (https://github.com/sivel/speedtest-cli).	This script actually do the throuput
		metering. Its output is used to stored and create stats.


Usage examples:

./speedtst2plot.py -o /tmp/throuput.png -s speedtestdb.db3
                Uses sqlite3 db speedtestdb.db3 and creates graph at specified file.


./speedtst-hist.py -p speedtestdb.db3 | ./speedtst2plot.py --output=/tmp/throuput.png -i
                speedtst-hist.py dumps data store at speedtestdb.db3 database to stdout, then it
                pipes to speedtst2plot which reads data from stdin (-i) and create graph image.


./speedtst2plot.py -o /tmp/throuput.png -r speedtst-stats.csv
                Gets its data from csv file (-r argument) and creates graph to specified file.


./speedtst-hist.py -p ./speedtst-stats.csv | ./speedtst2plot.py -i
                This example use speedtst-hist.py to print data (-p option) from csv file to stdout,
                then it's piped to speedtst2plot.py (-i option reads from stdin), which in terms creates
                graph png image to default location (/tmp/output.png).


