import errno
import select
import socket
import sys
import traceback
import time
from WebConf import WebConf
from HttpResponse import HttpResponse
from RequestParser import RequestParser

class Poller:
    """ Polling server """
    def __init__(self,port):
        self.host = ""
        self.port = port
        self.open_socket()
        self.clients = {}
        self.size = 1024
        self.webconfig = WebConf()
        self.timeouts = {}
        self.cache = {}


    def open_socket(self):
        """ Setup the socket for incoming clients """
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
            self.server.bind((self.host,self.port))
            self.server.listen(5)
            self.server.setblocking(0)
        except socket.error, (value,message):
            if self.server:
                self.server.close()
            print "Could not open socket: " + message
            sys.exit(1)

    def run(self):
        """ Use poll() to handle each incoming client."""
        self.poller = select.epoll()
        self.pollmask = select.EPOLLIN | select.EPOLLHUP | select.EPOLLERR
        self.poller.register(self.server,self.pollmask)
        self.timeout = float(self.webconfig.parameters["timeout"])
        lastSweep = time.time()

        while True:
            # poll sockets

            if (time.time() - lastSweep) > .5:  #sweet through every half second
                self.socketCheck()
                lastSweep = time.time()
            try:
                fds = self.poller.poll(timeout=1.0)
            except:
                return
            fd = 0
            for (fd,event) in fds:
                # handle errors
                if event & (select.POLLHUP | select.POLLERR):
                    self.handleError(fd)
                    continue
                # handle the server socket
                if fd == self.server.fileno():
                    self.handleServer()
                    continue
                # handle client socket
                result = self.handleClient(fd)


    def socketCheck(self):
        for key in self.timeouts.keys():
            if (time.time() - self.timeouts[key]) > self.timeout:
                del self.timeouts[key]
                del self.clients[key]


    def handleError(self,fd):
        self.poller.unregister(fd)
        if fd == self.server.fileno():
            # recreate server socket
            self.server.close()
            self.open_socket()
            self.poller.register(self.server, self.pollmask)
        else:
            # close the socket
            del self.clients[fd]
            del self.timeouts[fd]

    def handleServer(self):
        # accept as many clients as possible
        while True:
            try:
                (client,address) = self.server.accept()
            except socket.error, (value,message):
                # if socket blocks because no clients are available,
                # then return
                if value == errno.EAGAIN or errno.EWOULDBLOCK:
                    return
                print traceback.format_exc()
                sys.exit()
            # set client socket to be non blocking
            client.setblocking(0)
            self.clients[client.fileno()] = client
            self.timeouts[client.fileno()] = time.time()
            self.poller.register(client.fileno(),self.pollmask)


 
    def sendResponse(self, d, fd):
        rp = RequestParser(d)
        httpr = HttpResponse(rp, self.webconfig)

        responseFull = httpr.getResponse() 
        partialResponse = responseFull

        sent = 0
        while partialResponse: #if it's going to block, return and do another client
            try:
                #self.timeouts[fd] = time.time()
                sent = sent + self.clients[fd].send(partialResponse)
                self.timeouts[fd] = time.time()
                partialResponse = responseFull[sent:]

            except socket.error, (value,message):
            # if buffer is full, move on to another client
                if value == errno.EAGAIN or errno.EWOULDBLOCK:
                    continue 

        #print i
        #print httpr.headers["Content-Length"]

    def handleClient(self,fd):
        try:
            data = self.clients[fd].recv(self.size)
            self.timeouts[fd] = time.time()
        except socket.error, (value,message):
            # if no data is available, move on to another client
            if value == errno.EAGAIN or errno.EWOULDBLOCK:
                return
            print traceback.format_exc()
            sys.exit()

        if data:

            if "\r\n\r\n" in data:
                if fd in self.cache:
                    data = self.cache[fd] + data
                    del self.cache[fd]

                self.sendResponse(data, fd)
                self.timeouts[fd] = time.time() 

            else:
                if not fd in self.cache:
                    self.cache[fd] = data
                else:
                    self.cache[fd] += data
                #print responseFull

        else:
            if not "\r\n\r\n" in data:
                self.poller.unregister(fd)
                self.clients[fd].close()
                del self.clients[fd]
                del self.timeouts[fd]

                if fd in self.cache:
                    del self.cache[fd]
