import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.colorbar import ColorbarBase
import matplotlib as mpl


def computer_dis(x, y, z, i):
    Tx = [-1.3949,1.0042,-0.0967]    #Tx：0号楼设站坐标
    Ty = [0.6125,0.6087,-0.0930]     #Ty：1号楼设站坐标
    Tz = [-0.2184,1.7264,-0.0032]    #Tz：2号楼设站坐标

    '''
    计算到0,0,0的距离
    :param x:
    :param y:
    :param z:
    :return:
    '''
    return np.sqrt((x - Tx[int(i)]) ** 2 + (y - Ty[int(i)]) ** 2 + (z - Tz[int(i)]) ** 2)


def computer_signal_npz_std(i, npz_path=r"npy文件\1号楼\1号楼radar0.0_20.2.npy"):
    '''
    计算单个npz文件不同距离点的误差
    :return:
    '''
    #loaded_arr=[]
    loaded_arrs = np.load(npz_path)

    if len(loaded_arrs.shape)==1:
        loaded_arr=loaded_arrs.reshape(len(loaded_arrs)//4,4)
    else:
        loaded_arr=loaded_arrs



   # loaded_arr.extend(loaded_arrs[:, 3])
    label_dict = {"<10": [], "10-20": [], "20-40": [], ">40": []}
    i
    for point in loaded_arr:
        dis = computer_dis(point[0], point[1], point[2], i)
        if dis < 10:
            label_dict["<10"].append(point)
        elif dis >= 10 and dis < 20:
            label_dict["10-20"].append(point)
        elif dis >= 20 and dis < 40:
            label_dict["20-40"].append(point)
        else:
            label_dict[">40"].append(point)
    out_std = {}
    for key in label_dict.keys():
        pts = np.array(label_dict[key])
        if len(pts) == 0:
            out_std[key] = {"mean": -999, "max": -999, "std": 0.3}
            continue
        out_std[key] = {}
        out_std[key]["mean"] = pts[:, 3].mean()
        out_std[key]["max"] = pts[:, 3].max()
        out_std[key]["std"] = pts[:, 3].std()
    # print(out_std)
    return out_std


def computer_all_dir(index, current_dir=r"npy文件\0号楼"):
    # E:\2.1SE-T32\计算误差距离\npy文件\0号楼
    # E:\2.1SE-T32\计算误差距离\npy文件\1号楼
    # E:\2.1SE-T32\计算误差距离\npy文件\2楼平台

    '''

    :return:
    '''

    # 根据 位置和,X,z找到对应的npy，然后得到每一个x,z对应的val,就可以把那个图画出来了
    # 位置-10m/ 位置-20m     可以画出  X-Z-VAL的三维图，同时可以算出最小误差的点。
    index
    paths = os.listdir(current_dir)
    label_dict = {"<10": [], "10-20": [], "20-40": [], ">40": []}

    for path in paths:
        if path[-4:] == ".npy":
            x, z = path.split("_")
            try:
                if index == 2:
                    x = float(x[9:])
                    z = float(z[:-4])
                else:
                    x = float(x[8:])
                    z = float(z[:-4])

            except Exception as e:
                print(e)
                continue
            # 这里需要解析一下X,Z
            out = computer_signal_npz_std(index, os.path.join(current_dir, path))
            for key in label_dict.keys():
                temp_obj = out[key]
                label_dict[key].append({"x": x, "z": z, "dis_var": temp_obj})

    #print(label_dict)
    return label_dict


def draw_sca(labels_lists,A):  # label_lists,A:距离
    # min_val=100
    # min_index = -1
    title = ['<10m', '10-20m', '20-40m', '>40m']
    title1 = ['0号楼', '1号楼', '2楼平台']

    #X = [[[] for _ in range(len(labels_lists[0].keys()))] for _ in range(len(labels_lists))]
    #Y = [[[] for _ in range(len(labels_lists[0].keys()))] for _ in range(len(labels_lists))]
    #Z = [[[] for _ in range(len(labels_lists[0].keys()))] for _ in range(len(labels_lists))]
    B = [[],[],[]]



    X = [[[],[],[],[]], [[],[],[],[]], [[],[],[],[]]]
    Y = [[[],[],[],[]], [[],[],[],[]], [[],[],[],[]]]
    Z = [[[],[],[],[]], [[],[],[],[]], [[],[],[],[]]]




    for index, label_list in enumerate(labels_lists):

        for j, key in enumerate(label_list.keys()):
            x1 = []
            y1 = []
            z1 = []
            b=[]
            min_index = -1
            min_val = 100


            for i in label_list[key]:
                '''
                x1.append(round(i['x'], 2))
                y1.append(round(i['z'], 2))
                z1.append(i['dis_var']['std'])
                if i['dis_var']['std'] < min_val:
                    min_val = i['dis_var']['std']
                    min_index = len(z1) - 1
                '''

                if i['dis_var']['std']> 0.1:
                    if i['dis_var']['std']==0.3 or 0.7 < i['dis_var']['std'] <0.9 :
                        X[index][j].append(round(i['x'], 2))
                        Y[index][j].append(round(i['z'], 2))
                        Z[index][j].append(i['dis_var']['std'])
                        if i['dis_var']['std'] < min_val:
                            min_val = i['dis_var']['std']
                            min_index = len(Z[index][j]) - 1
                    else:
                        continue


                        X[index][j].append(round(i['x'], 2))
                        Y[index][j].append(round(i['z'], 2))
                        Z[index][j].append(0.08)
                        min_index=0

                else:
                    X[index][j].append(round(i['x'], 2))
                    Y[index][j].append(round(i['z'], 2))
                    Z[index][j].append(i['dis_var']['std'])
                    if i['dis_var']['std'] < min_val:
                        min_val = i['dis_var']['std']
                        min_index = len(Z[index][j]) - 1
            B[index].append(min_index)

            #X[index][j].append(x1)  # X[[[],[]],[[]]],0号楼-10，
            #Y[index][j].append(y1)
            #Z[index][j].append(z1)
            # X.append(x1)
            # Y.append(y1)
            # Z.append(z1)
        #print(X)
    #print(X)

    # 创建一个2x3的子图网格，并指定画布大小
    fig = plt.figure(figsize=(10, 8))

    # 定义子图网格的位置（2x3布局，所以总共6个位置，但我们只使用5个）
    #subplot_positions = [(1, 1), (1, 2), (2, 1), (2, 2)]
    subplot_positions = [(1, 1), (1, 2), (2, 1)]
    # print(b)
    # 遍历子图位置并绘制三维散点图
    for i, (row, col) in enumerate(subplot_positions, 1):  #i作为位置0,1,2号楼

        ax = fig.add_subplot(2, 2, i, projection='3d')  # 创建一个3D子图

        # 生成一些随机数据
        #c = b[i - 1]
        # 在当前子图上绘制三维散点图
        if i ==4:
            break
            # colors1 = ['red', 'orange', 'yellow', 'green', 'cyan', 'blue', 'purple', 'black', 'violet', 'brown']
            # gray_color = ['#808080']  # 添加灰色
            #
            # # 创建一个步长为0.002的边界列表，从0到0.03
            # n_steps = int((0.02 - 0) / 0.002) + 1
            # boundaries = np.linspace(0, 0.02, n_steps)
            # boundaries = np.append(boundaries, 0.03)  # 额外的边界，用于灰色显示
            #
            # # 创建一个ListedColormap，在颜色列表末尾添加灰色
            # cmap_list = colors1 * (n_steps // len(colors1)) + gray_color
            # cmap = ListedColormap(cmap_list)
            #
            # # 对于超过原始颜色列表长度的部分，使用灰色填充
            # norm = BoundaryNorm(boundaries, cmap.N)
            #
            # # 创建一个figure和axes
            # #fig, ax = plt.subplots(figsize=(6, 1))
            # # ax.set_axis_off()  # 关闭坐标轴显示
            #
            # # 绘制colorbar
            # cbar = ColorbarBase(ax, cmap=cmap, norm=norm,
            #                     boundaries=boundaries, ticks=boundaries[:-1], spacing='uniform',
            #                     orientation='horizontal', extend='max')
            #
            # # 设置刻度标签格式，不显示最后一个边界（0.03）的标签
            # cbar.ax.set_xticklabels(['{:.4f}'.format(x) for x in boundaries[:-1]], rotation=90)
        else:

            #color1= ['red' if i < 0.003 else 'black' if 0.003 <= i < 0.007 else 'blue' if  0.007 <= i < 0.017 else 'yellow'  for i in Z[i - 1][A]]
            #if#X["O号楼“][<10]

           ####################### 设置色彩##########################

            colors_list = colors = ['red', 'orange', 'yellow', 'green', 'cyan', 'blue', 'purple', 'black', 'violet', 'brown']

            colors = [None] * len(Z[i - 1][A])
            # print(max(Z[i - 1][A]))
            # 遍历z值，为0到0.5之间的值分配颜色
            for inn, val in enumerate(Z[i - 1][A]):
                if val<0.02:
                    index=int(val*1000/2)%len(colors_list)
                    colors[inn] = colors_list[index]
                else:
                    colors[inn] = 'gray'

            # 定义颜色列表（这里简化为几种颜色，实际应用中可以更详细）
            #colors = ['red', 'orange', 'yellow', 'green', 'blue', 'indigo', 'violet']

            # 映射颜色（这里简化映射逻辑，仅作为示例）
            # 实际应用中，你可能需要更复杂的逻辑来确保所有颜色都被使用
            # 并且可能需要循环使用颜色列表以覆盖整个z值范围

            #####################设置色彩##########################





            '''
            scatter1 = ax.scatter(X[i - 1][A], Y[i - 1][A], Z[i - 1][A], c=color1, cmap='jet',
                                  vmin=np.array(Z[i - 1][A]).min(), vmax=np.array(Z[i - 1][A]).max(),
                                  label=f'Scatter Plot {i - 1}', marker='o')
            '''
            #print(X[i-1][A][0])
            #print(B[i-1][A])
            #print(X[i-1][A][0][0], Y[i-1][A][0][0], Z[i-1][A][0][0])
            # scatter1 = ax.scatter(X[i - 1], Y[i - 1], Z[i - 1], c=Z[i - 1], cmap='viridis', label=f'scatter plot {i - 1}', marker='o')
            # scatter1 = ax.scatter(X[i - 1], Y[i - 1], Z[i - 1], c=Z[i - 1], cmap=cap, label=f'scatter plot {i - 1}',marker='o',norm=plt.Normalize(vmin=np.array(Z[i-1]).min(), vmax=np.array(Z[i-1]).max()))
            ax.scatter(X[i - 1][A], Y[i - 1][A], Z[i - 1][A], c=colors, marker='o')
            ax.scatter(X[i-1][A][B[i-1][A]], Y[i-1][A][B[i-1][A]], Z[i-1][A][B[i-1][A]], c='r', s=50)
            ax.text3D(X[i-1][A][B[i-1][A]], Y[i-1][A][B[i-1][A]], Z[i-1][A][B[i-1][A]], f'({X[i-1][A][B[i-1][A]]:.4f}, {Y[i-1][A][B[i-1][A]]:.4f}, {Z[i-1][A][B[i-1][A]]:.4f})', zdir=(0, 0, 1), color='k', fontsize=8)
            # print(X[i-1][c],Y[i-1][c],Z[i-1][c])
            #fig.colorbar(scatter1, ax=ax, shrink=0.5, aspect=5)

            ax.set_title(f' {title[A]} {title1[i-1]}')
            ax.view_init(elev=40, azim=45)
            #增加颜色条
            colors = ['red', 'orange', 'yellow', 'green', 'cyan', 'blue', 'purple', 'black', 'violet', 'brown', 'gray']
            cmp = mpl.colors.ListedColormap(colors)

            boundaries_low = np.arange(0, 0.023, 0.002)
            norm = mpl.colors.BoundaryNorm(boundaries_low, cmp.N)
            fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmp), ax=ax)

    fig2 = plt.figure()
    ax1 = fig2.add_subplot(111, projection='3d')
    #colors = ['red', 'green', 'blue', 'yellow']
    colors1 = ['red', 'green', 'blue']
    #loc1=['0号楼','1号楼','2楼平台']
    for i, color2 in enumerate(colors1):  #A:4个距离
        ax1.scatter(X[i][A], Y[i][A], Z[i][A], c=color2, alpha=0.7,label=title1[i])
        ax1.set_title(f'  {title[A]}')
        ax1.view_init(elev=40, azim=45)



        # 添加图例（注意：这里只有一个标签，因为所有散点图共享一个图例）
    #ax1.legend(title='红色：0号楼，绿色：1号楼，蓝色：2楼平台' + "\n"f"{title[A]}")
    ax1.legend(loc="best")
    # 调整子图之间的间距和画布边缘
    plt.tight_layout()
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体
    plt.rcParams['axes.unicode_minus'] = False

    # 显示图形
    plt.show()





# label_list=computer_all_dir()

# E:\2.1SE-T32\计算误差距离\npy文件\0号楼
# E:\2.1SE-T32\计算误差距离\npy文件\1号楼
# E:\2.1SE-T32\计算误差距离\npy文件\2楼平台
dirs = [r"E:\2.1SE-T32\计算误差距离\CB50npy\0号楼", r"E:\2.1SE-T32\计算误差距离\CB50npy\1号楼",
        r"E:\2.1SE-T32\计算误差距离\CB50npy\2楼平台"]

# dirs = [r"E:\2.1SE-T32\计算误差距离\npy文件\0号楼", r"E:\2.1SE-T32\计算误差距离\npy文件\1号楼",
#         r"E:\2.1SE-T32\计算误差距离\npy文件\2楼平台"]
label_lists = []
for i, dir in enumerate(dirs):
    label_list = computer_all_dir(i, dir)
    label_lists.append(label_list)
#print(label_lists)
A=1

draw_sca(label_lists,A)

# computer_signal_npz_std()
