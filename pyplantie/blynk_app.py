import BlynkLib
import requests
from pyplantie.utils.constants import BROKER_ADDRESS, VIDEO_URL, BLYNK_CLIENT_NAME, BLYNK_SERVER_HOST, BLYNK_SERVER_PORT,BLYNK_AUTH
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

blynk = BlynkLib.Blynk(BLYNK_AUTH)
pump_seconds = 1


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
    else:
        msg = {"value": "0"}

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
    pump_seconds = value[0]


@blynk.VIRTUAL_WRITE(6)
def control_servo(value):
    logger.info(' V6: {}'.format(value[0]))
    msg = {'value': value[0]}

    client.publish(
        topic=Servo.sub_topic,
        payload=json.dumps(msg),
        qos=0)

@blynk.VIRTUAL_WRITE(9)
def control_pump1(value):
    """
    Control bottom pump
    """
    logger.info(' V9: {}'.format(value[0]))
    if value[0] >= "1":
        msg = {'value': pump_seconds}

        client.publish(
            topic=Pump1.sub_topic,
            payload=json.dumps(msg),
            qos=0)


def send_hum_temp(value):
    """
    Sends the hum temp value received from the hum temp topic
    """
    blynk.virtual_write(7, value.get('T'))
    blynk.virtual_write(8, value.get('H'))
    logger.info(f'Updated temps to {value}')


@blynk.VIRTUAL_WRITE(10)
def control_table(value):
    """
    Control table widget
    """
    logger.info(' V9: {}'.format(value[0]))


id_val = 0
@blynk.VIRTUAL_WRITE(11)
def update_table(value):
    """
    Button to update table
    """
    global id_val
    logger.info(' V11: {}'.format(value[0]))
    if value[0] >= "1":
        if id_val == 5:
            blynk.virtual_write(10, 'clr')
            id_val=0
        else:
            blynk.virtual_write(10, 'add', id_val, "Name", "Value","other")
            blynk.virtual_write(10, 'pick', id_val)
            id_val += 1


client = mqtt.Client(BLYNK_CLIENT_NAME)
client.connect(BROKER_ADDRESS)
client.subscribe(SUB_TOPICS)
client.on_message = on_mqtt_message


while True:
    client.loop_start()
    blynk.run()
