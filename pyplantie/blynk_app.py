import BlynkLib
import RPi.GPIO as GPIO
from gpiozero import CPUTemperature
import requests
from configuration.vars import USB_PORT
import serial
import time
from pyplantie.utils.constants import BROKER_ADDRESS, VIDEO_URL, BLYNK_CLIENT_NAME
import paho.mqtt.client as mqtt

from pyplantie.workers.arduino_actuators import GrowLed, Pump1, Pump2, Servo
from pyplantie.workers.raspberry_actuators import WhiteLED

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
blynk = BlynkLib.Blynk('83pa6ghaq1G40yxJrxqeOLAWFV9YTRN6')

client = mqtt.Client(BLYNK_CLIENT_NAME)
self.client.connect(BROKER_ADDRESS)

pump_seconds = 1

@blynk.VIRTUAL_WRITE(0)
def control_video_stream(value):
    print('Valor de V0: {}'.format(value[0]))
    try:
        if value[0] >= "1":
            r = requests.get(url=VIDEO_URL + '/video_on')
        else:
            r = requests.get(url=VIDEO_URL + '/video_off')
        print(r)
    except:
        print('no response')


@blynk.VIRTUAL_WRITE(1)
def control_led(value):
    """
    Controls the white camera led
    """
    print('Valor de V1: {}'.format(value[0]))

    if value[0] >= "1":
        msg = {"value": "ON"}
    else:
        msg = {"value": "OFF"}

    client.publish(
        topic= WhiteLED.sub_topic,
        payload=msg,
        qos=0)


@blynk.VIRTUAL_READ(2)
def my_read_handler():
    # Envia o valor da temperatura da CPU
    cpu = CPUTemperature()
    print(cpu.temperature)
    blynk.virtual_write(2, cpu.temperature)


@blynk.VIRTUAL_WRITE(3)
def control_grow_led(value):
    """
    Controls the grow led
    """
    print(' V3: {}'.format(value[0]))

    if value[0] >= "1":
        msg = {"value": "255"}
        print('GROW LED ON')
    else:
        msg = {"value": "255"}
        print('GROW LED OFF')

    client.publish(
        topic=GrowLed.sub_topic,
        payload=msg,
        qos=0)

@blynk.VIRTUAL_WRITE(4)
def control_pump(value):
    print(' V4: {}'.format(value[0]))
    # Acende ou apaga o led vermelho, dependendo
    # do valor recebido
    if value[0] >= "1":
        msg = {'value': pump_seconds}

    client.publish(
        topic=Pump2.sub_topic,
        payload=msg,
        qos=0)

@blynk.VIRTUAL_WRITE(5)
def control_pump_seconds(value):
    print(' V5: {}'.format(value[0]))
    global pump_seconds
    # Acende ou apaga o led vermelho, dependendo
    # do valor recebido
    pump_seconds = value[0]

@blynk.VIRTUAL_WRITE(6)
def control_servo(value):
    print(' V6: {}'.format(value[0]))
    msg = {'value': value[0]}

    client.publish(
        topic=Servo.sub_topic,
        payload=msg,
        qos=0)


while True:
    blynk.run()