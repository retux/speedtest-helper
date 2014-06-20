#!/usr/bin/env python

""" 
speedtst2plot.py:	this scripts is part of speedtest-helper scripts, and it reads
	set of data created by speedtest-cli with speedtst-hist.py, which stored data
	in csv files or sqlite db.
	speedtst2plot.py gets its input from csv file, a certain sqlite3 db (created
	and populated by speedtst-hist.py, or from stdin (using -i option).
	Then with that data a graph is plotted using gnuplot.py Library.

	In debian based systems install python-gnuplot package (# aptitude install python-gnuplot).
	And

	
"""

import sys, getopt
import re, time, datetime
import time
import sqlite3
import csv
import os
import Gnuplot, Gnuplot.funcutils	# (From deb pkg python-gnuplot)

from pprint import pprint

# Config class, helps to share data between functions calls without need of globals
 
class Config:
	def __init__(self):
		self.tmpFile = None
		self.outFile = None
		self.csvInputFile = None
		self.sqliteInputFile = None

	def getoutFile(self):
		return self.outFile



def main(argv):
	
	# BOF: Default Configuration for tmp file and image file output
	# >>> Adapt path and file to fit your needs <<<
	myConfig = Config()
	myConfig.tmpFile = '/tmp/aux.csv'
	myConfig.outFile = '/tmp/output.png'
	# EOF Config values

	
	file = None
	write = False
	dump2sqlite = False

	try:
		opts, args = getopt.getopt(argv, "o:hr:s:i",["output=","help","read=","sqlite=", "stdin"])
	except getopt.GetoptError as Error:
		print str(Error.msg)
		print 'Usage: ' + sys.argv[0]
		sys.exit(2)

	for opt, arg in opts:
		if opt in ("-h", "--help"):
			Usage()
			sys.exit(2)
		elif opt in ("-o", "--output"):
			myConfig.outFile = arg
		elif opt in ("-r", "--read"):
			myConfig.csvInputFile = arg
			myConfig.tmpFile = arg
			doThePlot(myConfig)
		elif opt in ("-i", "--stdin"):
			ParseStdin(myConfig)
		elif opt in ("-s", "--sqlite"):
			myConfig.sqliteInputFile = arg
			getFromSqlite (myConfig)	
		else:
			assert False, "unhandled option."

	if ( len(argv) == 0 ):
		Usage()


def Usage():
	print "Usage :" + sys.argv[0] + " [-r <file.csv>] [-d <file.csc>]\n"
	print sys.argv[0] + " reads data from stdin, sqlite3 db or csv file and plot throughput graph"
	print "Script should be called this way: \n"
	print "speedtst2plot [options] | " + sys.argv[0] + "[options]"
	print "Or see the examples provided bellow."
	print "\nOptional arguments:"
	print "-o imagefile.png | --output=/path/to/filename.png	(optional) sets the path and name"
	print "	of png file output. Otherwise, /tmp/output.png is the default. Use this option before"
	print "	the others (this will be fixed)."
	print "-r file.csv | --read file.csv 	Reads data from file.csv for plotting."
	print "-s db-file.sql | --sqlite db-file.sql 	Reads data from sqlite3 DB for plotting."
	print "-i  | --stdin 	Reads data in csv format from stdin for plotting."
	print "\n Some examples: "
	print "./speedtst2plot.py -o /tmp/throuput.png -s speedtestdb.db3"
	print "		Uses sqlite3 db speedtestdb.db3 and creates graph at specified file."
	print "\n./speedtst-hist.py -p speedtestdb.db3 | ./speedtst2plot.py --output=/tmp/throuput.png -i"
	print "		speedtst-hist.py dumps data store at speedtestdb.db3 database to stdout, then it"
	print "		pipes to speedtst2plot which reads data from stdin (-i) and create graph image."
	print "\n./speedtst2plot.py -o /tmp/throuput.png -r speedtst-stats.csv"
	print "		Gets its data from csv file (-r argument) and creates graph to specified file."
	print "\n./speedtst-hist.py -p ./speedtst-stats.csv | ./speedtst2plot.py -i"
	print "		This example use speedtst-hist.py to print data (-p option) from csv file to stdout,"
	print "		then it's piped to speedtst2plot.py (-i option reads from stdin), which in terms creates"
	print "		graph png image to default location (/tmp/output.png)."

	print "\n"
	print "\n Author: retux (matiasgutierrezreto@gmail.com). Licensed: GPL."



def doThePlot (myConfig=None):
	g = Gnuplot.Gnuplot()
	#g = Gnuplot.Gnuplot(debug=1)
	g('set datafile separator ","')
	g('set term png')
	#g('set output "output.png"')
	g('set output "' + myConfig.outFile + '"')
	#g('set size 37,37')
	g('set xtics font "Times-Roman 4"')
	g('set ytics font "Times-Roman 4"')
	g('set title "Speedtest"')
	g('set style data fsteps')
	g('set xlabel "Hora (GMT)"')
	g('set timefmt "%s"')
	#g('set format x "%m/%d/%Y %H:%M:%S"')
	#g('set format x "%m/%d %H:%M"')
	g('set format x "%H:%M"')
	g('set xdata time')
	g('set ylabel "Mbits/s"')
	g('set grid')
	g('set key left')
	g('plot "' + myConfig.tmpFile + '" u 1:2 title "Download" with linespoints,  "' + myConfig.tmpFile + '" u 1:3 title "Upload" with linespoints')


def ParseStdin (myConfig=None):
	try:
		myfile = open (myConfig.tmpFile, 'wb')
		wr = csv.writer(myfile, quoting=csv.QUOTE_NONE, escapechar='\\', quotechar='')
		for line in sys.stdin:
			#sys.stdout.write(line)
			data = line.strip().split(',')
			wr.writerow(data)
			#pprint (data)
	except Exception as Error:
		print "CSV creation error: " + str(Error)
	finally:
		myfile.close()
		doThePlot(myConfig)
		deleteTmpFile(myConfig)


def getFromSqlite (myConfig=None):
	
	try:
		db = sqlite3.connect(myConfig.sqliteInputFile)
		cursor = db.cursor()
		tmpfile = myConfig.tmpFile
		myfile = open (tmpfile, 'w')
		wr = csv.writer(myfile)

		cursor.execute('SELECT * FROM speedtest ORDER BY timestamp')
		row = cursor.fetchone()
		while row != None:
			#print row[0], row[1]
			data = [ row[0], row[1], row[2] ]
			wr.writerow(data)
			# Don't forget fetching at last, not using while (True):
			row = cursor.fetchone()
		myfile.close()
	except Exception as Error:
		print "SQLite Error: " + str(Error)
	finally:
		db.close()
	doThePlot(myConfig)
	deleteTmpFile(myConfig)



def deleteTmpFile(myConfig=None):
	try:
		os.remove(myConfig.tmpFile)
	except OSError, e:  
        	print ("Error: %s - %s." % (e.filename,e.strerror))	 


	
if __name__ == "__main__":
   main(sys.argv[1:])



