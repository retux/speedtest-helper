#!/usr/bin/env python
import sys, getopt
import re, time, datetime
import time
import sqlite3
import csv

class Muestra:
	def __init__(self):
		self.timestamp = None
		self.Download = None
		self.Upload = None
		self.Url = None
		self.Unit = None


def main(argv):

	file = None
	write = False
	dump2sqlite = False

	try:
		opts, args = getopt.getopt(argv, "hw:p:s:",["help","write=","print=", "sqlite="])
	except getopt.GetoptError as Error:
		print str(Error.msg)
		print 'Usage: ' + sys.argv[0]
		sys.exit(2)

	for opt, arg in opts:
		if opt in ("-h", "--help"):
			Usage()
			sys.exit(2)
		elif opt in ("-w", "--write"):
			file = arg
			write = True
			ParseStdin(file, 1)		# tipo 1 => dump2file
		elif opt in ("-p", "--print"):
			file = arg	
		elif opt in ("-s", "--sqlite"):
			file = arg
			dump2sqlite = True
			ParseStdin (file, 2)	# tipo 2 => sqlite
		else:
			assert False, "unhandled option."

	if ( len(argv) == 0 ):
		ParseStdin(None,0)	# tipo 0 => stdout


def Usage():
	print "Usage :" + sys.argv[0] + " [-w <file.csv>] [-d <file.csc>]\n"
	print sys.argv[0] + " by default reads input from speedtest-cli from stdin, so script should"
	print "be called this way: \n"
	print "speedtest-cli [options] | " + sys.argv[0] + "[options]"
	print "\nOptional arguments:"
	print "-w file.csv | --write file.csv 	Parses download speed from stdin and appends stats to file.csv."
	print "-s db-file.sql | --sqlite db-file.sql 	Parses download speed from stdin and writes stats to sqlite3 DB."
	print "-p file.csv | --print file.csv	Prints data from file.csv to stdout."
	print "\n If no argumentes are provided program will print output data to stdout."
	print "\n Author: retux (matiasgutierrezreto@gmail.com). Licensed: GPL."


def ParseStdin(file, tipo):
	miMuestra = Muestra()
	miMuestra.timestamp = int(time.time())

	for line in sys.stdin:
		#sys.stdout.write(line)
		if ( re.search(r"[Dd]ownload:", line) and re.search(r"[0-9]", line) ):
			splitted = line.split(' ')
			for cada in splitted:
				if ( re.search(r"[0-9]", cada) ):
					miMuestra.Download = cada.strip()
		if ( re.search(r"[Uu]pload:", line) and re.search(r"[0-9]", line) ):
			splitted = line.split(' ')
			for cada in splitted:
				if ( re.search(r"[0-9]", cada) ):
					miMuestra.Upload = cada.strip()
				if ( re.search(r"bits/s", cada) ):
					miMuestra.Unit = cada.strip()

		if ( re.search(r"[Ss]hare", line) and re.search(r"http:", line) ):
			splitted = line.split(' ')
			for cada in splitted:
				if ( re.search(r"http://.*", cada) ):
					miMuestra.Url = cada.strip()

	if ( file == None and tipo == 0 ):
		Dump2Stdout(file, miMuestra)

	if ( file != None and tipo == 1 ):
		Dump2Csv (file, miMuestra)

	if ( file != None and tipo == 2 ):
		Dump2Sqlite (file, miMuestra)
		

	# Debug de datos
	#print miMuestra.Download
	#print miMuestra.Upload 
	#print miMuestra.Unit 
	#print miMuestra.Url 
	#print miMuestra.timestamp 

	splitted = None


def Dump2Stdout (file, miMuestra):
	print str(miMuestra.timestamp) + ';' + miMuestra.Download + ';' + miMuestra.Upload + ';' + miMuestra.Unit + ';' + miMuestra.Url


def Dump2Csv (file, miMuestra):
	myfile = open (file, 'a')
	#wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
	wr = csv.writer(myfile)
	data = [ miMuestra.timestamp, miMuestra.Download, miMuestra.Upload, miMuestra.Unit, miMuestra.Url ]
	wr.writerow(data)
	myfile.close()


def Dump2Sqlite (file, miMuestra):

	try:
		db = sqlite3.connect(file)
		cursor = db.cursor()
		cursor.execute('''CREATE TABLE IF NOT EXISTS 
			speedtest	(	timestamp	INT PRIMARY KEY,
					 	download 	TEXT,
					 	upload 	TEXT,
					 	unit		TEXT,
						url		TEXT);''')

		try:
			with db:
				db.execute('''INSERT INTO speedtest (timestamp, download, upload, unit, url)
					VALUES(?,?,?,?,?)''', (miMuestra.timestamp,miMuestra.Download,miMuestra.Upload, miMuestra.Unit, miMuestra.Url))
		except sqlite3.IntegrityError:
			print('Record already exists')


	except Exception as Error:
		print "SQLite Error: " + str(Error)

	finally:
		db.close()

	
	print miMuestra.Download

	
if __name__ == "__main__":
   main(sys.argv[1:])



