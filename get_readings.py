import serial
import os
import time
import pickle
import logger
from configuration.vars import USB_PORT
try:
    with open('.states.pickle', 'rb') as f:
        states = pickle.load(f)
except:
    states = {'LED': 'ON'}

ser = serial.Serial(USB_PORT, 115200, timeout=1)
ser.flush()
time.sleep(2)
ser.write(f"<\n>".encode('utf-8'))
line = ser.readline().decode('utf-8').rstrip().split(',')
print(line)
if line[0][0] == 'T':
    temp = float(line[0][1:])/100.0
    hum = float(line[1][1:])/100.0
logger.log_string(f'Temperature: {temp}, Humidity: {hum}', "READING")
