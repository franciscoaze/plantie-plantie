"""
Raspberry Pi Real World Interface

Provides an interface between the commands sent from the UI or core modules and the rpi workers.
"""
import paho.mqtt.client as mqtt
import importlib, inspect
from pyplantie.utils.constants import RPI_ACTUATORS_FILE, RPI_SENSORS_FILE, RPI_CLIENT_NAME, BROKER_ADDRESS
import threading
import atexit
import time
import json
from pyplantie.utils.mylogger import new_logger


class RPIClient:
    """
    Class that deals with incoming messages from mqtt broker on the subscribed topics and directs them to the RPI gpio pins.
    Every arduino action is described in workers.raspberry_actuators.

    """
    SUB_TOPICS = [('actions/#', 1), ('sensors/requests/#', 1)]

    def __init__(self):
        # Configure logger
        self.logger = new_logger(name=RPI_CLIENT_NAME)

        self.client = mqtt.Client(RPI_CLIENT_NAME)
        self.client.connect(BROKER_ADDRESS)
        self.client.subscribe(self.SUB_TOPICS)
        self.client.on_message = lambda client, userdata, msg: self.on_mqtt_message(client, userdata, msg)

        # Get all actuators and sensors
        self.actuator_workers = {name: cls(self.client, self.logger) for name, cls in
                                 inspect.getmembers(importlib.import_module(RPI_ACTUATORS_FILE), inspect.isclass) if
                                 not name.startswith('_')}
        self.sensor_workers = {name: cls(self.client, self.logger) for name, cls in
                               inspect.getmembers(importlib.import_module(RPI_SENSORS_FILE), inspect.isclass) if
                               not name.startswith('_')}
        self.logger.info(f'Found {len(self.actuator_workers)} RPI actuators and {len(self.sensor_workers)} RPI sensors')

        atexit.register(self.on_exit)

    def start(self):
        self.client.loop_forever()

    def on_mqtt_message(self, client, userdata, message):
        """
        Receives messages from mqtt queue
        """
        msg_dict = json.loads(message.payload)
        for worker in [self.actuator_workers[name] for name in self.actuator_workers if
                       self.actuator_workers[name].sub_topic == message.topic]:
            self.logger.info(f'message:{msg_dict} - topic:{worker.sub_topic}')
            worker.execute(msg_dict, self.logger)

        for worker in [self.sensor_workers[name] for name in self.sensor_workers if
                       self.sensor_workers[name].sub_topic == message.topic]:
            self.logger.info(f'message:{msg_dict} - topic:{worker.sub_topic}')
            worker.execute(msg_dict, self.client, self.logger)

    def on_exit(self):
        """
        Executes on function exit
        """
        self.client.loop_stop()
        self.logger.info("Exit Python application")


if __name__ == '__main__':
    rpi_rwi = RPIClient()
    rpi_rwi.start()