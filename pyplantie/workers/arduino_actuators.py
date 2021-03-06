"""
Contains all the arduino workers actuators definitions
"""
import copy


class _ArduinoActuator(object):

    def __init__(self, mqtt_client, logger):
        self.client = mqtt_client
        self.logger = logger

    def send_serial(self, serial_connection, msg, logger):
        template = copy.deepcopy(self.serial_format)
        alt_msg = template.replace("#value#", str(msg.get('value')))
        logger.info(f'Sending serial: {alt_msg}')
        serial_connection.write(alt_msg.encode('utf-8'))
        serial_connection.flush()


class Pump1(_ArduinoActuator):
    sub_topic = "actions/pump1"
    serial_format = "<PUMP1,#value#>"


class Pump2(_ArduinoActuator):
    sub_topic = "actions/pump2"
    serial_format = "<PUMP2,#value#>"


class GrowLed(_ArduinoActuator):
    sub_topic = "actions/growled"
    serial_format = "<LED,#value#>"


class Servo(_ArduinoActuator):
    sub_topic = "actions/servo"
    serial_format = "<SERVO,#value#>"
