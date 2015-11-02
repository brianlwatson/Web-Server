import stat
import time
import os
import sys
from email.utils import formatdate


class HttpResponse:
	def __init__(self, request, webconfig):
		self.version = 'HTTP/1.1'
		self.statuscode = 200
		self.phrase = 'OK'
		self.headers = {}
		self.body = ''
		self.method = ''
		self.entitybody = ''
		
		temppath = webconfig.hosts["default"] + request.path
		self.path = temppath.replace("\n", "")
		
		self.response = ''
		self.setCode(request)
		self.getEntityBody()
		self.setHeaders(request, webconfig)
		

	def setCode(self, request):
		self.statuscode = request.status

		self.method = request.method
		if self.statuscode == 200:
			self.phrase = 'OK'

		else:
			self.phrase = 'ERROR'



	def getEntityBody(self):
		#st = os.stat(self.path)

		#print 'PATH TEST: ' + self.path

		if not os.path.exists(self.path):
			self.statuscode = 404
			self.entitybody = "<html><body><h1>404 Not Found</h1></body></html>"
			self.headers["Content-Length"] = str(len(self.entitybody))
			self.phrase = "Not Found"

			return

		elif bool(os.stat(self.path).st_mode & stat.S_IRGRP) == False:
			self.statuscode = 403
			self.entitybody = "<html><body><h1>403 Forbidden</h1></body></html>"
			self.phrase = "Forbidden"
			self.headers["Content-Length"] = str(len(self.entitybody))
			return

		if self.statuscode == 400:
			self.entitybody = "<html><body><h1>400 Bad Request</h1></body></html>"
			self.phrase = "Bad Request"

		elif self.statuscode == 500:
			self.entitybody = "<html><body><h1>500 Internal Server Error</h1></body></html>"
			self.phrase = "Internal Server Error"

		elif self.statuscode == 501:
			self.entitybody = "<html><body><h1>501 Not Implemented</h1></body></html>"
			self.phrase = "Not Implemented"

		if self.statuscode != 200:
			self.headers["Content-Length"] = str(len(self.entitybody))
			self.headers["Content-Type"] = "text\\html"


		elif self.statuscode == 200:
			files = ''
			with open(self.path, "rb") as f:
				self.entitybody += f.read()

			f.close()
			#self.entitybody = "<html><body><h1>200 OK</h1></body></html>"
			return	

	def setHeaders(self, request, webconfig):
		
		path = self.path

		mediatype = os.path.splitext(path)[1]
		mediatypes = mediatype.strip('.')
		if mediatypes == '':
			mediatypes = "txt"


		self.headers["Date"] = formatdate(time.time(), localtime=False, usegmt=True) 
		self.headers["Server"] = "watson_server1.0"
		self.headers["Content-Type"] = webconfig.medias[mediatypes]
		
		if self.statuscode == 200:
			self.headers["Content-Length"] = str(os.path.getsize(path))
			self.headers["Last Modified"] = time.ctime(os.path.getmtime(path))#formatdate(os.stat(path).st_mtime)

	
		if self.statuscode == 200:
			self.headers["Content-Type"] = webconfig.medias[mediatypes]

		elif self.statuscode != 200:
			self.headers["Content-Type"] = "text\\html"
			
			#self.entitybody = 

	def getResponse(self):
		headerline = self.version + ' ' + str(self.statuscode) + ' ' + self.phrase + '\r\n'

		totalheaders = ''
		for key in self.headers:
			totalheaders += key + ': ' + self.headers[key].strip('\r\n') + '\r\n'
		
		blankline = '\r\n'


		self.response = headerline + totalheaders  + blankline + self.entitybody
		self.headers["Content-Length"] = len(self.entitybody)
		#print len(self.response)
		#print '\n\n'
		#print self.response
		return self.response