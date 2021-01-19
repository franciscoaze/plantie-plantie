"""
Arduino Real World Interface

Provides an interface between the commands sent from the UI or core modules and the arduino workers.
"""
import paho.mqtt.client as mqtt
import importlib, inspect
import serial
from pyplantie.utils.constants import ARDUINO_ACTUATORS_FILE, ARDUINO_SENSORS_FILE, ARDUINO_CLIENT_NAME, BROKER_ADDRESS, ARDUINO_USB_PORT
import threading
import atexit
import time
import json
from pyplantie.utils.mylogger import new_logger


class ArduinoClient:
    """
    Class that deals with incoming messages from mqtt broker on the subscribed topics and directs them to the arduino.
    Every arduino action is described in workers.arduino_actuators.

    """
    SUB_TOPICS = [('actions/#',1),('sensors/requests/#',1)]

    def __init__(self):
        # Configure logger
        self.logger = new_logger(name='arduino_rwi')
        # Get all actuators and sensors
        self.actuator_workers = {name: cls() for name, cls in inspect.getmembers(importlib.import_module(ARDUINO_ACTUATORS_FILE), inspect.isclass) if not name.startswith('_')}
        self.sensor_workers = {name: cls() for name, cls in inspect.getmembers(importlib.import_module(ARDUINO_SENSORS_FILE), inspect.isclass) if not name.startswith('_')}
        self.logger.info(f'Found {len(self.actuator_workers)} arduino actuators and {len(self.sensor_workers)} arduino sensors')

        self.client = mqtt.Client(ARDUINO_CLIENT_NAME)
        self.client.connect(BROKER_ADDRESS)
        self.client.subscribe(self.SUB_TOPICS)
        self.client.on_message = lambda client, userdata, msg: self.on_mqtt_message(client, userdata, msg)

        self.ser = serial.Serial(ARDUINO_USB_PORT, 115200, timeout=1)

        self.thread = threading.Thread(target=self.read_serial, args=())
        self.thread.start()
        self.client.loop_start()
        atexit.register(self.on_exit)

    def read_serial(self):
        """
        Non-blocking method to read incoming data from serial

        """
        while True:
            if self.ser.in_waiting > 0:
                data_str = self.ser.read(self.ser.in_waiting).decode('ascii').rstrip('\n')
                self.logger.info(f'Serial received: {data_str}')
                self.handle_incoming_serial(data_str)
            time.sleep(0.01)

    def handle_incoming_serial(self, reading):
        """
        Handles data coming from the Arduino
        
        note: As of now the only messages received from the arduino are temp and hum
        """
        try:
            indicator, values = reading.split(',', maxsplit=1)

            for worker in [self.sensor_workers[name] for name in self.sensor_workers if self.sensor_workers[name].indicator == indicator]:
                data = worker.process_sensor_data(values)
                worker.send_mqtt(self.client, data, self.logger)
        except:
            pass

    def on_mqtt_message(self, client, userdata, message):
        """
        Receives messages from mqtt queue
        """
        msg_dict = json.loads(message.payload)
        for worker in [self.actuator_workers[name] for name in self.actuator_workers if self.actuator_workers[name].sub_topic == message.topic]:
            self.logger.info(f'message:{msg_dict} - topic:{worker.sub_topic}')
            worker.send_serial(self.ser, msg_dict, self.logger)

        for worker in [self.sensor_workers[name] for name in self.sensor_workers if self.sensor_workers[name].sub_topic == message.topic]:
            self.logger.info(f'message:{msg_dict} - topic:{worker.sub_topic}')
            worker.send_serial(self.ser, msg_dict, self.logger)

    def on_exit(self):
        """
        Executes on function exit
        """
        self.client.loop_stop()
        self.logger.info("Exit Python application")


if __name__ == '__main__':
    ArduinoClient()