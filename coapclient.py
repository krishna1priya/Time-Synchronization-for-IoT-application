import sys
from ipaddress import ip_address

from twisted.internet import reactor
from twisted.python import log

import txthings.coap as coap
import txthings.resource as resource
import time 

class Agent:
    
    def __init__(self, protocol):
        self.protocol = protocol
        reactor.callLater(1, self.requestResource)

    def requestResource(self):
        request = coap.Message(code=coap.GET)
        request.opt.uri_path = (b'test',)
        request.opt.observe = 0
        request.remote = (ip_address("192.168.43.61"), coap.COAP_PORT)
        d = protocol.request(request, observeCallback=self.printLaterResponse)
        d.addCallback(self.printResponse)
        d.addErrback(self.noResponse)
        t2=time.time()
        t3=str(t2-t1)
        print ("data transmission time: "+t3)
    def printResponse(self, response):
        print("First result: " + str(response.payload, 'utf-8'))
    def printLaterResponse(self, response):
        print("Observe result: "+ str(response.payload, 'utf-8'))


    def noResponse(self, failure):
        print('Failed to fetch resource:')
        print(failure)

t1= time.time()
log.startLogging(sys.stdout)
print "Welcome Home"
print "Retriving home data"
endpoint = resource.Endpoint(None)


protocol = coap.Coap(endpoint)
client = Agent(protocol)
reactor.listenUDP(61616, protocol) 
t2=time.time()
t3= str(t2-t1)
print("UDP transmission time:"+t3)
reactor.run()
