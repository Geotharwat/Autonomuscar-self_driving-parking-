from wheels.stabilizer import dump_tps, dump_time, dump_power, dump_target_tps, config as configStablizer
import rpigpioemul as GPIO
import wheels
import time
import csv
import numpy as np

try:
    tests = [
        (12.5, 1),
        (12.5, 0.6),
        (12.5, 0.3),
        (15, 1),
        (15, 0.6),
        (15, 0.3),
        (30, 1),
        (30, 0.6),
        (30, 0.3),
    ]
    for test in tests:
        configStablizer(test[0], test[1])
        start = time.time()
        wheels.steer(1)
        wheels.drive(60)
        time.sleep(1)
        wheels.brake(60)
        time.sleep(0.5)
        stack = np.column_stack((np.array([x - dump_time[0] for x in dump_time]), np.array(dump_target_tps), np.array(dump_tps), np.array(dump_power)))
        with open(f'stabilizer_dump_{test[0]}_{test[1]}.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Time","Target TPS", "TPS", "Power"])
            writer.writerows(stack)
        dump_time.clear()
        dump_power.clear()
        dump_target_tps.clear()
        dump_tps.clear()
        time.sleep(0.5)
        # Reset by pressing CTRL + C
except KeyboardInterrupt:
    GPIO.cleanup()
