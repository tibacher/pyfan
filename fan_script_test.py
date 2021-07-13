from pyfan import *

pwm_list = range(1, 5)
for pwm_number in pwm_list:
    set_fanspeed(hwmon7, pwm_number, "200")
    reset_fan_config(hwmon7, pwm_number)


#plot_fan_speeds(hwmon7,[4])


while True:
    set_fanspeed(hwmon7, 1, "0")
    set_fanspeed(hwmon7, 2, "65")
    set_fanspeed(hwmon7, 3, "50")
    set_fanspeed(hwmon7, 4, "0")   
    #set_fanspeed(hwmon7, 1, "0")
    #set_fanspeed(hwmon7, 2, "0")
    #set_fanspeed(hwmon7, 3, "0")
    #set_fanspeed(hwmon7, 4, "0")
    time.sleep(0.1)
ag