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
from pyplantie.utils.sql_client import ElephantSQL

import logging

SUB_TOPICS = [('sensors/#', 1)]

logging.getLogger('BlynkLog').setLevel(logging.DEBUG)
logger = new_logger(name=BLYNK_CLIENT_NAME, extra_handlers=["BlynkLog"])

blynk = BlynkLib.Blynk(BLYNK_AUTH)
pump_seconds = 1

menu_labels =[]

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


@blynk.VIRTUAL_WRITE(11)
def control_table_trigger(value):
    """
    Control table widget
    """
    logger.info(' V9: {}'.format(value[0]))


@blynk.VIRTUAL_WRITE(12)
def control_table_trigger(value):
    """
    Control table widget
    """
    logger.info(' V9: {}'.format(value[0]))


db_client = ElephantSQL()
NAME = 1
TRIGGER = 2
VALUE = 3
MODE = 5

@blynk.VIRTUAL_WRITE(10)
def update_table(value):
    """
    Button to update table
    """
    global menu_labels

    logger.info(' V10: {}'.format(value[0]))
    if value[0] >= "1":
        results = db_client.get_data(table='JOBS')
        idx = 0
        for res in results:
            name_id = res[NAME]
            trigger_args = res[TRIGGER]
            value = res[VALUE]
            # TABLE TRIGGER
            blynk.virtual_write(11, 'add', idx, name_id, trigger_args)
            # TABLE VALUE
            blynk.virtual_write(12, 'add', idx, name_id, value)
            idx += 1

        menu_labels = [res[NAME] for res in results]
        blynk.set_property(13, "labels", *menu_labels)


@blynk.VIRTUAL_WRITE(13)
def show_job(value):
    """
    activates when user chooses a menu option
    """
    global menu_labels
    logger.info(' V13: {}'.format(value))
    job_name = menu_labels[int(value[0])-1]
    result = db_client.get_data(
        table='JOBS',
        where_filter={"name_id=": job_name})[0]

    triggers = json.loads(result[TRIGGER])
    duration = result[VALUE]
    trigger_mode = result[MODE]
    if trigger_mode == 'cron':
        start, tz, days = triggers_to_timer(triggers)
        blynk.set_property(14, "label", job_name)
        blynk.set_property(15, 'label', "N/A")
        blynk.set_property(15, 'min', 0)
        blynk.set_property(15, 'max', 0)
        blynk.virtual_write(15, 0)
        blynk.virtual_write(14, start, start, tz, days)
        blynk.virtual_write(16, 255)
        blynk.virtual_write(17, 0)

    elif trigger_mode == 'interval':
        blynk.virtual_write(14, -1, 'Europe/Lisbon')
        if 'hours' in triggers:
            blynk.virtual_write(15, int(triggers.get('hours')))
        elif 'minutes' in triggers:
            blynk.virtual_write(15, int(triggers.get('minutes')))

        blynk.set_property(14, "label", "N/A")
        blynk.set_property(15, 'label', job_name)
        blynk.virtual_write(16, 0)
        blynk.virtual_write(17, 255)


def triggers_to_timer(triggers):
    tz = 'Europe/Lisbon'
    if triggers.get('day_of_week'):
        _days = triggers.get('day_of_week', '1,2,3,4,5,6,7')
        days = ','.join([str(int(i)+1) for i in _days.split(',')])
    else:
        days = '1,2,3,4,5,6,7'

    start = int(triggers.get('hour', 0)) * 60 * 60 + int(triggers.get('minute', 0))* 60
    logger.info(f'Start value is {start}')
    return start, tz, days

def on_start():
    global menu_labels

    results = db_client.get_data(table='JOBS')
    menu_labels = [res[NAME] for res in results]
    blynk.set_property(13, "labels", *menu_labels)



client = mqtt.Client(BLYNK_CLIENT_NAME)
client.connect(BROKER_ADDRESS)
client.subscribe(SUB_TOPICS)
client.on_message = on_mqtt_message


while True:
    client.loop_start()
    blynk.run()
    on_start()
