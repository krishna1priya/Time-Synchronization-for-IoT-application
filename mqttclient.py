import paho.mqtt.client as mqtt
import time 

t1=time.time()
MQTT_SERVER = "192.168.43.61"
MQTT_PATH = "home"

def on_connect(client, userdata, flags, rc):
    if rc==0:
        client.connected_flag=True    
        print("Connected "+str(rc))
    else:
        print("Not connected with return code=",rc) 
    client.subscribe(MQTT_PATH)
  
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    
    t2=time.time()
    t3=str(t2-t1)
    print("Data transmission time: "+t3)
 
client = mqtt.Client()

client.on_connect = on_connect

client.on_message = on_message

client.connect(MQTT_SERVER, 1883, 60)

t4=time.time()
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    
    t2=time.time()
    t3=str(t2-t1)
    print("Data transmission time: "+t3)
 
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_SERVER, 1883, 60)
t4=time.time()
tim=str(t4-t1)
print("TCP transmission time : "+tim)
client.loop_forever()
