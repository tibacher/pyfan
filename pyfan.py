import subprocess
import time
import matplotlib.pyplot as plt
from FAN_CONFIG import *


def get_sensor_temp(hw_path, sensor_number, string_pattern="temp{}_input"):
    cmd = ["cat", hw_path + "/" + string_pattern.format(sensor_number)]
    temp = int(subprocess.check_output(cmd).strip().decode()) / 1000.
    return temp


def get_sensor_fanspeed(hw_path, sensor_number, string_pattern="fan{}_input"):
    cmd = ["cat", hw_path + "/" + string_pattern.format(sensor_number)]
    speed = int(subprocess.check_output(cmd).strip().decode())
    return speed


def mean_cpu_temp(hw_path, sensor_numbers=[2, 3, 4, 10, 11, 12]):
    cpu_temps = []
    for sensor_number in sensor_numbers:
        cpu_temps.append(get_sensor_temp(hw_path, sensor_number))
    temp_mean = float(sum(cpu_temps) / len(sensor_numbers))
    return temp_mean


def max_cpu_temp(hw_path, sensor_numbers=[2, 3, 4, 10, 11, 12]):
    cpu_temps = []
    for sensor_number in sensor_numbers:
        cpu_temps.append(get_sensor_temp(hw_path, sensor_number))
    temp_max = max(cpu_temps)
    return temp_max


def set_fanspeed(hw_path, pwm_number, pwm_value):
    set_config(hw_path, pwm_number)
    write_pwm_file(hw_path, pwm_number, pwm_value, "pwm{}")


# PWM Configuration...

def set_pwm_enable(hw_path, pwm_number, value="1"):
    write_pwm_file(hw_path, pwm_number, value, "pwm{}_enable")


def set_pwm_mode(hw_path, pwm_number, value="1"):
    write_pwm_file(hw_path, pwm_number, value, "pwm{}_mode")


def set_pwm_step(hw_path, pwm_number, value="1"):
    write_pwm_file(hw_path, pwm_number, value, "pwm{}_step_output")


def set_pwm_start(hw_path, pwm_number, value="10"):
    write_pwm_file(hw_path, pwm_number, value, "pwm{}_start_output")


def set_pwm_stop(hw_path, pwm_number, value="10"):
    write_pwm_file(hw_path, pwm_number, value, "pwm{}_stop_output")


def set_pwm_target(hw_path, pwm_number, value="60000"):
    write_pwm_file(hw_path, pwm_number, value, "pwm{}_target")


def set_pwm_tolerance(hw_path, pwm_number, value="3000"):
    write_pwm_file(hw_path, pwm_number, value, "pwm{}_tolerance")


def write_pwm_file(hw_path, pwm_number, value, string_pattern):
    file = open(hw_path + "/" + string_pattern.format(pwm_number), "w")
    file.write(str(value))
    file.close()


def set_config(hw_path, pwm_number):
    set_pwm_enable(hw_path, pwm_number, "1")
    set_pwm_mode(hw_path, pwm_number, "1")
    # set_pwm_step(hw_path, pwm_number, "1")
    # set_pwm_start(hw_path, pwm_number, "10")
    # set_pwm_stop(hw_path, pwm_number, "10")
    # set_pwm_target(hw_path, pwm_number, "60000")
    # set_pwm_tolerance(hw_path, pwm_number, "3000")


def reset_fan_config(hw_path, pwm_number):
    set_pwm_enable(hw_path, pwm_number, "2")
    set_pwm_mode(hw_path, pwm_number, "1")


def plot_fan_speeds(hw_path, fan_numbers=range(1, 5)):
    for fan_number in fan_numbers:
        real_speeds = []
        fan_speeds = list(range(256))
        fan_speeds.reverse()
        # seconds to max speed
        t_end = time.time() + 10
        while time.time() < t_end:
            set_fanspeed(hwmon7, fan_number, fan_speeds[0])

        for speed in fan_speeds:
            real_speed = get_sensor_fanspeed(hw_path, fan_number)
            real_speeds.append(real_speed)
            # print(real_speed)
            t_end = time.time() + 0.2
            while time.time() < t_end:
                set_fanspeed(hwmon7, fan_number, speed)
                time.sleep(.05)
        print(real_speeds)
        fan_speeds.reverse()
        plt.figure()
        plt.plot(fan_speeds, real_speeds)
    plt.show()


def control_fans(fan_numbers=[1, 2, 3, 4], old_pwm_values=None):
    pwm_values = {}
    for fan_number in fan_numbers:
        if eval("FAN{}_ENABLE".format(fan_number)):
            hw_path = eval("FAN{}_HW".format(fan_number))
            hw_temp = eval("FAN{}_HW_TEMP".format(fan_number))
            hw_temp_sensors = eval("FAN{}_HW_TEMP_SENSOR".format(fan_number))
            min_pwm = eval("FAN{}_MIN_PWM ".format(fan_number))
            max_pwm = eval("FAN{}_MAX_PWM ".format(fan_number))
            min_temp = eval("FAN{}_MIN_TEMP".format(fan_number))
            max_temp = eval("FAN{}_MAX_TEMP".format(fan_number))

            temp = max_cpu_temp(hw_temp, hw_temp_sensors)

            fanpwm = max(min_pwm,
                         min(max_pwm, min_pwm + ((temp - min_temp) * (max_pwm - min_pwm)) / (max_temp - min_temp)))
            # print(int(fanpwm))

            if old_pwm_values is not None:
                alpha = 0.82 # smoothing value
                fanpwm = int(old_pwm_values[fan_number] * alpha + fanpwm * (1 - alpha))
            pwm_values[fan_number] = int(fanpwm)
            set_fanspeed(hw_path, fan_number, int(fanpwm))
    return pwm_values


def fan_control_service(fan_numbers=[1, 2, 3, 4],DEBUG=False):
    old_values = None
    while True:
        old_values = control_fans(fan_numbers, old_values)
        time.sleep(3)
        if DEBUG:
            print("mean: {0:.2f}°C".format(mean_cpu_temp(hwmon0)) + "\t" + "max: {0:.2f}°C".format(
                max_cpu_temp(hwmon0)))
            print("pwmvalues:")
            print(old_values)
