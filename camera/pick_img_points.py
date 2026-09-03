import os
import cv2

import multiprocessing
import matplotlib.pyplot as plt
import random
import sys


'''
python3 *.py [filename]
使用说明：
鼠标右键选点，键盘R撤销最后一个点。
选择点数>6个，关闭程序时自动保存txt
'''

def extract_points_2D(path):

    img = cv2.imread(path)
    disp = cv2.cvtColor(img.copy(), cv2.COLOR_BGR2RGB)



    # Setup matplotlib GUI
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_title('Select 2D Image Points')
    ax.set_axis_off()
    ax.imshow(disp)
    corners = []#存储选择的点

    colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple', 'brown', 'pink', 'gray', 'cyan']

    def onclick(event):
        if event.button!=3:
            return
        x = event.xdata
        y = event.ydata
        if (x is None) or (y is None): return

        # Display the picked point
        corners.append((x, y))
        print("IMG pick:", str(corners[-1]))

        ax.plot(x, y, 'o', color=colors[random.randint(0, 9)], label='Points')
        plt.text(x + 3,  # 文本x轴坐标
                 y - 3,  # 文本y轴坐标
                 s=f"{len(corners)}",
                 fontdict=dict(fontsize=12, color='r',
                               family='monospace',  # 字体,可选'serif', 'sans-serif', 'cursive', 'fantasy', 'monospace'
                               weight='normal',  # 磅值，可选'light', 'normal', 'medium', 'semibold', 'bold', 'heavy', 'black'
                               )  # 字体属性设置
                 )
        ax.figure.canvas.draw_idle()

    # 定义一个事件处理函数，用于处理键盘按键事件
    def on_key(event):
        print("Key pressed: {}".format(event.key))
        if event.key=='r':
            print("回复上一步")
            if len(corners)>0:
                last_point=corners.pop()
                print(f"删除的最后一个点坐标：{last_point}")
            ax.cla()
            ax.imshow(disp)


            for i,(x,y) in enumerate(corners):
                ax.plot(x, y, 'o', color=colors[random.randint(0, 9)], label='Points')
                plt.text(x + 3,  # 文本x轴坐标
                         y - 3,  # 文本y轴坐标
                         s=f"{i+1}",
                         fontdict=dict(fontsize=12, color='r',
                                       family='monospace',  # 字体,可选'serif', 'sans-serif', 'cursive', 'fantasy', 'monospace'
                                       weight='normal',
                                       # 磅值，可选'light', 'normal', 'medium', 'semibold', 'bold', 'heavy', 'black'
                                       )  # 字体属性设置
                         )
            ax.figure.canvas.draw_idle()

    # Display GUI
    fig.canvas.mpl_connect('button_press_event', onclick)
    # 绑定键盘按键事件到事件处理函数
    fig.canvas.mpl_connect('key_press_event', on_key)

    plt.show()

    print(corners)

    if (len(corners) >= 6):
        with open(os.path.join(os.path.dirname(path),"标靶2D.txt"),"w") as f:
            for corner in corners:
                f.write(f"{int(corner[0])} {int(corner[1])}\n")
    else:
        print('PnP Requires minimum 6 points')
        return

#extract_points_2D(r"F:\3.0TK-SEL\data\correct2\c1\1.jpg")

if __name__ == '__main__':
    if len(sys.argv)!=2:
        print("python3 *.py [filename]")
    else:
        input_path = sys.argv[1]
        print("输入的图片路径："+input_path)
        if not os.path.isfile(input_path):
            print(f"{input_path} 文件路径不存在！")
        else:
            # pick points
            img_p = multiprocessing.Process(target=extract_points_2D, args=[input_path])
            img_p.start()
            img_p.join()


