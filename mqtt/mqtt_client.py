#!/usr/bin/python
#---------------------------------------------------------------------
# mqtt_client.py
# Read value of dht11 sensor
#
# Author : Phien Nguyen (Mark)
# Date   : 21 June 2025
#---------------------------------------------------------------------

import time
import datetime

import paho.mqtt.client as paho
from paho import mqtt
    
class MQTTClient:
    def __init__(self, user, password, cluster_URL):
        self.user = user
        self.password = password
        self.cluster_URL = cluster_URL

        self.mqtt_client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
        # Enable TLS for secure connection
        self.mqtt_client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
        # Set user and password
        self.mqtt_client.username_pw_set(self.user, self.password)
        # Connect to cluster URL at port 8883
        self.mqtt_client.connect(self.cluster_URL, 8883)

    def set_connect_callback(self, connect_callback):
        self.mqtt_client.on_connect = connect_callback

    def set_subscribe_callback(self, subscribe_callback):
        self.mqtt_client.on_subscribe = subscribe_callback

    def set_message_callback(self, message_callback):
        self.mqtt_client.on_message = message_callback

    def set_publish_callback(self, publish_callback):
        self.mqtt_client.on_publish = publish_callback

    def subscribe_channel(self, channel, qos):
        self.mqtt_client.subscribe(channel, qos=qos)

    def publish(self, topic, data, qos):
        self.mqtt_client.publish(topic, data, qos)

    def start_thread_subscribe(self):
        self.mqtt_client.loop_start()

# Setting callbacks for different events to see if it works, print the message etc.
def on_connect(client, userdata, flags, rc, properties=None):
    print("CONNACK received with code %s." % rc)

# With this callback you can see if your publish was successful
def on_publish(client, userdata, mid, properties=None):
    print("mid: " + str(mid))

# Print which topic was subscribed to
def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

# Print message, useful for checking if it was successful
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

if __name__ == "__main__":
    print("THIS APPLICATION USE TO GET ENVIROMENT AND SEND TO SERVER")
    # Define MQTT information
    mqtt_user = "smartnode"
    mqtt_password = "smartnode"
    mqtt_cluster_URL = "xxxx.s1.eu.hivemq.cloud"
    mqtt_topic_weather = "weather"
    mqtt_subscribe_HiveMQ = "hiveMQ"

    mqtt_client_obj = MQTTClient(user=mqtt_user, password=mqtt_password, cluster_URL=mqtt_cluster_URL)
    mqtt_client_obj.set_message_callback(on_message)
    mqtt_client_obj.subscribe_channel(mqtt_subscribe_HiveMQ, 0)
    mqtt_client_obj.start_thread_subscribe()

    while True:
        current_time = datetime.datetime.now()
        str_mqtt = "[{0:02}:{1:02}:{2:02}]".format(
            current_time.hour, current_time.minute, current_time.second)
        print(str_mqtt)
        mqtt_client_obj.publish(mqtt_topic_weather, str_mqtt, 0)
        time.sleep(5)
    