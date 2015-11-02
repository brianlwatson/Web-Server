import socket
import sys
import argparse
from poller import Poller

#this is going to be my main function basically 

class Server:
    def __init__(self):
        self.parse_arguments()
        self.debug = 0

    def parse_arguments(self):
        parser = argparse.ArgumentParser(prog='CS360 Web Server', description='BYU CS 360 Lab 4', add_help = True)
        parser.add_argument('-p', '--port', type=int, action='store', help='specify port to bind on',default = 8080)
        parser.add_argument('-d', nargs='?', const = '1', default = '0')
        self.args = parser.parse_args()

    def run(self):
        p = Poller(self.args.port) #so now my 
        p.run()


s = Server()
#print s.args.port
s.debug = s.args.d
#print s.debug
s.run()

#works