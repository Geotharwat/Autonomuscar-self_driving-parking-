from maneuver import calculateManuever
import rpigpioemul as GPIO
import wheels

if __name__ == "__main__":
    try:
        manuever = calculateManuever(10)
        rev = []
        for movement in manuever:
            print(movement.speed, movement.steering)
            wheels.moveExact(movement.speed*30, movement.steering, movement.displacement)
            rev.append(movement)
            # time.sleep(10)
        # while len(rev) > 0:
        #     print(movement.speed, movement.steering)
        #     movement = rev.pop()
        #     moveExact(-movement.speed*100, -movement.steering, movement.displacement)
      
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()
