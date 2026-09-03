import os
import numpy as np

def read_folder_cloude_data(cloude_path):
    #cloude_path=r"C:\Users\ZHXR\Desktop\新建文件夹\2025-03-28_10-04-02\txt/"
    ab = os.listdir(cloude_path)
    #print(ab)
    sorted_ab = sorted(ab, key=lambda x: int(x.split('.')[0]))
    #print(sorted_ab)
    lists = []
    for a in sorted_ab:
        list = os.path.join(cloude_path, a)
        #print(list)
        lists.append(list)

    # print(f"当前文件夹下的文件个数：{len(lists)}")
    # print(f"当前文件夹下的文件及路径：{lists}")
    return lists  #


def read_cloud_datas(paths,cloude_path):
    cloude_datas=[]
    lengths=[]
    for i in paths:
        cloud_data=np.loadtxt(i)[:,0:5]
        cloude_datas.append(cloud_data)
        # lengths.append(len(cloude_datas))


    if cloude_datas:
        combine_datas=np.vstack(cloude_datas)
        combine_datas[:][3]=0
    else:
        combine_datas= np.array([])
    #print(combine_datas)
    np.savetxt(rf'{cloude_path}\out.txt',combine_datas, fmt='%.5f')
    return combine_datas
        # ,lengths
    # cloude_path=r"C:\Users\ZHXR\Desktop\新建文件夹\2025-03-28_10-04-02\txt/"
    # read_folder_cloude_data(cloude_path)


def judge_time(combine_datas):
    for i in range(len(combine_datas)-1):
        if combine_datas[i+1][4]-combine_datas[i][4] < 1:
            continue
        else:
            print(f"{combine_datas[i+1][4]}-{combine_datas[i][4]}时间差为：{combine_datas[i+1][4]-combine_datas[i][4]}")
            print(f"共{len(combine_datas)}行数据,第{i+1}行数据时间大于1")
    #np.savetxt('out.txt',)











if __name__=="__main__":
    cloude_path=r"F:\2.1SE-T32\2.1data\20250415验证C050点云缺失\2025-04-15_09-09-28\txt/"
    path_lists=read_folder_cloude_data(cloude_path)
    combine_datas=read_cloud_datas(path_lists,cloude_path)
    judge_time(combine_datas)


