from machine import Pin, UART, time_pulse_us, PWM
from time import sleep 
import time


A =Pin(2, Pin.OUT)
B =Pin(3, Pin.OUT)
C =Pin(4, Pin.OUT)
D =Pin(5, Pin.OUT)
S =Pin(6, Pin.IN, Pin.PULL_UP)
trig= Pin(15, Pin.OUT)
echo = Pin(14, Pin.IN)
trig2= Pin(10, Pin.OUT)
echo2 = Pin(11, Pin.IN)
SOUND_SPEED =340
TRIG_PULSE_DURATION_US = 10
servo= PWM(Pin(16))
servo.freq(50)
uart = UART (0,9600, tx = Pin (0), rx=Pin(1))


stuck_timer = None

current="Manual"


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
    
def drift():
    A.value(0)
    B.value(1)
    C.value(0)
    D.value(0)

def s_angle(angle):
    duty= int(1000 + (angle/180) * 8000)
    servo.duty_u16(duty)
    sleep(0.2)
    

def eye_lens():
    trig.value(0)
    time.sleep_us(2)
    trig.value(1)
    time.sleep_us(TRIG_PULSE_DURATION_US)
    trig.value(0)
    
    try:
    
        duration= time_pulse_us(echo, 1, 30000)
        distance= SOUND_SPEED * duration / 20000
        
    
    except OSError:
        distance = 400
        
    time.sleep_ms(50)
    
    
    return distance

def back_lens():
    trig2.value(0)
    time.sleep_us(2)
    trig2.value(1)
    time.sleep_us(TRIG_PULSE_DURATION_US)
    trig2.value(0)
    
    try:
    
        duration= time_pulse_us(echo2, 1, 30000)
        distance= SOUND_SPEED * duration / 20000
        
    
    except OSError:
        distance = 400
        
    time.sleep_ms(50)
    
    
    return distance

def fl ():
    # Sweep small angles around center to detect object
    center = 90
    search_range = range(center - 30, center + 31, 10)
    detected = False
    closest_angle = center
    min_distance = 400

    for angle in search_range:
        s_angle(angle)
        sleep(0.05)
        d = eye_lens()

        if d < min_distance and d > 5:  # Valid detection
            min_distance = d
            closest_angle = angle
            detected = True

    # Track object by turning towards detected angle
    if detected:
        s_angle(closest_angle)
        print("Object at:", closest_angle, "Distance:", min_distance)

        if min_distance < 20:
            backward()
            sleep(0.1)
            stop()

        elif closest_angle < 80:
            right()
            sleep(0.05)
            stop()

        elif closest_angle > 100:
            left()
            sleep(0.05)
            stop()
        else:
            forward()
            sleep(0.05)
            stop()
    else:
        print("No object detected, stopping.")
        stop()
                    
                
                  

   
def obs():
    
    global stuck_timer
    
    front_d = eye_lens()
    back_d = back_lens()
    
    print("Front:", front_d, "| Back:", back_d)

    
    now = time.ticks_ms()
    if front_d < 50:
        if stuck_timer is None:
            stuck_timer = now
        elif time.ticks_diff(now, stuck_timer) > 5000:  
            print("Stuck too long: U-turning...")
            left(); sleep(0.5)
            stop()
            stuck_timer = None
            return
    else:
        stuck_timer = None 

    
    if front_d > 50 or front_d == -0.017:
        forward()
        return

    stop()

    angles = [30, 60, 90, 120, 150]
    
    #angles = [30, 45, 60, 75, 90, 105, 120, 135, 150]
    readings = []

    for angle in angles:
        s_angle(angle)
        sleep(0.3)
        readings.append(eye_lens())

    s_angle(90)
    
    right_d, mid_right, focus, mid_left, left_d = readings

    #right_d, mdrr, mid_right, mdrf, focus, mdlf, mid_left, mdll, left_d = readings
    
    best = max(readings)
    print (readings)
    
    if best > 50 or best == -0.017:
        if best == right_d:
            right(); sleep(0.22)    
        
        elif best == mid_right:
            right(); sleep(0.12) 
       
      
        elif best == left_d:
            left(); sleep(0.22)
            
        elif best == mid_left:
            left(); sleep(0.12)
            
        elif best == focus:
            forward(); sleep(0.12)
    
    
    
    elif back_d > 60:
        print("Reversing...")
        backward()
        sleep(back_d / 200.0)
        
        
        
    else:
        print("Boxed in, turning...")
        left(); sleep(0.1)

    stop()

                                   
def power():
    print("Power mode")
    cur = "off"
    while True:
        
       
        if cur == "off":
            stop()
            sleep(0.1)
            
        elif cur == "on":
            obs()
            sleep(0.001)
            
        
        
            
        if cur == "off" and S.value() == 0:
            cur = "on"
            print("on")
            
        elif cur == "on" and S.value() == 0:
            cur = "off"
            print("off")
        
            
        elif uart.any():                 
            data=uart.read()             
            data=data.decode().strip().upper()
            print (data)
            cur = "off"
            blue_tooth()
    



def blue_tooth():
    
    global current
     
    while True:
         
        if current == "obs":
             obs()
             
        elif current == "fl":
             fl()   
        
         
        if uart.any():                 
            data=uart.read()             
            data=data.decode().strip().upper()
            print (data)              
            
            if "OBS" in data:
                current = "obs" 
                
            elif ("FL" in data):
                current = "fl"
                
            elif ("STP" in data):
                current = "manual"
                stop()
                
            elif ("FWD" in data):
                current = "manual"
                forward()
               
                
            elif ("BWD" in data):
                current = "manual"
                backward()
                
            elif ("LFT" in data):
                current = "manual"
                left()
                
            elif ("RGT" in data):
                current = "manual"
                right()
            
            elif ("DFT" in data):
                current = "manual"
                drift()
                
        sleep(0.05)
        

power()
