import BlynkLib
import RPi.GPIO as GPIO
from gpiozero import CPUTemperature
import requests
import time
from pyplantie.utils.constants import BROKER_ADDRESS, VIDEO_URL, BLYNK_CLIENT_NAME
import paho.mqtt.client as mqtt
import json

from pyplantie.workers.arduino_actuators import GrowLed, Pump1, Pump2, Servo
from pyplantie.workers.raspberry_actuators import WhiteLED
from pyplantie.workers.raspberry_sensors import InternalTemp
from pyplantie.workers.arduino_sensors import BME208

SUB_TOPICS = [('sensors/#', 1)]

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
blynk = BlynkLib.Blynk('83pa6ghaq1G40yxJrxqeOLAWFV9YTRN6')

client = mqtt.Client(BLYNK_CLIENT_NAME)
client.connect(BROKER_ADDRESS)
client.subscribe(SUB_TOPICS)
client.on_message = lambda client, userdata, msg: on_mqtt_message(client, userdata, msg)

pump_seconds = 1

def on_mqtt_message(client, userdata, message):
    topic = message.topic
    msg_dict = json.loads(message.payload)
    if topic == InternalTemp.pub_topic:
        send_cpu_temp(msg_dict)
    elif topic == BME208.pub_topic:
        send_hum_temp(msg_dict)

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
        payload=json.dumps(msg),
        qos=0)


@blynk.VIRTUAL_READ(2)
def send_cpu_temp(value):
    """
    Sends the cpu temp value received from the internal temp topic
    """
    blynk.virtual_write(2, value.get('temperature'))


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
        msg = {"value": "0"}
        print('GROW LED OFF')

    client.publish(
        topic=GrowLed.sub_topic,
        payload=json.dumps(msg),
        qos=0)

@blynk.VIRTUAL_WRITE(4)
def control_pump2(value):
    """
    Control bottom pump
    """
    print(' V4: {}'.format(value[0]))
    if value[0] >= "1":
        msg = {'value': pump_seconds}

        client.publish(
            topic=Pump2.sub_topic,
            payload=json.dumps(msg),
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
        payload=json.dumps(msg),
        qos=0)


@blynk.VIRTUAL_READ(7)
def send_hum_temp(value):
    """
    Sends the hum temp value received from the hum temp topic
    """
    blynk.virtual_write(7, value.get('temperature'))

while True:
    blynk.run()