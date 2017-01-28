#!/usr/bin/env python
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust, Kyle Carlstrom
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
        self.code = int(code)
        self.body = body

class HTTPClient(object):
    # Connect code based on lab tutorial by Joshua Campbell
    def connect(self, host, port):
        port = int(port or 80)
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        return client_socket

    def get_code(self, data):
        return None

    def get_headers(self, host, body_size, port=None):
        port = port or 80
        headers = ["Host: {}:{}\r\n".format(host, str(port))]
        headers.append("Content-Length: {}\r\n".format(str(body_size)))
        if body_size:
            headers.append("Content-Type: application/x-www-form-urlencoded\r\n")
        headers.append("\r\n")
        return "".join(headers)

    def get_body(self, data):
        if data:
            print("ENCODING: " + urllib.urlencode(data))
            return urllib.urlencode(data)
        return ""

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
        status_code = response.split("\r\n")[0].split(" ")[1]
        body = "" if len(response.split("\r\n\r\n", 1)) == 1 else response.split("\r\n\r\n", 1)[-1]
        return HTTPResponse(status_code, body)

    def GET(self, url, args=None):
        parsed_url = urlparse.urlparse(url)
        body = self.get_body(args)
        headers = self.get_headers(parsed_url.hostname, len(body))
        action = "GET {} HTTP/1.1\r\n".format(parsed_url.path)

        client_socket = self.connect(parsed_url.hostname, parsed_url.port)
        client_socket.sendall(action + headers + body)
        message = self.recvall(client_socket)

        return self.parse_response(message)

    def POST(self, url, args=None):
        parsed_url = urlparse.urlparse(url)
        body = self.get_body(args)
        headers = self.get_headers(parsed_url.hostname, len(body), parsed_url.port)
        action = "POST {} HTTP/1.1\r\n".format(parsed_url.path)

        client_socket = self.connect(parsed_url.hostname, parsed_url.port)
        print(action + headers + body)
        client_socket.sendall(action + headers + body)

        message = self.recvall(client_socket)
        return self.parse_response(message)

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
