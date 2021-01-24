import os

DATABASE_URL = os.getenv("DATABASE_URL", r"postgres://kquyqdfq:NbPlwIBv66TllqtVTlgjQUMtvBIaYfa6@balarama.db.elephantsql.com:5432/kquyqdfq")
LOG_FILE = os.getenv("LOG_FILE", "logs/system_activity.log")
PUMP_SECONDS = os.getenv("PUMP_SECONDS", 3)

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

VIDEO_URL = os.getenv("VIDEO_URL","http://192.168.1.80:8000")
BLYNK_CLIENT_NAME = os.getenv("BLYNK_CLIENT_NAME", "Blynk-app")