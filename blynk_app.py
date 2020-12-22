# Programa: Blynk com Raspberry Pi
# Autor: Arduino e Cia
import BlynkLib
import RPi.GPIO as GPIO
from gpiozero import CPUTemperature
from video_streaming import VideoStreamer
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
# Inicializa Blynk
blynk = BlynkLib.Blynk('83pa6ghaq1G40yxJrxqeOLAWFV9YTRN6')
import requests
from configuration.vars import USB_PORT
import serial
import time


URL = "http://192.168.1.80:8000"

ser = serial.Serial(USB_PORT, 115200, timeout=1)
ser.flush()
time.sleep(2)

pump_seconds = 1

@blynk.VIRTUAL_WRITE(0)
def control_video_stream(value):
    print('Valor de V0: {}'.format(value[0]))
    # Acende ou apaga o led vermelho, dependendo
    # do valor recebido
    try:
        if value[0] >= "1":
            r = requests.get(url = URL+'/video_on')
        else:
            r = requests.get(url=URL + '/video_off')
        print(r)
    except:
        print('no response')

# Registra os pinos virtuais
@blynk.VIRTUAL_WRITE(1)
def control_led(value):
    print('Valor de V1: {}'.format(value[0]))
    # Acende ou apaga o led vermelho, dependendo
    # do valor recebido
    if value[0] >= "1":
        GPIO.output(17,GPIO.HIGH)
    else:
        GPIO.output(17, GPIO.LOW)

# Camera ON/OFF

@blynk.VIRTUAL_READ(2)
def my_read_handler():
    # Envia o valor da temperatura da CPU
    cpu = CPUTemperature()
    print(cpu.temperature)
    blynk.virtual_write(2, cpu.temperature)

@blynk.VIRTUAL_WRITE(3)
def control_grow_led(value):
    print(' V3: {}'.format(value[0]))
    # Acende ou apaga o led vermelho, dependendo
    # do valor recebido
    if value[0] >= "1":
        ser.write(f"<LED,{255}\n>".encode('utf-8'))
        ser.flush()
        print('GROW LED OFF')
    else:
        ser.write(f"<LED,{0}\n>".encode('utf-8'))
        ser.flush()
        print('GROW LED ON')

@blynk.VIRTUAL_WRITE(4)
def control_led(value):
    print(' V4: {}'.format(value[0]))
    # Acende ou apaga o led vermelho, dependendo
    # do valor recebido
    if value[0] >= "1":
        print(f"<PUMP,{pump_seconds}\n>".encode('utf-8'))
        ser.write(f"<PUMP,{PUMP_SECONDS}\n>".encode('utf-8'))
        ser.flush()

@blynk.VIRTUAL_WRITE(5)
def control_led(value):
    print(' V5: {}'.format(value[0]))
    global pump_seconds
    # Acende ou apaga o led vermelho, dependendo
    # do valor recebido
    pump_seconds = value[0]

while True:
    blynk.run()