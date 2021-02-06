from pyfan import *

pwm_list = range(1, 5)
for pwm_number in pwm_list:
    set_fanspeed(hwmon7, pwm_number, "10")
    reset_fan_config(hwmon7, pwm_number)

# plot_fan_speeds(hwmon7)
