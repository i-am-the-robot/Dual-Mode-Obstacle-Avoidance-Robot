from machine import Pin, UART, time_pulse_us, PWM
from time import sleep
import time


A =Pin(2, Pin.OUT)
B =Pin(3, Pin.OUT)
C =Pin(4, Pin.OUT)
D =Pin(5, Pin.OUT)
trig= Pin(15, Pin.OUT)
echo = Pin(14, Pin.IN)
SOUND_SPEED =340
TRIG_PULSE_DURATION_US = 10
servo= PWM(Pin(16))
servo.freq(50)

def forward():
    A.value(0)
    B.value(1)
    C.value(1)
    D.value(0)
    
    
def backward():
    A.value(1)
    B.value(0)
    C.value(0)
    D.value(1)
   
    
def left():
    A.value(1)
    B.value(0)
    C.value(1)
    D.value(0)
    
   
    
def right():
    A.value(0)
    B.value(1)
    C.value(0)
    D.value(1)
    
def stop():
    A.value(0)
    B.value(0)
    C.value(0)
    D.value(0)

def s_angle(angle):
    duty= int(1000 + (angle/180) * 8000)
    servo.duty_u16(duty)
    

def eye_lens():
    trig.value(0)
    time.sleep_us(2)
    trig.value(1)
    time.sleep_us(TRIG_PULSE_DURATION_US)
    trig.value(0)
    
    try
    
    duration= time_pulse_us(echo, 1, 30000)
    global distance
    distance= SOUND_SPEED * duration / 20000
    time.sleep_ms(100) #changed from 500
    
    except OSError:
        distance = 100
    
    
    return distance



   
def obs():
    
    while True:
        distance = eye_lens()
        print("Distance: ",distance)
        
        if distance >= 40:
            forward()
            
        else:
            stop()
            s_angle(30)
            sleep(0.5)
            right_d =eye_lens()
            
            if right_d >= 40:
                s_angle(90)
                right()
                sleep(0.4)
                stop()
                
            else:
                #stop()
                s_angle(150)
                sleep(0.5)
                left_d =eye_lens()
                
                if left_d >= 40:
                    s_angle(90)
                    left()
                    sleep(0.4)
                    stop()
                   
                    
                else:
                    s_angle(90)
                    sleep(1)
                    backward()
                    sleep(0.5)
                    stop()
                    sleep(0.5)
                    back_d =eye_lens()
                    
                    
                    if back_d <= 45:
                        s_angle(90)
                        left()
                        sleep(0.9)
                        stop()
                    
                    #if back_d <= 35:
                        
                    
        sleep(0.1)
        
obs()
                    
