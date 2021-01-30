import json
import socket
import socketserver
import os
import time
import threading
from pprint import pprint, pp


# -------------------------------------------
#  This server class
# -------------------------------------------


class MyTCPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        # original data
        self.data = self.request.recv(1024).strip()
        # ip
        self.come_ip = self.client_address[0]
        print("{} 连接到此服务器".format(self.come_ip))
        # decoded receved msg
        self.content = str(self.data, 'utf-8')
        self.content = self.content.replace("'", '"')
        # this `ready` is the json data transmitted from client
        ready = json.loads(self.content)
        # and i will save those data in the folder `./online_devices`
        self.log_this_device(self.come_ip, ready)

    def exec_multi_cmd(self, cmds: list):
        """a method used to execute multiple commands"""
        for cmd in cmds:
            os.system(cmd)
            time.sleep(0.5)

    def log_this_device(self, device_ip, json_thing):
        """
        a method used to create <ip>.json in folder
        and analyse the json to decide what to do next
        """
        # the `json_thing` should be a json file loaded by `json.loads`
        with open(f'./online_devices/{device_ip}.json', 'w') as f:
            json.dump(json_thing, f)
        print(f'{device_ip}.json 数据已写入')
        # the client wants to send a message
        if json_thing["mode"] == "send-message":
            print('有 {} 发来的消息：\n{}'.format(
                self.come_ip, json_thing["extraInfo"]))
        # the client wants the server to execute multiple commands
        elif json_thing["mode"] == 'exec-command':
            print('{} 希望执行 {} 个命令'.format(
                self.come_ip, len(
                    json_thing["cmdList"])
            ))
            self.exec_multi_cmd(json_thing["cmdList"])


# -------------------------------------------
#  sending message to another client
# -------------------------------------------

def send_msg(host, port, msg):
    """基本通讯"""
    print('尝试连接', host, ':', port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
        sock.sendall(bytes(msg, "utf-8"))
        print("信息已发送:", msg)
    finally:
        sock.close()


def send_json(host: str, port: int, dict_data: dict):
    """封装了基本通讯，可以发送一个字典"""
    msg = str(dict_data).replace('\n', '')
    times = 0
    while times <= 3:
        times += 1
        try:
            send_msg(host, port, msg)
            return
        except ConnectionRefusedError:
            print('目标客户端 {}:{} 连接失败，进行第 {} 次尝试'.format(host, port, times))
    print('数据发送失败')


def construct_cmd_data(cmd=[]) -> dict:
    """ 构建用于通讯的字典数据 """
    print('正在获取硬件信息...')
    data = {
        "cmdList": cmd
    }
    return data


def let_client_exec_cmd(client_ip, cmd):
    with open('server.json', 'r') as f:
        a = json.load(f)
    CMDPORT = a['cmd_port']
    data = construct_cmd_data(cmd)
    send_json(client_ip, CMDPORT, data)

# -------------------------------------------
#  useful commands
# -------------------------------------------


def check_dir() -> None:
    """ check whether a directory exists """
    if not os.path.exists('online_devices'):
        os.mkdir('online_devices')
        print('Folder online_devices has been created')
    else:
        print('Directory {} fond'.format('online_devices'))


def find_all_online_devices() -> list:
    """
    go through all json files in the folder ./online_devices
    to find all online clients' ip
    """
    files = os.listdir('./online_devices')
    # ['127.0.0.1.json']
    ips = []
    for i in files:
        ip = str(i)[:9]
        ips.append(ip)
    return ips

# -------------------------------------------
#  server functions
# -------------------------------------------


def start_server() -> None:
    """
    # The most *Basic* function to start a server
    if you directly call this function,
    the current thread will be blocked
    """
    with open('server.json', 'r') as f:
        a = json.load(f)
    PORT = a['port']
    IP = a['ip']
    server = socketserver.TCPServer((IP, PORT), MyTCPHandler)
    check_dir()
    print('服务已启动：', IP, PORT)
    server.serve_forever()


def kick_start_server() -> None:
    """
    # Start the server automatically, the entance of typing 1
    Besides kick start the server, this func will also
    delete all the histories of connected clients.
    """
    print()
    print('   清空客户端连接历史记录')
    print('   请确认删除')
    print('   在完成客户端记录后，请按下 Ctrl + C 手动停止该服务器')
    print('   若无反应，可在按下快捷键后回车。')
    print('   随后再次打开该程序进行其他操作。')

    os.system('del online_devices\*')
    t = threading.Thread(target=start_server)
    t.setDaemon(True)
    t.start()
    print('服务器已做为子线程启动')

# -------------------------------------------
#  Send commands to client
# -------------------------------------------


def send_commands_to_a_client(cmds:list) -> None:
    """Send a single cmd command to a client"""
    with open('server.json', 'r', encoding='utf-8') as f:
        logs = json.load(f)
    ip = logs['ip']
    port = logs['cmd_port']
    data = {
        "mode": "exec-command",
        "cmdList": cmds
    }
    send_json(ip, port, data)



# -------------------------------------------
#  main prog
# -------------------------------------------

def main() -> None:
    """# the entrance of this program"""
    print('输入序号 0，1，2 以选择服务端模式')
    print('0 为测试模式，请勿使用')
    print('1 为监听模式，记录所有打开了客户端的数据')
    print('2 为命令发送模式，可以向指定 IP 发送 cmd 命令')
    print('')
    while True:
        mode = input('输入数字：')
        if mode not in {'1', '2', '0'}:
            continue
        elif mode == '0':
            let_client_exec_cmd('127.0.0.1', ['calc'])              # <- testing method
        elif mode == '1':
            kick_start_server()
        elif mode == '2':
            send_commands_to_a_client(['calc'])

if __name__ == "__main__":
    main()
