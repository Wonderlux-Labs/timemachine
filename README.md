# timemachine
Semi organized repo of all code used for Dance Dance Time Machine

## Implementation/Physical Realities

### Platforms

4 platforms that use Circuit Playground Bluetooth boards with homemade pressure sensors attached. Send messages to the bluetooth listener running on another raspi which can then dispatch events via MQTT.

### Controller

Main control being done with Home Assistant because it is rock solid for realtime monitoring of many different things and I already know my way around it

### Media

Two projectors - each on a separate raspberry pi running LibreElec
Sound - Comes out of Controller to speakers
Lightform projection mapper controlled by mqtt to OSC

### Automations

Lights, Led animations, smart plugs for floods and smoke machines, etc - all handled with Home Assistant scripting

### LEDs

Pixelblaze controllers controlled via websocket and/or home assistant
Arduinos driving WS2812
