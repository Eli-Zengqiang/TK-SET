import socket
from threading import Thread


class TcpClient:
    server_addr = ('127.0.0.1', 9999)

    def __init__(self):
        self.tcp_cli_socket = socket.socket()

    def msg_recv(self):
        """
        接收数据
        """
        while True:
            data = self.tcp_cli_socket.recv(1024)
            if data.decode("utf-8") == "exit":
                print('客户端退出')
                self.tcp_cli_socket.close()
                break

            print(data.decode("utf-8"))

    def msg_send(self):
        """
        发送数据
        """
        while True:
            data_info = input("请发言：")
            if data_info == "exit":
                self.tcp_cli_socket.send(data_info.encode("utf-8"))
                break
            else:
                self.tcp_cli_socket.send((data_info + ' -ta').encode("utf-8"))

    def start(self):
        """
        连接服务器
        """
        try:
            self.tcp_cli_socket.connect(self.server_addr)
        except Exception as e:
            print("连接失败，请重试！")
            self.tcp_cli_socket.close()
            print(e)
            return

        while True:
            name = input("请输入用户名：")
            self.tcp_cli_socket.send((name + ' -n').encode('utf-8'))
            data = self.tcp_cli_socket.recv(128).decode('utf-8')
            print(data)
            if data == "OK":
                print("你已成功进入聊天室")
                break
            else:
                print(data)

        t = Thread(target=self.msg_recv)
        t.start()
        t1 = Thread(target=self.msg_send)
        t1.start()


if __name__ == '__main__':
    client = TcpClient()
    client.start()
