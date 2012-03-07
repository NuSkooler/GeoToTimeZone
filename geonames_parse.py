#!/usr/bin/env python

"""
 Copyright (c) 2012 Bryan Ashby

 This software is provided 'as-is', without any express or implied
 warranty. In no event will the authors be held liable for any damages
 arising from the use of this software.

 Permission is granted to anyone to use this software for any purpose,
 including commercial applications, and to alter it and redistribute it
 freely, subject to the following restrictions:

    1. The origin of this software must not be misrepresented; you must not
    claim that you wrote the original software. If you use this software
    in a product, an acknowledgment in the product documentation would be
    appreciated but is not required.

    2. Altered source versions must be plainly marked as such, and must not be
    misrepresented as being the original software.

    3. This notice may not be removed or altered from any source
    distribution.
"""

import csv
import sys
from optparse import OptionParser
import demjson

#	some globals
PROG_VERSION	= '1.2.0.0'
EXIT_SUCCESS 	= 0
EXIT_FAILURE	= (-1)
DEFAULT_MEMBERS = ["lat", "lon", "tz"]

def makeMemberName(n):
	s = n[0].upper()
	s += n[1:]
	return s

class Generator:
	def getHeader(self, requestedFields=DEFAULT_MEMBERS):
		return None

	def getFooter(self, requestedFields=DEFAULT_MEMBERS):
		return None

	def getEntry(self, requestedFields=DEFAULT_MEMBERS):
		return None

	def getEntrySeparator(self):
		return None

class GeneratorJSON(Generator):
	def getHeader(self, requestedFields=DEFAULT_MEMBERS):
		return "[\n"

	def getFooter(self, requestedFields=DEFAULT_MEMBERS):
		return "]\n"

	def getEntry(self, row, requestedFields=DEFAULT_MEMBERS):
		members = {}
		for m in requestedFields:
			members[m] = getattr(row, 'get' + makeMemberName(m))()
		return demjson.encode(members, encoding='utf-8', compactly=False)

	def getEntrySeparator(self):
		return ',\n'

class GeneratorMongoDB(Generator):
	def getEntry(self, row, requestedFields=DEFAULT_MEMBERS):
		members = {}
		for m in requestedFields:
			members[m] = getattr(row, 'get' + makeMemberName(m))()
		return demjson.encode(members, encoding='utf-8')

	def getEntrySeparator(self):
		return '\n'

class CityRow:
	def processCell(self, pos, cellData):
		pass		

	def getId(self):
		return self.id or None

	def getName(self):
		return self.name or None

	def getAsciiName(self):
		return self.asciiName or None

	def getAltNames(self):
		return self.altNames or None

	def getLocaleName(self):
		return self.localeName or None

	def getLat(self):
		return self.geoLat or None

	def getLon(self):
		return self.geoLon or None

	def getTz(self):
		return self.timeZone or None

	def getLoc(self):
		return [self.geoLon, self.geoLat]

class CityRowGeoNames(CityRow):
	def __init__(self, row):
		pos = 0
		for cellData in row:
			self.processCell(pos, cellData)
			pos += 1

	"""
		GeoNames.ort citiesXXXXX.txt is broken up in a tab CVS in the following order:

		geoNameId		= (-1)
		name			= u''
		asciiName		= ''
		altNames		= []
		geoLat			= 0.0
		geoLon			= 0.0
		featureClass	= None
		featureCode		= None
		altCountryCodes	= []
		adminCode1		= ''
		adminCode2		= ''
		adminCode3		= ''
		adminCode4		= ''
		population		= 0
		elevation		= 0
		dem
		timeZone
		modDate
	"""
	def processCell(self, pos, cellData):
		#
		#	See docs here for more information:
		#	http://download.geonames.org/export/dump/
		#
		if 0 == pos:
			self.id = int(cellData)
		elif 1 == pos:
			self.name = unicode(cellData, 'utf-8')
		elif 2 == pos:
			self.asciiName = cellData
		elif 3 == pos:
			altNames = cellData.split(',')
			self.altNames = []
			for n in altNames:
				self.altNames.append(unicode(n, 'utf-8'))
			#	we can also proivde the "localeName" here
			if len(self.altNames) > 0:
				self.localeName = self.altNames[-1]
		elif 4 == pos:
			self.geoLat = float(cellData)
		elif 5 == pos:
			self.geoLon = float(cellData)
		elif 17 == pos:
			self.timeZone = cellData
		elif 18 == pos:
			pass
		else:
			pass

class CityFileReader:
	def __init__(self):
		self.rows = []

	def parse(self, path):
		return False

	def getRows(self):
		return self.rows

class CityFileReaderGeoNames(CityFileReader):
	def parse(self, path):
		try:
			with open(path, 'rb') as f:
				reader = csv.reader(f, delimiter='\t')
				for row in reader:
					self.rows.append(CityRowGeoNames(row))
				return True
		except:
			return False

def output(node, outFile, opts):
	if None == node:
		return
	if None != outFile:
		outFile.write(node)
	if not opts.silent:
		print node

def getGenerator(name):
	try:
		obj = globals()['Generator' + name]
		return obj()
	except:
		return None

def getReader(name):
	try:
		obj = globals()['CityFileReader' + name]
		return obj()
	except:
		return None

def main():
	"""
	ArgumentParser usage currently disabled as it requires Python 2.7+
	(also not yet complete)

	import argparse

	argParser = argparse.ArgumentParser(
		description='Parses and transforms city-to-timezone data such as from GeoNames.org')

	argParser.add_argument('--version', action='version', version='%(prog)s v' + PROG_VERSION)
	argParser.add_argument('--members', nargs='+', choices=DEFAULT_MEMBERS)
	argParser.add_argument('--reader', help='specifies reader to use for input', default='GeoNames')
	argParser.add_argument('--generator', help='specifies generator to use for output', default='MongoDB')

	#	I/O files
	argParser.add_argument('infile', nargs='?', type=argparse.FileType('rb'), default=sys.stdin)
	argParser.add_argument('outfile', nargs='?', type=argparse.FileType('w'), default=sys.stdout)

	args = argParser.parse_args()

	##############################
	return 0;
	"""

	optParser = OptionParser(
		version='1.1.0.0',
		description='Parses and transforms city-to-timezone data such as from GeoNames.org')

	optParser.add_option('', '--out', dest='outPath', help='specifies output file path', type='string')
	optParser.add_option('', '--members', dest='members', help='specifies member(s) to include', type='string', default=','.join(DEFAULT_MEMBERS))
	optParser.add_option('', '--reader', dest='reader', help='specifies reader to use for input', type='string', default='GeoNames')
	optParser.add_option('', '--generator', dest='generator', help='specifies generator to use for output', type='string', default='MongoDB')
	optParser.add_option('', '--silent', dest='silent', help='less chatty', action='store_true', default=False)

	(opts, args) = optParser.parse_args()

	if len(args) < 1:
		optParser.error('Missing input file!')

	inputFilePath = args[0]

	if None != opts.outPath:
		try:
			outFile = open(opts.outPath, 'w')
		except:
			optParser.error('Cannot open "%s"' % opts.outPath)
	else:
		outFile = None

	if None != opts.members:
		memberNames = opts.members.split(',')

	reader = getReader(opts.reader)
	if None == reader:
		optParser.error('Reader "%s" unknown' % opts.reader) 

	generator = getGenerator(opts.generator)
	if None == generator:
		optParser.error('Generator "%s" unknown' % opts.generator)

	if not reader.parse(inputFilePath):
		optParser.error('Cannot parse "%s"' % inputFilePath)

	output(generator.getHeader(memberNames), outFile, opts)
	cityRows = reader.getRows()
	for row in cityRows:
		output(generator.getEntry(row, memberNames), outFile, opts)
		output(generator.getEntrySeparator(), outFile, opts)
	output(generator.getFooter(memberNames), outFile, opts)

	return EXIT_SUCCESS

if '__main__' == __name__:
	sys.exit(main())
