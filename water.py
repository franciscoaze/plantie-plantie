import serial
import os
import time
import pickle
import logger
from configuration.vars import PUMP_SECONDS

# Connecting to Arduino
ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
ser.flush()
time.sleep(2)

ser.write(f"<PUMP,{PUMP_SECONDS}\n>".encode('utf-8'))
ser.flush()
logger.log_string(f'Turning ON PUMP for {PUMP_SECONDS} seconds.', "ACTION")

ser.close()