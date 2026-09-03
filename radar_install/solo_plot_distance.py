import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap


def computer_dis(x, y, z):
    '''
    x = [-0.5967, 0.6141, -0.0191]
    y = [0.6514, 0.0490, 0.8550]
    z = [-0.0907, 0.0088, 0.0157]


    计算到0,0,0的距离
    :param x:
    :param y:
    :param z:
    :return:
    '''
    return np.sqrt((x - 0) ** 2 + (y -0) ** 2 + (z -0) ** 2)
def computer_signal_npz_std(npz_path=r"E:\2.1SE-T32\计算误差距离\npy文件\1号楼\1号楼radar0.0_20.2.npy"):
    '''
    计算单个npz文件不同距离点的误差
    :return:
    '''
    loaded_arr = np.load(npz_path)
    label_dict = {"<10": [], "10-20": [], "20-40": [], ">40": []}

    for point in loaded_arr:
        dis = computer_dis(point[0], point[1], point[2])
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
            out_std[key] = {"mean": -999, "max": -999, "std": 999}
            continue
        out_std[key] = {}
        out_std[key]["mean"] = pts[:, 3].mean()
        out_std[key]["max"] = pts[:, 3].max()
        out_std[key]["std"] = pts[:, 3].std()
    #print(out_std)
    return out_std


def computer_all_dir(current_dir=r"E:\2.1SE-T32\计算误差距离\npy文件\2楼平台"):
    # E:\2.1SE-T32\计算误差距离\npy文件\0号楼
    # E:\2.1SE-T32\计算误差距离\npy文件\1号楼
    # E:\2.1SE-T32\计算误差距离\npy文件\2楼平台

    '''

    :return:
    '''

    # 根据 位置和,X,z找到对应的npy，然后得到每一个x,z对应的val,就可以把那个图画出来了
    # 位置-10m/ 位置-20m     可以画出  X-Z-VAL的三维图，同时可以算出最小误差的点。
    paths = os.listdir(current_dir)
    label_dict = {"<10": [], "10-20": [], "20-40": [], ">40": []}

    for path in paths:
        if path[-4:] == ".npy":
            x, z = path.split("_")
            try:
                x = float(x[9:])
                z = float(z[:-4])

            except Exception as e:
                print(e)
                continue
            # 这里需要解析一下X,Z
            out = computer_signal_npz_std(os.path.join(current_dir, path))
            for key in label_dict.keys():
                temp_obj = out[key]
                label_dict[key].append({"x": x, "z": z, "dis_var": temp_obj})

    print(label_dict)
    return label_dict


def draw_sca(label_list): # label_lists

    title = ['<10', '10-20', '20-40', '>40']
    X=[]
    Y=[]
    Z=[]
    b = []

    for j, key in enumerate(label_list.keys()):
        x1 = []
        y1 = []
        z1 = []
        min_index = -1
        min_val = 100

        for i in label_list[key]:
            x1.append(round(i['x'], 2))
            y1.append(round(i['z'], 2))
            z1.append(i['dis_var']['std'])
            if i['dis_var']['std'] < min_val:
                min_val = i['dis_var']['std']
                min_index = len(z1) - 1
        b.append(min_index)


        X.append(x1)
        Y.append(y1)
        Z.append(z1)
    print(X)
    # 创建一个2x3的子图网格，并指定画布大小
    fig = plt.figure(figsize=(10, 8))

    # 定义子图网格的位置（2x3布局，所以总共6个位置，但我们只使用5个）
    #subplot_positions = [(1, 1), (1, 2), (2, 1), (2, 2)]
    subplot_positions = [(1, 1), (1, 2), (2, 1),(2,2)]
    # print(b)
    # 遍历子图位置并绘制三维散点图
    for i, (row, col) in enumerate(subplot_positions, 1):

        ax = fig.add_subplot(2, 2, i, projection='3d')  # 创建一个3D子图

        #ax = fig.add_subplot(2, 2, 1, projection='3d')  # 创建一个3D子图

        # 生成一些随机数据
        c = b[i - 1]
        # 在当前子图上绘制三维散点图

        scatter1 = ax.scatter(X[i - 1], Y[i - 1], Z[i - 1], c=Z[i - 1], cmap='jet',
                              vmin=np.array(Z[i - 1]).min(), vmax=np.array(Z[i - 1]).max(),
                              label=f'Scatter Plot {i - 1}', marker='o')
        # scatter1 = ax.scatter(X[i - 1], Y[i - 1], Z[i - 1], c=Z[i - 1], cmap='viridis', label=f'scatter plot {i - 1}', marker='o')
        # scatter1 = ax.scatter(X[i - 1], Y[i - 1], Z[i - 1], c=Z[i - 1], cmap=cap, label=f'scatter plot {i - 1}',marker='o',norm=plt.Normalize(vmin=np.array(Z[i-1]).min(), vmax=np.array(Z[i-1]).max()))
        ax.scatter(X[i-1][c], Y[i-1][c], Z[i-1][c], c='g', s=30)
        # print(X[i-1][c],Y[i-1][c],Z[i-1][c])
        fig.colorbar(scatter1, ax=ax, shrink=0.5, aspect=5)

        ax.set_title(f' {title[i - 1]}')
        ax.legend()  # 显示图例（可选）

    fig2 = plt.figure()
    ax1 = fig2.add_subplot(111, projection='3d')
    colors = ['red', 'green', 'blue', 'yellow']
    #colors = ['red', 'green', 'blue']
    for i, color in enumerate(colors):
        ax1.scatter(X[i], Y[i], Z[i], label=f'Set', c=color, alpha=0.7)

        # 添加图例（注意：这里只有一个标签，因为所有散点图共享一个图例）
    ax.legend(title='Sets')

    # 调整子图之间的间距和画布边缘
    plt.tight_layout()


    # 显示图形
    plt.show()




label_list=computer_all_dir()

# E:\2.1SE-T32\计算误差距离\npy文件\0号楼
# E:\2.1SE-T32\计算误差距离\npy文件\1号楼
# E:\2.1SE-T32\计算误差距离\npy文件\2楼平台



draw_sca(label_list)


