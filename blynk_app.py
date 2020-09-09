# Programa: Blynk com Raspberry Pi
# Autor: Arduino e Cia
import BlynkLib
import RPi.GPIO as GPIO
from gpiozero import CPUTemperature

GPIO.setmode(GPIO.BCM)
# Define as GPIOs 14 e 18 como saida
GPIO.setup(17, GPIO.OUT)
# Inicializa Blynk
blynk = BlynkLib.Blynk('83pa6ghaq1G40yxJrxqeOLAWFV9YTRN6')

# Registra os pinos virtuais
@blynk.VIRTUAL_WRITE(1)
def my_write_handler(value):
    print('Valor de V1: {}'.format(value[0]))
    # Acende ou apaga o led vermelho, dependendo
    # do valor recebido
    if value[0] >= "1":
        GPIO.output(17,GPIO.HIGH)
    else:
        GPIO.output(17, GPIO.LOW)

# Camera ON/OFF
@blynk.VIRTUAL_WRITE(0)
def my_write_handler(value):
    print('Valor de V0: {}'.format(value[0]))
    # Acende ou apaga o led vermelho, dependendo
    # do valor recebido
    if value[0] >= "1":
        GPIO.output(17,GPIO.HIGH)
    else:
        GPIO.output(17, GPIO.LOW)

@blynk.VIRTUAL_READ(2)
def my_read_handler():
    # Envia o valor da temperatura da CPU
    cpu = CPUTemperature()
    print(cpu.temperature)
    blynk.virtual_write(2, cpu.temperature)


while True:
    blynk.run()