import paho.mqtt.client as mqtt
from pyplantie.utils.constants import BROKER_ADDRESS

SUB_TOPICS = [('actions/#', 1), ('sensors/requests/#', 1)]


class MQTTClient:

    def __init__(self, client_name: str):
        self.connected = False
        self.cli = mqtt.Client(client_name, clean_session=False)

        self.cli.subscribe(SUB_TOPICS)

        self.cli.on_connect = self.on_connect
        self.cli.on_disconnect = self.on_disconnect

        self.cli.connect(BROKER_ADDRESS)

    def start(self):
        self.cli.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        self.connected = True
        print('connected')

    def on_disconnect(self, client, userdata, rc):
        self.connected = False
        print('disconnected')
        self.cli.reconnect()
        