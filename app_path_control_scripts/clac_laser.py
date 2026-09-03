import time

from Motor import Motor
from minMotor import MinMotor
import math




def computer_value(first_m_angle=0):
    while True:
        print("输入x返回上一级\n"
              "输入两个点的全站仪角度，用'.'隔开度分秒\n"
              )
        hz1_str = input("输入[点1]的hz: ")
        if hz1_str == "x":
            break
        v1_str = input("输入[点1]的v: ")
        if v1_str == "x":
            break
        hz2_str = input("输入[点2]的hz: ")
        if hz2_str == "x":
            break
        v2_str = input("输入[点2]的v: ")
        if v2_str == "x":
            break
        # dis_str = input("输入全站仪到墙壁的距离: ")
        # if dis_str == "x":
        #     break
        try:
            items=hz1_str.split(".")
            hz1=float(items[0])+float(items[1])/60+float(items[2])/3600
            items = v1_str.split(".")
            v1 = float(items[0]) + float(items[1]) / 60 + float(items[2]) / 3600
            items = hz2_str.split(".")
            hz2 = float(items[0]) + float(items[1]) / 60 + float(items[2]) / 3600
            items = v2_str.split(".")
            v2 = float(items[0]) + float(items[1]) / 60 + float(items[2]) / 3600
            #dis=float(dis_str)
            print(f"解析结果：\n"
                  f"点1：hz={hz1},v={v1};\n"
                  f"点2：hz={hz2},v={v2};\n")
                  #f"全站仪到墙壁的距离：{dis}\n")
            if v1>180:
                v1=360-v1
            if v2>180:
                v2=360-v2
            print((v2-v1)/2)
            v_dif=first_m_angle+(v2-v1)/2-90
            if v_dif<0:
                v_dif+=360
            if v_dif>360:
                v_dif-=360
            #dis_angle=2*math.atan(0.036/dis)/math.pi*180#通过距离反算需要补偿的角度
            #print("根据全站仪距离估算左右间距补偿角度：",dis_angle)
            #+dis_angle
            hz_dif=(hz2-hz1)/2#全站仪逆时针变小,已经验证过
            print("-----------------【标定结果】----------------------")
            print(f"实际0度时小电机编码器角度：{v_dif},水平方向偏角：{hz_dif}")
            print(f"\n\n\n")
        except:
            print("输入解析失败！！！")
            continue


def main_clac_progress():
    #没有考虑堵转的情况,需要手动解除  按流程操作不会堵转
    print("----------------------------------------------------------------------------------")
    print("-----------------【TK-SET设备】小电机交互式半自动标定程序v1.0.0-------------------------")
    print("----------------------------------------------------------------------------------")
    #开启激光灯
    with open('/proc/rp_power/laser', 'w') as f:
        f.write('1')
    # 开启小电机
    with open('/proc/rp_power/motor', 'w') as f:
        f.write('1')
    # 开启转台
    with open('/proc/rp_power/zt', 'w') as f:
        f.write('1')
    motor=Motor()
    motor.cmd_find_zero()
    #motor.cmd_set_position(0)
    mmotor=MinMotor()
    first_m_angle=0
    end_m_angle=180
    #主程序
    while True:
        print("-----------------------【程序主菜单】------------------------------\n",
              "[0].转动转台使设备与全站仪平行\n",
              "[1].转动小电机到大致水平位置（转动前将设备相机位置朝向墙面）\n",
              "[2].自动反转转台与小电机\n",
              "[3].计算偏移值\n",
              "[4].解除小电机堵转\n"
              "[5].测试找点功能（输入转台与小电机目标角度）\n"
              "[x].退出程序\n",
              )
        select = input("选择功能项: ")
        if select=="0":
            while True:
                print("输入x返回上一级\n"
                      "输入当前设备与全站仪的夹角参数\n",
                      )
                angle_str = input("输入: ")
                if angle_str=="x":
                    break
                else:
                    try:
                        angle=float(angle_str)
                        print("-----------------------转动转台角度------------------")
                        angle_dif=angle-90#TODO：这里可能要反过来，需要验证下
                        if angle_dif>360:
                            angle_dif-=360
                        elif angle_dif<0:
                            angle_dif += 360
                        motor.cmd_set_position(angle_dif)
                        print("当前转台角度：",motor.angle)
                    except:
                        print("输入解析失败！！！")
                        continue
        elif select=="1":
            while True:
                first_m_angle = mmotor.cmd_read_angle()  # 记录起始位置
                print("当前编码器绝对值：", first_m_angle)
                print("输入x返回上一级\n"
                      "输入数字为转动指定角度(设备屏幕，顺时针为正，逆时针为负)\n",
                      )
                angle_str = input("输入: ")
                if angle_str=="x":
                    break
                else:
                    try:
                        angle0=float(angle_str)
                        print("-----------------------转动小电机指定角度------------------")
                        mmotor.cmd_set_pos(angle0)
                        first_m_angle =mmotor.cmd_read_angle()#记录起始位置
                        print("当前编码器绝对值：",first_m_angle)
                    except Exception as e:
                        print("输入解析失败！！！")
                        print(e)
                        continue

        elif select=="2":
            motor.cmd_find_zero()
            print(f"转台当前角度：{motor.angle}")
            dist_angle=round(motor.angle,3)+180
            if dist_angle>360:
                dist_angle=dist_angle-360
            print(f"转台目标角度：{dist_angle}")
            motor.cmd_set_position(dist_angle)
            first_m_angle = mmotor.cmd_read_angle()  # 记录起始位置
            print("当前编码器绝对值：", first_m_angle)
            mmotor.cmd_set_pos(-180)
            end_m_angle =mmotor.cmd_read_angle()#记录结束位置
            print("当前编码器绝对值：", end_m_angle)
        elif select=="3":
            print("第一个点小电机编码器绝对值：",first_m_angle)
            computer_value(first_m_angle)
        elif select=="4":
            state=mmotor.cmd_reset_protect()
            if not state:
                print("解除堵转失败，重启小电机中...")
                # 开启小电机
                with open('/proc/rp_power/motor', 'w') as f:
                    f.write('0')
                time.sleep(2)
                with open('/proc/rp_power/motor', 'w') as f:
                    f.write('1')
                print("小电机重启完成，请注意转动方向！")
        elif select=="5":
            while True:
                print("输入x返回上一级\n")
                hz1_str = input("输入转台的目标角度: ")
                if hz1_str == "x":
                    break
                v1_str = input("输入小电机的目标角度: ")
                if v1_str == "x":
                    break
                try:
                    zt_angle=float(hz1_str)
                    print(f"------------------转台转动到{zt_angle}-------------")
                    motor.cmd_set_position(zt_angle)


                    motor_angle=float(v1_str)
                    print(f"------------------小电机转动到{motor_angle}-------------")
                    s_angle = mmotor.cmd_read_angle()  # 记录起始位置
                    print("当前编码器绝对值：", s_angle)
                    mmotor.cmd_set_pos(motor_angle-s_angle)

                except:
                    print("输入解析失败！！！")
                    continue


        elif select=="x":
            break
        else:
            print("输入项错误，请重新输入！！！")
            continue

















if __name__ == "__main__":
    main_clac_progress()
    #computer_value(302.217)
