import json
import os

currPath = os.path.dirname(os.path.abspath(__file__))
parentPath = os.path.dirname(currPath)
libPath = parentPath+'/jan-lib'

# tole moramo dodati da lahko importamo py file iz drugih lokacij
import sys
sys.path.insert(1, libPath)

import jan_sqlite


def getSensorMain(sensorId, startDate, endDate):

    sqlConn = jan_sqlite.create_connection(currPath+"/sensor.db")

    # //SELECT * FROM data WHERE sensor_id = '1' AND created_on BETWEEN '2020-02-15' AND '2020-02-15 23:59:59'
    selectStr = "SELECT * FROM data WHERE sensor_id = '"+sensorId+"' AND created_on BETWEEN '"+startDate+"' and '"+endDate+"'"
    print(selectStr)
    with sqlConn:
        # data = jan_sqlite.get_data_all(sqlConn,'data')
        data = jan_sqlite.run_query(sqlConn, selectStr)
        
    dataList = []  
    currTemp = None
    currHumi = None
    currRssi = None
    for a in data:

        if currTemp == None:
            currTemp = a[3]
            currHumi = a[2]
            currRssi = a[4]

        # d = {"created_on": a[0], "sensor_id": a[1], "humidity": a[2], "temperature": a[3], "rssi": a[4]}
        d = {"date": a[0], "value": a[3]}
        dataList.append(d)

    returnObj = {
        "sensorId": sensorId, 
        "currentTemp":currTemp,
        "currentHumidity": currHumi,
        "currentRssi": currRssi,
        "data": dataList
    }

    dJson = json.dumps(returnObj)

    print(dJson)

    return dJson

if __name__ == '__main__':
    getSensorMain('1','2020-02-15','2020-02-15 23:59:59')