import socket
from threading import Thread
import time
import sys


# 创建存储对象
class Node:
    def __init__(self):
        self.Name = None    # 用户名
        self.Thr = None     # 套接字连接对象


class TcpServer:
    user_name = {}  # 存储用户信息； dict 用户名：Node对象

    def __init__(self, port):
        """
        初始化服务器对象
        port:   服务器端口
        """
        self.server_port = port      # 服务器端口
        self.tcp_socket = socket.socket()       # tcp套接字
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)       # 端口重用
        self.tcp_socket.bind(self.server_port)

    def start(self):
        """
        启动服务器
        """
        self.tcp_socket.listen(10)      # 设置服务器接受的链接数量
        print(self.get_time(), "系统：等待连接")
        while True:
            try:
                conn, addr = self.tcp_socket.accept()       # 监听客户端的地址和发送的消息

            except KeyboardInterrupt:       # 按下ctrl+c会触发此异常
                self.tcp_socket.close()     # 关闭套接字
                sys.exit("\n" + self.get_time() + "系统：服务器安全退出！")        # 程序直接退出，不捕捉异常
            except Exception as e:
                print(e)
                continue

            # 为当前链接创建线程
            t = Thread(target=self.do_request, args=(conn, ))
            t.start()

    def do_request(self, conn):
        """
        监听客户端传送的消息，并将该消息发送给所有用户
        """
        conn_node = Node()
        print(f"conn_node为：{conn_node}")
        while True:
            recv_data = conn.recv(1024).decode('utf-8').strip() # 获取客户端发来的数据
            print(f"recv_data:{recv_data}")
            info_list = recv_data.split(" ")        # 切割命令
            print(f"info_list:{info_list}")
            # 如果接收到命令为exit，则表示该用户退出，删除对应用户信息，关闭连接
            if recv_data == "exit":
                msg = self.get_time() + " 系统：用户" + conn_node.Name + "退出聊天室！"
                print(msg)
                self.send_to_other(conn_node.Name, msg)
                conn.send('exit'.encode("utf-8"))
                self.user_name.pop(conn_node.Name)
                conn.close()
                break
            else:
                try:
                    A = info_list[-2], info_list[-1]
                    print(f"A:{A}")
                except IndexError:
                    conn.send((self.get_time() + ' 系统：无法识别您的指令，请重新输入！').encode('gb2312'))
                    continue

            if info_list[-1] == '-n':
                # 新用户注册
                print(self.get_time() + ' 系统：' + info_list[0] + '连接成功')
                data_info = self.get_time() + ' 系统：' + info_list[0] + '加入了聊天'
                self.send_to_all(data_info)
                conn.send('OK'.encode('utf-8'))
                conn_node.Name = info_list[0]
                conn_node.Thr = conn

                self.user_name[info_list[0]] = conn_node
                print(f'self.user_name:{self.user_name}')
            elif info_list[-1] == '-ta':
                # 群发消息
                msg = self.get_time() + ' %s：' % conn_node.Name + ' '.join(info_list[:-1])
                self.send_to_all(msg)

    def send_to_all(self, msg):
        """
        对所有用户发送消息
        """
        print(msg)
        for i in self.user_name.values():
            i.Thr.send(msg.encode('utf-8'))

    def send_to_other(self, name, msg):
        """
        对除了当前发送信息的用户外的其他用户发送消息
        """
        # print("收到消息:" + msg)
        for n in self.user_name:
            if n != name:
                self.user_name[n].Thr.send(msg.encode('utf-8'))
            else:
                continue

    def get_time(self):
        """
        返回当前系统时间
        """
        return '[' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ']'


if __name__ == '__main__':
    HOST = "127.0.0.1"
    POST = 9999
    server = TcpServer((HOST, POST))
    server.start()

