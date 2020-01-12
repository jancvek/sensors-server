from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import threading

from urllib.parse import urlparse, parse_qs

from os import curdir, sep
import json

import os

currPath = os.path.dirname(os.path.abspath(__file__))
parentPath = os.path.dirname(currPath)
libPath = parentPath+'/jan-lib'

# tole moramo dodati da lahko importamo py file iz drugih lokacij
import sys
sys.path.insert(1, libPath)

import jan_sqlite

PORT = 8888

class Handler(BaseHTTPRequestHandler):

    #Handler for the GET requests
    def do_GET(self):
        print(self.path)

        try:  
            # if self.path.endswith('.html'): 
            if self.path.endswith('/'):   
                print("v defaultnem pathu")
        
                #send code 200 response  
                self.send_response(200)  
        
                #send header first  
                self.send_header('Content-type','text-html')  
                self.end_headers()  
        
                #send file content to client  
                fileData = "<html><head></head><body><h1>Dela!</h1></body></html>"
                self.wfile.write(fileData.encode('utf-8'))  
 
                return

            # elif self.path.endswith('/saveData'):
            elif self.path.find('saveData'):
                print("v saveData pathu")

                print(self.path)

                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                query_parameters = parse_qs(urlparse(self.path).query)
                
                id = None
                temp = ''
                humi = ''
                rssi = ''

                if 'id' in query_parameters:
                    id = query_parameters["id"][0]
                else:
                    print("parameter id je nujen!")
                    fileData = "<html><head></head><body><h1>NI PODATKA ID!</h1></body></html>"
                    self.wfile.write(fileData.encode('utf-8'))  
                    return
                if 'temp' in query_parameters:
                    temp = query_parameters["temp"][0] #return -> ['21'] so ve need to add [0]
                if 'humi' in query_parameters:
                    humi = query_parameters["humi"][0]
                if 'rssi' in query_parameters:
                    rssi = query_parameters["rssi"][0]

                sqlConn = jan_sqlite.create_connection(currPath+"/sensor.db")

                with sqlConn:
                    params = "sensor_id,temperature,humidity,rssi"
                    values = (str(id),str(temp),str(humi),int(rssi))              
                    jan_sqlite.insert_data(sqlConn, 'data', params, values)

                fileData = "<html><head></head><body><h1>OK! Sprejeti podatki id = "+id+", temp = "+temp+", humi = "+humi+", rssi = "+rssi+"</h1></body></html>"
                self.wfile.write(fileData.encode('utf-8'))  
                return

        except IOError:  
            self.send_error(404, 'file not found')  

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

if __name__ == '__main__':
    server = ThreadedHTTPServer(('0.0.0.0', PORT), Handler) #uporabi 'localhost' če želiš dovoliti dostop le na host-u
    print('Starting server, use <Ctrl-C> to stop')
    server.serve_forever()