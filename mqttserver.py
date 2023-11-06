import os
import glob
import pandas as pd
import time as t
import httplib,urllib
import paho.mqtt.publish as publish

MQTT_SERVER = "192.168.43.61"
MQTT_PATH = "home"
df = pd.DataFrame(columns=['TS', 'Temp'])
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm') 
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'
 
def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines
def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
       # temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c

publish.single(MQTT_PATH, "temperature=  "+str(read_temp()), hostname=MQTT_SERVER)
temperature = read_temp()
params = urllib.urlencode({'field1': temperature, 'key':'0ULCO0NCVI34G7W5'})  
headers = {"Content-type": "application/x-www-form-urlencoded","Accept":
    "text/plain"}  
conn = httplib.HTTPConnection("api.thingspeak.com:80")  
conn.request("POST", "/update", params, headers)  
response = conn.getresponse()  
print "Welcome Home"
print "Data also available on Cloud"
print response.status, response.reason  
data = response.read()  
conn.close()
read_temp()
while True:
        for i in range(5):
                tm=read_temp()
                ts=t.time()
                df = df.append({'TS':ts, 'Temp':tm}, ignore_index=True)
        print(df)
        df.to_csv('temp.csv', index=False)
        time.sleep(1)   
