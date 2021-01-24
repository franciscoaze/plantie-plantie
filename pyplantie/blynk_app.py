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
from pyplantie.utils.mylogger import new_logger
import logging

SUB_TOPICS = [('sensors/#', 1)]

logging.getLogger('BlynkLog').setLevel(logging.DEBUG)
logger = new_logger(name=BLYNK_CLIENT_NAME, extra_handlers=["BlynkLog"])

GPIO.setmode(GPIO.BCM)

blynk = BlynkLib.Blynk('dEI_FInM4Af6bjoJ2hDQOvFPLQvSxQpU', server='127.0.1.1', port=8080)
pump_seconds = 1


def on_mqtt_message(client, userdata, message):
    logger.info(f'Received {message.payload} from {message.topic}')
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
    logger.info('Valor de V1: {}'.format(value[0]))

    if value[0] >= "1":
        msg = {"value": "ON"}
    else:
        msg = {"value": "OFF"}

    client.publish(
        topic= WhiteLED.sub_topic,
        payload=json.dumps(msg),
        qos=0)


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
    logger.info(' V3: {}'.format(value[0]))

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
    logger.info(' V4: {}'.format(value[0]))
    if value[0] >= "1":
        msg = {'value': pump_seconds}

        client.publish(
            topic=Pump2.sub_topic,
            payload=json.dumps(msg),
            qos=0)


@blynk.VIRTUAL_WRITE(5)
def control_pump_seconds(value):
    logger.info(' V5: {}'.format(value[0]))
    global pump_seconds
    # Acende ou apaga o led vermelho, dependendo
    # do valor recebido
    pump_seconds = value[0]


@blynk.VIRTUAL_WRITE(6)
def control_servo(value):
    logger.info(' V6: {}'.format(value[0]))
    msg = {'value': value[0]}

    client.publish(
        topic=Servo.sub_topic,
        payload=json.dumps(msg),
        qos=0)


def send_hum_temp(value):
    """
    Sends the hum temp value received from the hum temp topic
    """
    blynk.virtual_write(7, value.get('T'))
    blynk.virtual_write(8, value.get('H'))
    logger.info(f'Updated temps to {value}')


client = mqtt.Client(BLYNK_CLIENT_NAME)
client.connect(BROKER_ADDRESS)
client.subscribe(SUB_TOPICS)
client.on_message = on_mqtt_message


while True:
    client.loop_forever()
    blynk.run()