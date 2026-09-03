import bluetooth

# devs= bluetooth.discover_devices(lookup_names=True, )
#
# print(devs)
#
# print("本机蓝牙MAC地址:",bluetooth.read_local_bdaddr())


# def connect_target_device(self, target_name, target_address):
#     self.find_target_device(target_name=target_name, target_address=target_address)
#     if self.find:
#         print("Ready to connect")
#         sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
#         try:
#             sock.connect((target_address, 1))
#             print("Connection successful. Now ready to get the data")
#             data_dtr = ""
#             while True:
#                 data = sock.recv(1024)
#                 data_dtr += data.decode()
#                 if '\n' in data.decode():
#                     # data_dtr[:-2] 截断"\t\n",只输出数据
#                     print(datetime.datetime.now().strftime("%H:%M:%S") + "->" + data_dtr[:-2])
#                     data_dtr = ""
#         except Exception as e:
#             print("connection fail\n", e)
#             sock.close()


target_address = "20:17:12:04:15:76"
port = 1 #默认端口号

# 连接到设备
sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM) #创建RFCOMM套接字对象
sock.connect((target_address, port))

# 发送消息
sock.send("Hello World")
data = sock.recv(1024)
print(f"Received: {data}")

#关闭连接
sock.close()