from constants import RPI
print('RPI',RPI)

if True:
    from RPi.GPIO import *
else: 
    import random as r;
    HIGH = 1
    LOW = 0
    OUT = 0
    IN = 1
    BCM = "BCM"

    pinstate = {
        0: LOW
    }

    tristate = {
        0: OUT
    }
    class PWMC:
        def start(s):
            return None
        def stop():
            return None
            
    def setmode(mode: str):
        print(f"GPIO: mode set to {mode}")

    def setup(pin: int, state: int):
        global tristate
        if(tristate.get(pin) != state) :
            s = "OUT" if state == OUT else "IN"
            print(f"GPIO: setup pin({pin}) as {s}")
            tristate[pin] = state

    def output(pin: int,state: int):
        global pinstate
        if(pinstate.get(pin) != state) :
            s = "HIGH" if state == HIGH else "LOW"
            print(f"GPIO: pin({pin}) set to {s}");
            pinstate[pin] = state

    def PWM(pin, freq):
        return PWMC()
    def input(pin: int):
        global pinstate
        if(pinstate.get(pin) != None) :
            return pinstate.get(pin);
        return r.choice([HIGH, LOW]);

    def cleanup():
        print("GPIO: cleanup")