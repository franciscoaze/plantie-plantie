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
vs = VideoStreamer()

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
@blynk.VIRTUAL_WRITE(0)
def control_video_stream(value):
    print('Valor de V0: {}'.format(value[0]))
    # Acende ou apaga o led vermelho, dependendo
    # do valor recebido
    if value[0] >= "1":
        vs.start_new_stream()
    else:
        vs.stop_stream()

@blynk.VIRTUAL_READ(2)
def my_read_handler():
    # Envia o valor da temperatura da CPU
    cpu = CPUTemperature()
    print(cpu.temperature)
    blynk.virtual_write(2, cpu.temperature)


while True:
    blynk.run()