"""
Contains all the arduino workers sensors definitions
"""
import copy
import json

class _ArduinoSensor(object):
    sep = ","
    request_format = "<#value#>"

    def __init__(self, mqtt_client, logger):
        self.client = mqtt_client
        self.logger = logger

    def extra_processing(self, treated_data: dict) -> dict:
        return treated_data

    def process_sensor_data(self, data) -> dict:
        sep_data = data.split(self.sep)
        return self.extra_processing(dict(zip(self.data_format, sep_data)))

    def send_mqtt(self, client, final_data: dict, logger, qos=1):
        # alt_msg = copy.deepcopy(self.pub_format)
        # for key, val in final_data.items():
        #     alt_msg = alt_msg.replace(f"#{key}#", str(val))
        logger.info(f'Sending mqtt to topic {self.pub_topic}: {final_data}')
        client.publish(
            topic=self.pub_topic,
            payload=json.dumps(final_data),
            qos=qos)

    def send_serial(self, serial_connection, msg, logger):
        template = copy.deepcopy(self.request_format)
        alt_msg = template.replace("#value#", str(msg.get('value')))
        logger.info(f'Sending serial: {alt_msg}')
        serial_connection.write(alt_msg.encode('utf-8'))
        serial_connection.flush()


class BME208(_ArduinoSensor):
    indicator = "BME"
    data_format = ["T", "H"]
    pub_topic = 'sensors/arduino/temphum'
    sub_topic = "sensors/requests/BME"
    pub_format = {"T": 0, "H": 0}

    def extra_processing(self, treated_data: dict) -> dict:
        """
        Transform into percentage
        """
        return {key: float(val)/100.0 for key, val in treated_data.items()}

