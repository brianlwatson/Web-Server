#This is going to be the object that holds my settings


class WebConf:
	def __init__(self):
		self.hosts = {}
		self.medias = {}
		self.parameters = {}
		self.parseWeb_Conf()

		"""
		media txt text/plain
		media html text/html
		media jpg image/jpeg
		media gif image/gif
		media png image/png
		media pdf application/pdf

		in media, you want to store txt:text/plain
		don't store the key value media
		"""

	def parseWeb_Conf(self):
		with open('web.conf') as f:
			for line in f:
				words = line.split(' ', 2)

				if words[0] == 'host':
					self.hosts[words[1]] = words[2]
					#print words[1]
					#print words[2]
				elif words[0] == 'media':
					self.medias[words[1]] = words[2]
				elif words[0] == 'parameter':
					self.parameters[words[1]] = words[2]
				


"""
p = WebConf()

print '\n\nmedias'
print p.medias
print '\n\nparameter'
print p.parameters
print '\n\nhost'
print p.hosts

works!
"""