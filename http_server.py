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
import sensor

PORT = 8888

class Handler(BaseHTTPRequestHandler):

    #Handler for the GET requests
    def do_GET(self):
        print(self.path)

        try:  
            # if self.path.endswith('.html'): 
            if self.path.endswith('/'):   
                print("v defaultnem pathu")
                self.path = "index.html"
                print(curdir + sep +self.path)
                f = open(curdir + sep +self.path) #open requested file  
        
                #send code 200 response  
                self.send_response(200)  
        
                #send header first  
                self.send_header('Content-type','text-html')  
                self.end_headers()  
        
                #send file content to client  
                fileData = f.read()
                self.wfile.write(fileData.encode('utf-8'))  
                f.close()  
                return

            # elif self.path.endswith('/saveData'):
            elif self.path.find('saveData') > -1:
                print("v saveData pathu")

                print(self.path.find('saveData'))

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

            elif self.path.find('/tempApi/main') > -1:
                #send code 200 response  
                self.send_response(200)

                #send header first  
                self.send_header('Content-type', 'application/json')
                self.end_headers()    

                query_parameters = parse_qs(urlparse(self.path).query)

                sensorId = ''
                startDate = ''
                endDate = ''

                if 'sensorId' in query_parameters:
                    sensorId = query_parameters["sensorId"][0]
                else:
                    print("parameter sensorId je nujen!")
                    fileData = "<html><head></head><body><h1>NI PODATKA sensorId!</h1></body></html>"
                    self.wfile.write(fileData.encode('utf-8'))  
                    return

                if 'startDate' in query_parameters:
                    startDate = query_parameters["startDate"][0]
                else:
                    print("parameter startDate je nujen!")
                    fileData = "<html><head></head><body><h1>NI PODATKA startDate!</h1></body></html>"
                    self.wfile.write(fileData.encode('utf-8'))  
                    return

                if 'endDate' in query_parameters:
                    endDate = query_parameters["endDate"][0]
                else:
                    print("parameter endDate je nujen!")
                    fileData = "<html><head></head><body><h1>NI PODATKA endDate!</h1></body></html>"
                    self.wfile.write(fileData.encode('utf-8'))  
                    return

                # eg: '1','2020-02-15','2020-02-15 23:59:59'
                resJson = sensor.getSensorById(sensorId,startDate,endDate)

                mStr = json.dumps(resJson)
                mBin = mStr.encode('utf-8')

                self.wfile.write(mBin) 

            elif self.path.find('/tempApi/table') > -1:
                #send code 200 response  
                self.send_response(200)

                #send header first  
                self.send_header('Content-type', 'application/json')
                self.end_headers()    

                query_parameters = parse_qs(urlparse(self.path).query)

                sensorId = ''
                startDate = ''
                endDate = ''

                if 'top' in query_parameters:
                    top = query_parameters["top"][0]
                else:
                    print("parameter top je nujen!")
                    fileData = "<html><head></head><body><h1>NI PODATKA top!</h1></body></html>"
                    self.wfile.write(fileData.encode('utf-8'))  
                    return

                # eg: '1','2020-02-15','2020-02-15 23:59:59'
                resJson = sensor.getSensors(top)

                mStr = json.dumps(resJson)
                mBin = mStr.encode('utf-8')

                self.wfile.write(mBin) 

        except IOError:  
            self.send_error(404, 'file not found')  

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

if __name__ == '__main__':
    server = ThreadedHTTPServer(('0.0.0.0', PORT), Handler) #uporabi 'localhost' če želiš dovoliti dostop le na host-u
    print('Starting server, use <Ctrl-C> to stop')
    server.serve_forever()