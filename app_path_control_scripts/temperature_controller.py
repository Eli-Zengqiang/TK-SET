

import math
import time

import sys, getopt
# 电阻到温度
RAW1_DATA1_PATH= "/sys/bus/iio/devices/iio:device1/in_voltage0_raw"
RAW1_DATA2_PATH= "/sys/bus/iio/devices/iio:device1/in_voltage1_raw"

RAW2_DATA1_PATH= "/sys/bus/iio/devices/iio:device1/in_voltage2_raw"
RAW2_DATA2_PATH= "/sys/bus/iio/devices/iio:device1/in_voltage3_raw"

PWM1_DUTY_CYCLE_PATH= "/sys/class/pwm/pwmchip0/pwm0/duty_cycle"
PWM1_ENABLE_PATH= "/sys/class/pwm/pwmchip0/pwm0/enable"

PWM2_DUTY_CYCLE_PATH= "/sys/class/pwm/pwmchip1/pwm0/duty_cycle"
PWM2_ENABLE_PATH= "/sys/class/pwm/pwmchip1/pwm0/enable"

def get_temp_func(data):
    ADC_VREF=6.144
    VREF=3.3
    R1=10000.0
    SH_A = (1.154700980e-3)
    SH_B = (2.302299168e-4)
    SH_C = (1.008804359e-7)

    r = 0
    vol = 0
    pos = 1

    # 电压到电阻
    if data&0x8000 == 0 :
        #/* 正 */
        pos = 1
    else:
        #/* 负 */
        pos = -1
        data = data & 0x7fff

    vol = data
    vol = pos*vol/32768.0*ADC_VREF
    r = R1 * (vol / (VREF - vol))

    # 电阻到温度
    return (1.0 / (SH_A + SH_B * math.log(r) + SH_C * math.pow(math.log(r), 3)) - 273.15)

def get_temp_value(id=1):
    '''
    获取指定ID（1，2）的温度
    '''
    path1=RAW1_DATA1_PATH
    path2 = RAW1_DATA2_PATH
    if id!=1:
        path1 = RAW2_DATA1_PATH
        path2 = RAW2_DATA2_PATH
    r11=0
    r12=0
    with open(path1, "r") as f:
        r11=int(f.read().strip())
        print(r11)
    with open(path2, "r") as f:
        r12 = int(f.read().strip())
        print(r12)
    v1=get_temp_func(r11)
    v2=get_temp_func(r11)
    if v1>v2:
        return v2
    return v1


def run_temp_controller(id,temp_value):
    current_temp_value=get_temp_value(id)
    print(current_temp_value)
    path=PWM1_ENABLE_PATH
    if id!=1:
        path = PWM2_ENABLE_PATH

    with open(path, "w") as f:  # 开启加热
        f.write("1")
    print("开始加热")
    start=time.time()

    while True:
        time.sleep(2)
        current_temp_value = get_temp_value(id)
        print('current_temp_value:', current_temp_value)
        if current_temp_value>temp_value:
            break
    with open(path, "w") as f:  # 关闭加热
            f.write("0")
    print(f"关闭加热,加热到{current_temp_value}，用时{time.time()-start}")

if __name__ == "__main__":
    id=1
    set_value=60
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:t:", [])
    except getopt.GetoptError:
        print(' -i <id> -t <template_value>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('-i <id> -t <template_value>')
            sys.exit()
        elif opt in ("-i"):
            id = int(arg)
        elif opt in ("-t"):#获取是绝对0位还是相对0位
            set_value=float(arg)
    run_temp_controller(id,set_value)