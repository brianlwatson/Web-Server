import errno
import select
import socket
import sys
import traceback

#parses the http request

class RequestParser:
	def __init__(self, message):
		self.method = ''
		self.path = ''
		self.headers = {}
		self.status = 0
		self.body = {}
		self.parse_request(message)
		

	def parse_request(self, message):
		try:
		    from http_parser.parser import HttpParser
		except ImportError:
		    from http_parser.pyparser import HttpParser

		p = HttpParser()
		nparsed = p.execute(message,len(message))
		
		self.method = p.get_method()
		self.path = p.get_path()
		self.headers = p.get_headers()

		if p.get_method() == 'GET':
			self.status = 200

		#if "Range" in p.get_headers():
		#	strings = self.headers["Range"]
		#	print strings

		elif p.get_method() != 'GET':
			self.status = 501		#if the method is not a GET
			#TODO maybe make this a head request eventually if you do the download accelerator

		if not p.get_method():
			self.status = 400

		if p.get_path() == '/':
			self.path = '/index.html'

		elif p.get_path().endswith('/'):
			self.path += 'index.html'
		
		if p.get_path() is None:
			self.status = 501


		#print self.path
		"""
		print '\nMethod: ' 
		print p.get_method() 
		print '\nPath: ' 
		print p.get_path()
		print '\nHeaders: ' 
		print p.get_headers()
		print '\nVersion: '
		version = p.get_version()
		print version
		"""
		#print '\nRESPONSE CODE: ' + str(self.status) + '\n'
		#print self.path
		#print self.status
		#working so far