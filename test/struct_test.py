import struct
data=b'U\x01\x01\x00\x00D\x84>\x89\x19pBk\xc0\xdc\xaa'
data1=b'U\x01\x01\x00$\x06\x01;$\x06\x81:\xb8\x1fy\xaa'
print(len(data))
print(type(data1))
angle=struct.unpack('<f',data1[8:12])[0]
print(data1[8:12])
print(angle)

byte_data = b'U\x01\x01\x00$\x06\x01;$\x06\x81:\xb8\x1fy\xaa'

# 将字节串转换为十六进制字符串
hex_datas = byte_data.hex()
# print(len(hex_datas)) # 输出为字符串形式的十六进制
datas=[]
for i in range(int(len(hex_datas)/2)):
    a='0x'+hex_datas[2*i:2*i+2]
    datas.append(a)
    print(datas)
with open('output.txt', 'w') as file:
    # 将列表中的元素用空格连接成一个字符串
    content = ' '.join(datas)
    # 写入文件
    file.write(content)

print("列表已成功写入 output.txt 文件。")




