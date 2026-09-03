import pandas as pd

# 替换为你的Excel文件路径
file_path = r"E:\2.1SE-T32\设备验收结果\检查表.xls"

# 使用pandas的read_excel函数读取Excel文件
# 假设你的数据在第一张表上，且没有指定列名，可以使用header=None来忽略表头
# 如果你的Excel有表头，则不需要设置header=None
df = pd.read_excel(file_path, header=None)  # 或者指定header=0如果你有表头

# 获取第一列和第二列的数据，这里使用iloc是基于位置的索引
# 如果你的数据有表头，且你知道列名，也可以使用loc进行基于标签的索引，例如df.loc[:, '列名']
first_column = df.iloc[:, 0].tolist()  # 第一列数据放入列表
second_column = df.iloc[:, 3].tolist()  # 第二列数据放入列表

# 输出查看结果
print("第一列数据:", first_column)
print("第二列数据:", second_column)