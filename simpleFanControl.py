#!/usr/bin/python
import ASUS.GPIO as GPIO
import os
import signal
import time

# Basic configuration
#use 'gpio readall' on shell to get the 'CPU' to corresponding pin of interest
#239 is for blue wire aka control on pin number 32, pwm3 sitting between two blacks
## more info at serverbiz.co.kr/product-info/?vid=55
c_FAN = 239                 # gpio pin the fan is connected to, default #26
c_MIN_TEMPERATURE = 45      # temperature in degrees c when fan should turn on
c_TEMPERATURE_OFFSET = 2    # temperarute offset in degrees c when fan should turn off

# Advanced configuration
c_PWM_FREQUENCY = 50        # frequency of the pwm signal to control the fan with
# Variables: Do not touch!
c_TEMPERATURE_OFFSET = c_MIN_TEMPERATURE - c_TEMPERATURE_OFFSET
last_cpu = 0        # last measured cpu temperarute
desired_fan = 0        # desired fan pwm signal in %
last_fan = 0        # last fan pwm signal in %

# Select pin reference
GPIO.setmode(GPIO.ASUS)
# Declare fan pin as output
GPIO.setup(c_FAN, GPIO.OUT)
# Setup pwm on fan pin
fan = GPIO.PWM(c_FAN, c_PWM_FREQUENCY)
# Setup fan pwm to start with 0 % duty cycle
fan.start(0)

# function to get the cpu temperarute
def getCPUTemp():
    f = open("/sys/class/thermal/thermal_zone0/temp")
    CPUTemp = f.read()
    f.close()
    return int(CPUTemp.replace("\n",""))/1000    # remove return from result, cast to int and divide by 1000

# class helping with killing signals so gpio's can be cleaned up
class GracefulKiller:
    thread_dont_terminate = True
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.thread_dont_terminate = False

# main function
if __name__ == '__main__':
    killer = GracefulKiller()    # get a GracefulKiller
    while killer.thread_dont_terminate:    # main loop
      try:
        cpu = getCPUTemp()                    # get cpu temperature
        if (cpu < c_TEMPERATURE_OFFSET):    # check if temperature is low enough to turn off
            desired_fan = 0    # set desired fan speed to 0 aka off
        elif (cpu > c_MIN_TEMPERATURE ):    # check if temperature exceeded the set level
            if ((cpu >= last_cpu) and desired_fan < 100):    # check if temperature is rising or staying the same
                if (desired_fan < 30):    # fan was off and minimum speed is 30% duty cycle
                    desired_fan = 30
                else:    # increase speed, since we are not decreasing the temperature
                    desired_fan += 5
            elif (cpu < last_cpu and desired_fan > 30):    # only if everything cools we can decrease the speed
                desired_fan -= 5
            #print "CPU: %d HDD: %d Fan: %d RPM: %d" % (cpu, hdd, desired_fan, rpm)    # debug information
            print("CPU: {:f} Fan: {:f}".format(cpu, desired_fan))
        if(desired_fan != last_fan):    # only change duty cycle when it changed
            last_fan = desired_fan
            fan.ChangeDutyCycle(desired_fan)

        last_cpu = cpu    # keep track of cpu temperature
        rpm = 0            # reset rpm
        time.sleep(5)    # sleep for 5 seconds
      except Exception as er:
        print(er)
        break
    GPIO.cleanup()    # cleanup gpio's
    print ("Fancontrol: Stopping fancontrol") # print exit message
