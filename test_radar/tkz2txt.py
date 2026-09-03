import os
import struct


def read_data_foders(path):
    # path=r"F:\2.1SE-T32\2.1data\20250415验证CC50点云缺失\缺点测试/"
    data_folders=os.listdir(path)
    data_folders_list=[]
    for data_folder in data_folders:
        data_folders_list.append(os.path.join(path,data_folder))
    data_folders_list=sorted(data_folders_list)
    print(data_folders_list)
    return data_folders_list



def read_tkz_and_save_txt(tkz_file_paths):
    for tkz_files in  tkz_file_paths:
        txt_path_name=os.path.join(tkz_files,'out')
        os.makedirs(txt_path_name,exist_ok=True)


        for i in range(0,13):
            tkz_file_path= os.path.join(tkz_files,str(i) +'.tkz')
            txt_file_path= os.path.join(txt_path_name,str(i) +'.txt')

            with open(tkz_file_path, 'rb') as tkz_file, open(txt_file_path, 'w') as txt_file:
                # 写入表头（可选）
                #txt_file.write("x y z intensity timestamp ring\n")

                while True:
                    # 每个点占 4+4+4+4+8+2=26 字节
                    data = tkz_file.read(26)
                    if not data or len(data) < 26:
                        break

                    # 解包二进制数据
                    x, y, z, intensity, timestamp, ring = struct.unpack('ffffd h', data)

                    # 写入 txt 文件（格式：空格分隔）
                    txt_file.write(f"{x} {y} {z} {intensity} {timestamp} {ring}\n")
                print(f"{txt_file_path}，写入完成")


# 使用示例
# tkz_file = r"F:\2.1SE-T32\2.1data\20250415验证C050点云缺失\缺点测试\2025-04-17_15-48-54\0.tkz"  # 输入的 tkz 文件路径
# txt_file = "output.txt"  # 输出的 txt 文件路径
# read_tkz_and_save_txt(tkz_file, txt_file)
# print(f"数据已保存至 {txt_file}")

if __name__=="__main__":

    #path=r"G:\TK-set\verify_lost_data"
    
    #tkz_file_paths=read_data_foders(path) #读取文件路径下的所有文件夹

    tkz_file_paths=[r"G:\TK-set\2.1error_data\20260428验证新版本\2026-04-28_14-14-42"]#单个文件夹处理
    read_tkz_and_save_txt(tkz_file_paths) #将TKZ文件转换成txt文件

