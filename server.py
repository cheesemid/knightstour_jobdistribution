#!/usr/bin/env python3
import http.server
import socketserver
from http import HTTPStatus
import pickle
import time

import backend

# Server Vars
serverport = 60000

# Bools
dodebug = True

#HTTPRequestHandler
class Handler(http.server.BaseHTTPRequestHandler):
    pagedict = {
        "/next": backend.getnextjob, #backend.getnextjob,
        "/keepalive": backend.updatekeepalive, #backend.updatekeepalive
        "/identify": backend.addclient, #backend.addclient
        "/return": backend.returnjob, #backend.returnjob
        "/admin": b"INSERT ADMIN", #backend.admin
        "/": b"Hello Sir"
    }
    
    def pages(self, data=None):
        try:
            selection = self.pagedict[self.path]
        except KeyError:
            selection = self.pagedict["/"]
        if isinstance(selection, bytes):
            self.wfile.write(selection)
        else:
            try:
                self.wfile.write(selection(data))
            except ConnectionAbortedError:
                logger(3, "ConnectionAbortedError")
    
    def do_GET(self):
        self.send_response(HTTPStatus.OK)
        self.end_headers()
        self.pages()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        self.send_response(HTTPStatus.OK)
        self.end_headers()
        self.pages(post_data)

def logger(iloglevel, logmsg):
    loglevels = {0: "Debug", 1: "Info", 2: "Warn", 3: "Error", 4: "Fatal Error"}
    try:
        strloglevel = loglevels[iloglevel]
    except:
        strloglevel = loglevels[1]
    timelist = list(time.localtime())
    for i in [3,4,5]:
        if int(timelist[i]) < 10:
            timelist[i] = "0" + str(timelist[i]) 
    if iloglevel == 0 and dodebug or iloglevel != 0:
        print("[{0}/{1}/{2} {3}:{4}:{5}]".format(timelist[1],timelist[2],timelist[0],timelist[3],timelist[4],timelist[5]), end="")
        print(f"::{strloglevel}- ", end="")
        print(logmsg, flush=True)
    return 0


if __name__ == "__main__":
    # Initialize Backend
    if backend.initenv():
        # Run Server
        httpd = socketserver.TCPServer(('', serverport), Handler)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            logger(1, "Program Exiting...")
            backend.shutdown()
    else:
        raise Exception("Backend.initenv() returned False")



# python3 server.py
# 127.0.0.1 - - [11/Apr/2017 11:36:49] "GET / HTTP/1.1" 200 -
# http :8000
'''
HTTP/1.0 200 OK
Date: Tue, 11 Apr 2017 15:36:49 GMT
Server: SimpleHTTP/0.6 Python/3.5.2
Hello world
'''


# import http.server
# import socketserver
# from http import HTTPStatus


# class Handler(http.server.SimpleHTTPRequestHandler):
#     def do_GET(self):
#         self.send_response(HTTPStatus.OK)
#         self.end_headers()
#         self.wfile.write(b'Hello world')


# httpd = socketserver.TCPServer(('', 8000), Handler)
# httpd.serve_forever()


# # python3 server.py
# # 127.0.0.1 - - [11/Apr/2017 11:36:49] "GET / HTTP/1.1" 200 -
# # http :8000
# '''
# HTTP/1.0 200 OK
# Date: Tue, 11 Apr 2017 15:36:49 GMT
# Server: SimpleHTTP/0.6 Python/3.5.2
# Hello world
# '''

#self.log_message("%s", "tester")