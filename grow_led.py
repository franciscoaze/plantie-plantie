import serial
import os
import time
import pickle
import logger
from configuration.vars import LOG_FILE

try:
    with open('.states.pickle', 'rb') as f:
        states = pickle.load(f)

except:
    states = {'LED': 'ON'}

print(states)
ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
ser.flush()
time.sleep(2)
if states['LED'] == "ON":
    # Then turn it off
    ser.write(f"<LED,{0}\n>".encode('utf-8'))
    ser.flush()
    states['LED'] = "OFF"
    logger.log_string('Turning OFF grow LED.', "ACTION")

else:
    # Then turn it off
    ser.write(f"<LED,{255}\n>".encode('utf-8'))
    ser.flush()
    states['LED']= "ON"
    logger.log_string('Turning ON grow LED.', "ACTION")

with open('.states.pickle', 'wb') as f:
    pickle.dump(states, f)
print('\t|\n\tv')
print(states)
ser.close()