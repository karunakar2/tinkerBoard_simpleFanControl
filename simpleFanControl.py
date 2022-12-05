#!/usr/bin/python
import os
import signal
import time
import warnings

#save the pid for later
try:
    #with tempfile.NamedTemporaryFile(delete=False) as file1:
    with open('/tmp/simpleFanControl.txt','w') as file1:
        file1.write(str(time.time()))
        file1.write(' : ')
        file1.write(str(os.getpid()))
        file1.write('\n')
except Exception as er:
    warnings.warn(er)

# notifications on linux
notifyTitle = 'sbcFanModule'
try:
    from gi import require_version
    require_version('Notify','0.7')
    from gi.repository import Notify as notify
    notify.init(notifyTitle)
except ModuleNotFoundError:
    notifyTitle = False
    warnings.warn("can't notify with gui, keep track personally")

# linux notify fuction
def postMe(caption):
    try:
        if notify.is_initted() or notify.init(notifyTitle):
            info = notify.Notification.new(notifyTitle,
                                           caption,
                                           'dialog-warning')
            info.set_timeout(notify.EXPIRES_DEFAULT)
            info.set_urgency(notify.Urgency.LOW)
            info.show()
    except Exception as e:
        print(e)
    warnings.warn(caption)

try:
    import ASUS.GPIO as GPIO
except Exception as er:
    warnings.warn(er)
    postMe('Fan stopped: cant get the control')
    raise Exception('ASUS GPIO module required')

# Basic configuration
#use 'gpio readall' on shell to get the 'CPU' to corresponding pin of interest
#239 is for blue wire aka control on pin number 32, pwm3 sitting between two blacks
## more info at serverbiz.co.kr/product-info/?vid=55
c_FAN = 239                 # gpio pin the fan is connected to, default #26
c_MIN_TEMPERATURE = 60      # temperature in degrees c when fan should turn on
c_TEMPERATURE_OFFSET = 5    # temperarute offset in degrees c when fan should turn off

# Advanced configuration
c_PWM_FREQUENCY = 100        # frequency of the pwm signal to control the fan with
# Variables: Do not touch!
c_TEMPERATURE_OFFSET = c_MIN_TEMPERATURE - c_TEMPERATURE_OFFSET
last_cpu = 0        # last measured cpu temperarute
last_gpu = 0
desired_fan = 0        # desired fan pwm signal in %
last_fan = 0        # last fan pwm signal in %

try:
    # Select pin reference
    GPIO.setmode(GPIO.ASUS)
    # Declare fan pin as output
    GPIO.setup(c_FAN, GPIO.OUT)
    # Setup pwm on fan pin
    fan = GPIO.PWM(c_FAN, c_PWM_FREQUENCY)
    # Setup fan pwm to start with 0 % duty cycle
    fan.start(0)
except Exception as er:
    print(er)
    postMe('Root permissions required')

# function to get the cpu temperarute
def getCPUTemp():
    f = open("/sys/class/thermal/thermal_zone0/temp")
    CPUTemp = f.read()
    f.close()
    return int(CPUTemp.replace("\n",""))/1000    # remove return from result, cast to int and divide by 1000

def getGPUTemp():
    f = open("/sys/class/thermal/thermal_zone1/temp")
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
        postMe('Fan stopped: system requested termination')
        self.thread_dont_terminate = False

# main function
if __name__ == '__main__':
    killer = GracefulKiller()    # get a GracefulKiller
    while killer.thread_dont_terminate:    # main loop
      try:
        cpu = getCPUTemp()                    # get cpu temperature
        gpu = getGPUTemp()
        if (cpu < c_TEMPERATURE_OFFSET and gpu < c_TEMPERATURE_OFFSET):    # check if temperature is low enough to turn off
            desired_fan = 0    # set desired fan speed to 0 aka off
        elif (cpu > c_MIN_TEMPERATURE or gpu > c_MIN_TEMPERATURE ):    # check if temperature exceeded the set level
            if ((cpu >= last_cpu or gpu >= last_gpu) and desired_fan < 100):    # check if temperature is rising or staying the same
                if (desired_fan < 30):    # fan was off and minimum speed is 30% duty cycle
                    desired_fan = 30
                else:    # increase speed, since we are not decreasing the temperature
                    desired_fan += 5
            elif ((cpu < last_cpu and gpu < last_gpu) and desired_fan > 30):    # only if everything cools we can decrease the speed
                desired_fan -= 5
        print("CPU: {:f} GPU: {:f} Fan: {:f}".format(cpu, gpu, desired_fan))
        if(desired_fan != last_fan):    # only change duty cycle when it changed
            last_fan = desired_fan
            fan.ChangeDutyCycle(desired_fan)

        last_cpu = cpu    # keep track of cpu temperature
        last_gpu = gpu    # keep track of cpu temperature
        time.sleep(5)    # sleep for 5 seconds
      except Exception as er:
        warnings.warn(er)
        break
    try:
        GPIO.cleanup()    # cleanup gpio's
    except Exception as er:
        warnings.warn("can't tidy GPIO")
        warnings.warn(er)

    if notifyTitle:
        postMe('Fan stopped: start manually from /bin/simpleFanControl.py')
        time.sleep(3)
        notify.uninit()
    warnings.warn("Fancontrol: Stopping fancontrol") # print exit message
