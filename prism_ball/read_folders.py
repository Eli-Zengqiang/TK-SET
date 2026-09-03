import os

def read_folders_file(path):
    ab=os.listdir(path)
    total_points_file=None
    # print(ab)
    sorted_ab = sorted(ab)
    lists=[]
    for a in sorted_ab:

        if len(a) < 8:
            continue
        list=os.path.join(path,a)
        #print(list)
        if os.path.isdir(list):
            lists.append(list)

        elif '全站仪' in list:
            print(list)
            total_points_file=str(list)
            # print(total_points_file)

    print(f"当前文件夹下的文件个数：{len(lists)}")
    print(f"当前文件夹下的文件及路径：{lists}")
    print(f"全站仪打点文件：{total_points_file}")
    return lists,total_points_file

#paths=r"F:\2.1SE-T32\2.1data\20250515CB55-CC53-C854\CF52/"
if __name__=="__main__":
    paths=r"F:\2.1SE-T32\2.1data\20250515CB55-CC53-C854\8CC53"
    read_folders_file(paths)