#!/usr/bin/env python
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, https://github.com/treedust, Kyle Carlstrom, and Tian Zhi Wang
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib
import urlparse

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPRequest(object):
    def __init__(self, method, url, args=None):
        parsed_url = urlparse.urlsplit(url)

        self.method = method
        self.host = parsed_url.hostname
        self.port = int(parsed_url.port or 80)
        self.body = urllib.urlencode(args) if args else ""
        self.path = "".join([parsed_url.path, "?", parsed_url.query])

    def get_headers(self):
        headers = ["Host: {}:{}\r\n".format(self.host, self.port),
                   "Content-Length: {}\r\n".format(len(self.body))]
        if self.body:
            headers.append("Content-Type: application/x-www-form-urlencoded\r\n")

        return "".join(headers)

    def get_action_line(self):
        return "{} {} HTTP/1.1\r\n".format(self.method, self.path)

    def get_full_request(self):
        action_line = self.get_action_line()
        headers = self.get_headers()
        return "".join([action_line, headers, "\r\n", self.body])

class HTTPClient(object):
    # Connect code based on lab tutorial by Joshua Campbell
    def connect(self, host, port):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        return client_socket

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)

    def parse_response(self, response):
        status_code = int(response.split("\r\n")[0].split(" ")[1])
        # Check if there is a body in the response and if so set it
        body = "" if len(response.split("\r\n\r\n", 1)) == 1 else response.split("\r\n\r\n", 1)[-1]
        return HTTPResponse(status_code, body)

    def handle_request(self, request):
        client_socket = self.connect(request.host, request.port)
        client_socket.sendall(request.get_full_request())
        message = self.recvall(client_socket)
        return self.parse_response(message)

    def GET(self, url, args=None):
        request = HTTPRequest("GET", url, args)
        return self.handle_request(request)

    def POST(self, url, args=None):
        request = HTTPRequest("POST", url, args)
        return self.handle_request(request)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command( sys.argv[2], sys.argv[1] )
    else:
        print client.command( sys.argv[1] )   
