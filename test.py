#!/usr/bin/env python3

#####################################
#                                   #
#              "Test"               #
#       Simple bandwidth test       #
#        from browser or CLI        #
#                                   #
#          Etienne  SELLAN          #
#                                   #
#####################################

import sys
import time
import signal
import threading
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from os import environ

# SETTINGS BEGIN
settings = {}
settings["listen_address"] = "0.0.0.0"
settings["port"] = 80
settings["max_payload_size"] = 100000000 #  bytes
# SETTINGS END

payload = str.encode("\x10" * settings["max_payload_size"])

def settings_initialisation():
    for setting in settings:
        # Take environment settings if defined
        if ("test_"+setting) in environ:
            settings[setting] = environ[("test_"+setting)]

class request_handler(BaseHTTPRequestHandler):
    def do_GET(self):
        request = None
        if len(path_to_array(self.path)) > 0:
            request = path_to_array(self.path)[0]

        if "curl" in self.headers['User-Agent'].lower() or request == "payload":
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            duration = 0
            payload_size = 10000
            while duration < 1 and payload_size < settings["max_payload_size"]:
                payload_size *= 10
                print("Use a payload of "+human_readable(payload_size))
                time1 = time.time()
                self.wfile.write(payload[0:payload_size])
                time2 = time.time()
                duration = time2-time1
            speed = payload_size/duration
            human_readable_speed = human_readable(speed)+'/s'
            self.wfile.write(str.encode(human_readable_speed+"\n"))
        else:
            with open('index.html', 'rb') as file:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(file.read())
        return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass

def run_on(port):
    print("\n")
    print("/-------------------------------\\")
    print("|  Starting Test on port {}  |".format(str(settings["port"]).rjust(5, " ")))
    print("\\-------------------------------/")
    print("\n")
    print("\n\nLogs : \n")
    server_address = (settings["listen_address"], int(settings["port"]))
    httpd = ThreadedHTTPServer(server_address, request_handler)
    httpd.serve_forever()


def human_readable(bytes):  # Convert bytes to human readable string format
    units = ['o', 'Ko', 'Mo', 'Go', 'To', 'Po']
    cursor = 0
    while bytes > 1024:
        bytes /= 1024
        cursor += 1
    value = str(bytes).split('.')
    value[1] = value[1][:2]
    value = '.'.join(value)
    return value+' '+units[cursor]


def human_readable_time(seconds):  # Convert time in seconds to human readable string format
    units = ['second', 'minute', 'hour', 'day', 'week', 'month', 'year']
    maximum_values = [60, 60, 24, 7, 4, 12, 99]
    cursor = 0
    while seconds > maximum_values[cursor]:
        seconds /= maximum_values[cursor]
        cursor += 1
    value = math.ceil(seconds)
    unit = units[cursor]
    if float(value) > 1:
        unit += 's'
    return str(value)+' '+unit

def path_to_array(path):
    # Split path
    path_array = path.split('/')
    # Remove empty elements
    path_array = [element for element in path_array if element]
    return path_array


def array_to_path(path_array):
    # Join array
    path = '/' + '/'.join(path_array)
    return path

if __name__ == "__main__":
    server = Thread(target=run_on, args=[int(settings["port"])])
    server.daemon = True
    server.start()
    settings_initialisation()
    signal.pause()
