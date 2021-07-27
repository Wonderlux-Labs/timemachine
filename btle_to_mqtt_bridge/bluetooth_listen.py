import os
import time
from waiting import wait

import paho.mqtt.client as mqtt

mqttConnected = False

def on_connect(_1,_2,_3,_4):
    global mqttConnected

    print("Connected to MQTT")
    mqttConnected = True

def on_disconnect():
    global mqttConnected

    print("something went wrong with MQQT!")
    mqttConnected = False

def setup_mqtt():
    global mqttConnected

    if mqttConnected:
        print("already connected to MQTT")
    else:
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        client.username_pw_set('timemachinemqtt', password='timemachine')
        client.connect("192.168.68.118")
        client.loop_start()
        return client

from adafruit_ble import BLERadio
from adafruit_ble.services.nordic import UARTService
ble = BLERadio()
ble._adapter.ble_backend = "hcitool"
uart = UARTService()


class Platform:
    def __init__(self, name):
        self.name = name
        self.address = None
        self.found = False
        self.connection = None
        self.service = None

platform_one = Platform(name='platform_one')
platform_two = Platform(name='platform_two')
platform_three = Platform(name='platform_three')
platform_four = Platform(name='platform_four')
platforms = [platform_one, platform_two, platform_three, platform_four]
disconnected_platforms = []
failureCount = 0

state_topic = 'home-assistant/'

def reset_bt():
    raise 'Restarted...see you in a bit!'

def platform_connected(platform):
    global disconnected_platforms
    if platform.connection and platform.connection.connected:
        if platform in disconnected_platforms:
            disconnected_platforms.remove(platform)
            if client:
                client.publish(f'home-assistant/{platform.name}/availability', 'online')
                client.publish(f'home-assistant/{platform.name}/occupied', 'empty')
        return True
    else:
        if platform not in disconnected_platforms:
            if client: client.publish(f'home-assistant/{platform.name}/availability', 'offline')
            disconnected_platforms.append(platform)
        return False

def all_connected():
    all_connected = True
    for platform in platforms:
        if not platform_connected(platform):
            all_connected = False
    return all_connected

def scan_for_platforms(timeout, scan_platforms=platforms):
    for entry in ble.start_scan(minimum_rssi=-120, timeout=timeout):
        for platform in scan_platforms:
            if not platform_connected(platform):
                name = entry.complete_name
                if name and name == f'time_{platform.name}':
                    print(f'found {platform.name} with {entry.rssi}')
                    platform.connection = ble.connect(entry)


def scan(failures):
    print('scanning for platforms')
    print('current failure count' + str(failures))
    timeout = (7 * failures) + 3
    for x in range(0, 5):
        if not all_connected():
            print("scan number" + str(x))
            scan_for_platforms(timeout, scan_platforms=disconnected_platforms)
            time.sleep(timeout + 1)
        ble.stop_scan()

failure_count = 0
client = setup_mqtt()
scan(failure_count)

while True:
    if not mqttConnected:
       client = setup_mqtt()

    if len(disconnected_platforms) > 1:
        failure_count += 1
        if failure_count > 3: reset_bt
        scan(failure_count, scan_platforms=disconnected_platforms)
    else:
        failure_count = 0

    for platform in platforms:
        if platform_connected(platform):
            uartsvc = platform.connection[UARTService]
            event = uartsvc.readline().decode("utf-8").rstrip()
            if len(event) > 1:
                evt = event.split(':')[1]
                channel = 'home-assistant/' + platform.name + '/occupied'
                print(channel + '|' + evt)
                client.publish(channel, evt)
