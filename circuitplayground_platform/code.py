import time
import analogio
import board

from adafruit_circuitplayground.bluefruit import cpb
from colorlist import COLORS, BLUES
from platform_name import PLATFORM_NAME, PLATFORM_NUMBER
import adafruit_fancyled.adafruit_fancyled as fancy

# set up BLE
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

advertised = False
connected = False
msg = f'{PLATFORM_NAME}: no events'
msg_changed = True

ble = BLERadio()
uart = UARTService()
advertisement = ProvideServicesAdvertisement(uart)
ble.name = 'time_' + PLATFORM_NAME

def advertise():
    global msg
    global msg_changed
    global advertised
    global connected
    global leds

    if not advertised:
        ble.start_advertising(advertisement)
        print("Waiting for connection.")
        advertised = True

    if not connected and ble.connected:
        print("Connection received.")
        connected = True
        leds = 'resting'

    if counter % 1000 == 0:
        if not ble.connected:
            print('trying again')
            ble.stop_advertising()
            advertised = False
            connected = False

    if connected and msg_changed:
        uart.write(msg)
        msg_changed = False

def showLeds(color, color_two=None, gamma=2.7, brightness=0.2):
    if color_two:
        colors = [fancy.mix(color, color_two, i / 9) for i in range(10)]
        adjusted = fancy.gamma_adjust(colors, brightness=brightness)
        for i in range(10):
            cpb.pixels[i] = adjusted[i].pack()
    else:
        color = fancy.gamma_adjust(color, brightness=brightness)
        for i in range(10):
            cpb.pixels[i] = color.pack()

    cpb.pixels.show()

def offlineLeds():
    showLeds(COLORS[0], brightness = 0.2)

def mapRange(x, offset_size, min_brightness, max_brightness):
    portion = (x * (max_brightness-min_brightness)) / (offset_size)
    return portion + min_brightness

def breathingLeds(adjust_factor, speed, min, max):
    bright_adjust = mapRange(adjust_factor, speed, min, max)
    up = min + bright_adjust
    down = max - bright_adjust + min
    return [up, down]

resting_brightness_toggle = 'up'
def restingLeds(counter):
    global resting_brightness_toggle
    speed = 200
    min_brightness = 0.02
    max_brightness = 0.3
    adjust_factor = counter % speed
    if adjust_factor == 0:
        resting_brightness_toggle = not resting_brightness_toggle
    bright_adjust = breathingLeds(adjust_factor, speed, min_brightness, max_brightness)
    if resting_brightness_toggle:
        brightness = bright_adjust[0]
    else:
        brightness = bright_adjust[1]
    color = BLUES[0]
    showLeds(color, brightness=brightness)

activated_brightness_toggle = True
def activatedLeds(counter):
    global activated_brightness_toggle
    speed = 10
    min_brightness = 0.5
    max_brightness = 1
    adjust_factor = counter % speed
    if adjust_factor == 0:
        activated_brightness_toggle = not activated_brightness_toggle
    bright_adjust = breathingLeds(adjust_factor, speed, min_brightness, max_brightness)
    if activated_brightness_toggle:
        brightness = bright_adjust[0]
    else:
        brightness = bright_adjust[1]
    color = COLORS[PLATFORM_NUMBER]
    showLeds(color, brightness=brightness)

def getAvgVoltage(pin=analogio.AnalogIn(board.A1), numSamples=1000):
    samples = [0] * numSamples
    for i in range(numSamples):
        samples[i] = pin.value
    return (sum(samples) / len(samples))

def getOffVoltage():
    time.sleep(2)
    off1 = getAvgVoltage()
    off2 = getAvgVoltage()
    off3 = getAvgVoltage()
    return ((off1 + off2 + off3) / 3)

offV = 0
activated = False
hitCount = 0
offCount = 0
offset = 0
sound_ready = False

def play_sound(file):
    global sound_ready
    cpb.play_file(file)
    sound_ready = False

def reset_globals(activated):
    global leds
    global offCount
    global hitCount
    global msg_changed
    global msg
    global sound_ready

    if activated:
        leds = 'activated'
        msg = 'platform_one:occupied'
    else:
        leds = 'resting'
        msg = 'platform_one:empty'

    offCount = 0
    hitCount = 0
    msg_changed = True
    sound_ready = True

def activate():
    global activated

    if not activated:
        activated = True
        reset_globals(activated)

def deactivate():
    global activated

    if activated:
        activated = False
        reset_globals(activated)

def platform_occupied(currentV, offV):
    return abs(0 - currentV) < abs(offV - currentV)

def mean(samples):
    return sum(samples) / len(samples)

def show_leds(activated, connected, counter):
    if activated:
        activatedLeds(counter)
    elif not connected:
        offlineLeds()
    else:
        restingLeds(counter)

def make_noise(activated):
    if activated:
        play_sound('sounds/platform_on.wav')
    else:
        play_sound('sounds/platform_off.wav')

samples = []
sample_size = 10
offV = getOffVoltage()
currentVoltage = offV
counter = 1
while True:
    if offV == 0:
        offV = getOffVoltage()
        currentVoltage = offV

    advertise()
    show_leds(activated, connected, counter)
    if sound_ready:
        make_noise(activated)

    samples.append(getAvgVoltage())

    if len(samples) == sample_size:
        currentVoltage = mean(samples)
        samples = []

    if platform_occupied(currentVoltage, offV):
        if hitCount >= 3 and (not activated):
            activate()
        else:
            hitCount += 1
    else:
        if offCount >= 3 and activated:
            deactivate()
        else:
            offCount += 1

    counter += 1


