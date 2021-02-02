import os

TABLE_MODELS_FILE = os.getenv("TABLE_MODELS_FILE", "pyplantie.utils.table_models")
DATABASE_URL = os.getenv("DATABASE_URL", r"postgres://kquyqdfq:2C8rvf7n_45OmkluDyT9w-tacJP6pKWi@balarama.db.elephantsql.com:5432/kquyqdfq")
LOG_FILE = os.getenv("LOG_FILE", "logs/system_activity.log")
PUMP_SECONDS = os.getenv("PUMP_SECONDS", 3)
DB_WATCHER_MIN = os.getenv("DB_WATCHER_MIN", 1)

BROKER_ADDRESS = os.getenv("BROKER_ADDRESS", "192.168.1.80")

ARDUINO_USB_PORT = os.getenv("ARDUINO_USB_PORT", '/dev/ttyUSB0')
ARDUINO_ACTUATORS_FILE = os.getenv("ARDUINO_ACTUATORS_FILE", "pyplantie.workers.arduino_actuators")
ARDUINO_SENSORS_FILE = os.getenv("ARDUINO_SENSORS_FILE", "pyplantie.workers.arduino_sensors")
ARDUINO_CLIENT_NAME = os.getenv("ARDUINO_CLIENT_NAME", "Arduino-RWI")

RPI_ACTUATORS_FILE = os.getenv("RPI_ACTUATORS_FILE", "pyplantie.workers.raspberry_actuators")
RPI_SENSORS_FILE = os.getenv("RPI_SENSORS_FILE", "pyplantie.workers.raspberry_sensors")
RPI_CLIENT_NAME = os.getenv("RPI_CLIENT_NAME", "RPI-RWI")

JOBS_DEF_FILE = os.getenv("JOBS_DEF_FILE", "pyplantie.workers.jobs")
CORE_CLIENT_NAME = os.getenv("CORE_CLIENT_NAME", "Core-app")

VIDEO_URL = os.getenv("VIDEO_URL", "http://192.168.1.80:8000")
BLYNK_CLIENT_NAME = os.getenv("BLYNK_CLIENT_NAME", "Blynk-app")
BLYNK_SERVER_HOST = os.getenv("BLYNK_SERVER_HOST", '192.168.1.80')
BLYNK_SERVER_PORT = os.getenv("BLYNK_SERVER_PORT", '9443')
BLYNK_AUTH = os.getenv("BLYNK_AUTH", '2p5G4h1wANysfVDWthWi71DorXeAByTG')