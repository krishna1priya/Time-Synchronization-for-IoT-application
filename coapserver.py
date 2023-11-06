import os
import glob

import pandas as pd
import time as t

import httplib, urllib

import sys
import datetime

from twisted.internet import defer
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.python import log

import txthings.resource as resource
import txthings.coap as coap


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
        #temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c
temperature = read_temp()
params = urllib.urlencode({'field1': temperature, 'key':'0ULCO0NCVI34G7W5'})  
headers = {"Content-type": "application/x-www-form-urlencoded","Accept":  
    "text/plain"}  
conn = httplib.HTTPConnection("api.thingspeak.com:80")  
conn.request("POST", "/update", params, headers)  
response = conn.getresponse()  
print  "The cloud is ready for data..."
print response.status, response.reason  
data = response.read()  
conn.close()


class CounterResource (resource.CoAPResource):
   

    def __init__(self, start=0):
        resource.CoAPResource.__init__(self)
        self.counter = start
        self.visible = True
        self.addParam(resource.LinkParam("title", "Counter resource"))
  def render_GET(self, request):
        d = defer.Deferred()
        reactor.callLater(3, self.responseReady, d, request)
        return d

    def responseReady(self, d, request):
        log.msg('response ready')
        payload = "konichiwa"
        response = coap.Message(code=coap.CONTENT, payload=payload)
        d.callback(response)

class TimeResource(resource.CoAPResource):
    def __init__(self):
        resource.CoAPResource.__init__(self)
        self.visible = True
        self.observable = True
        self.notify()

    def notify(self):
        log.msg('trying to send notifications')
        self.updatedState()
        reactor.callLater(60, self.notify)

    def render_GET(self, request):
        response = coap.Message(code=coap.CONTENT, payload=datetime.datetime.now().strftime("HORA"))
        print "time running"
        return defer.succeed(response)
class CoreResource(resource.CoAPResource):
    

    def __init__(self, root):
        resource.CoAPResource.__init__(self)
        self.root = root

    def render_GET(self, request):
        data = []
        self.root.generateResourceList(data, "")
        payload = ",".join(data)
        log.msg("%s", payload)
        response = coap.Message(code=coap.CONTENT, payload=payload)
        response.opt.content_format = coap.media_types_rev['application/link-format']
        return defer.succeed(response)

class HomeResource(resource.CoAPResource):
    isLeaf = True
    def render_GET(self,response):
        print ("Current status: "+ str(read_temp()))
        return defer.succeed(response)


# Resource tree creation
log.startLogging(sys.stdout)
root = resource.CoAPResource()

well_known = resource.CoAPResource()
root.putChild('.well-known', well_known)
core = CoreResource(root)
well_known.putChild('core', core)

counter = CounterResource(5000)
root.putChild('counter', counter)

time = TimeResource()
root.putChild('time', time)

home = HomeResource()   ##########
root.putChild('home',home)

other = resource.CoAPResource()
root.putChild('other', other)
block = BlockResource()
other.putChild('block', block)

separate = SeparateLargeResource()
other.putChild('separate', separate)

endpoint = resource.Endpoint(root)
reactor.listenUDP(61616, coap.Coap(endpoint)) #, interface="::")
reactor.run()
while True:
        for i in range(5):
                tm=read_temp()
                ts=t.time()
                df = df.append({'TS':ts, 'Temp':tm}, ignore_index=True)

        print(df)
	df.to_csv('temp#.csv', index=False)
  print(read_temp())      
  time.sleep(1)
