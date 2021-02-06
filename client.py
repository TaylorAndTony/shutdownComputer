import socket
import socketserver
import json
import os
import re
from datetime import datetime
import time
import threading
from pprint import pprint, pp

# -------------------------------------------
#  useful commands
# -------------------------------------------


def exec_cmd(cmd):
    """执行一个cmd命令，并返回输出结果"""
    r = os.popen(cmd)
    text = r.read()
    r.close()
    return text


def acquire_cpu():
    """获取CPU型号"""
    ori = exec_cmd('wmic cpu GET Name')
    regex = r'\n.+?\n'
    text = re.findall(regex, ori)[0].replace('\n', '')
    return text


def acquire_ip():
    """获取 ip 地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


def give_me_date():
    """get the current date and time"""
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


def log_start_status():
    """
    If this client is started, it will first write online time
    to a txt file named client_start_status.txt
    this txt file only log 10 most recent online times.
    """
    if not os.path.exists('client_start_status.txt'):
        f = open('client_start_status.txt', 'w')
        f.close()
    # 文件存在
    else:
        # 先读取
        with open('client_start_status.txt', 'r', encoding='utf-8') as f:
            content = f.read().splitlines()
        # 判断文件长度
        # 超出限制
        if len(content) > 10:
            content.pop(0)
            content.append(give_me_date())
            # 复写文件
            with open('client_start_status.txt', 'w') as f:
                f.write('\n'.join(content))
        else:
            with open('client_start_status.txt', 'a') as f:
                f.write(give_me_date() + '\n')
    
# -------------------------------------------
#  communication area
# -------------------------------------------


def send_msg(host, port, msg):
    """基本通讯"""
    print('> 子线程服务器：尝试连接', host, ':', port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
        sock.sendall(bytes(msg, "utf-8"))
        print("> 子线程服务器：信息已发送:", msg)
    finally:
        sock.close()


def send_json(host: str, port: int, dict_data: dict):
    """封装了基本通讯，可以发送一个字典"""
    msg = str(dict_data).replace('\n', '')
    send_msg(host, port, msg)


def construct_data(mode='auto-connect', msg='', cmd=[]) -> dict:
    """
    ### 构建用于通讯的字典数据
    `mode` 可以为以下类型：
    - `auto-connect`: 用于自动发送系统信息
    - `send-message`: 用于向服务器发送自定义数据，数据为结尾的 extraInfo
    - `exec-command`: 用于向服务器发送命令并让服务端执行，命令为结尾的 cmdList，是一个列表
    """
    print('正在获取硬件信息...')
    data = {
        "mode": mode,
        "time": give_me_date(),
        "serverFindIP": "",
        "hardware": {
            "CPU": acquire_cpu().strip(),
            "IP": acquire_ip().strip()
        },
        "extraInfo": msg,
        "cmdList": cmd
    }
    return data


def send_auto_data_until_success():
    """
    不断发送数据至目标服务器，直到发送成功后退出死循环
    请用多线程开启此函数
    """
    with open('client.json', 'r') as f:
        a = json.load(f)
    port = a['port']
    ip = a['targetip']
    data = construct_data('auto-connect')  # <- modify here!
    connected = False
    while not connected:
        try:
            send_json(ip, port, data)
            connected = True
        except ConnectionRefusedError:
            print('> 子线程服务器：未发现服务器，等待中...')
            time.sleep(3)

# -------------------------------------------
#  built-in server
# -------------------------------------------



class MyTCPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        """

        """
        # original data
        self.data = self.request.recv(1024).strip()
        # ip
        self.come_ip = self.client_address[0]
        print("> 子线程服务器：{} 希望向此客户端发送数据".format(self.come_ip))
        # decoded receved msg
        self.content = str(self.data, 'utf-8')
        self.content = self.content.replace("'", '"')
        # this `ready` is the json data transmitted from client
        ready = json.loads(self.content)
        self.analyse_json_and_exec_cmds(ready)
    
    def analyse_json_and_exec_cmds(self, json_thing):
        """
        response to the json sent by server,
        analyse its structure and execute
        the commands one by one in it.
        """
        cmd = json_thing['cmdList']
        print('> 子线程服务器：执行命令 {}'.format(cmd))
        os.system(cmd)


def start_server() -> None:
    """
    # The most *Basic* function to start a server
    if you directly call this function,
    the current thread will be blocked
    """
    with open('client.json', 'r') as f:
        a = json.load(f)
    PORT = a['cmd_port']
    IP = a['localip']
    server = socketserver.TCPServer((IP, PORT), MyTCPHandler)
    print('监听服务端发送命令的子服务器已启动：', IP, PORT)
    server.serve_forever()


# -------------------------------------------
#  comm control
# -------------------------------------------

def kick_start_data_sending():
    """ # using threading to start server"""
    t1 = threading.Thread(target=send_auto_data_until_success)
    t1.setDaemon(True)
    t1.start()
    print('自动查询服务器子线程已开启！')

# -------------------------------------------
#  main program
# -------------------------------------------

def main():
    log_start_status()
    kick_start_data_sending()
    start_server()

if __name__ == '__main__':
    # 主线程：一个阻塞的 TCP 服务器
    # 子线程：死循环发送数据，发送成功后退出
    main()
