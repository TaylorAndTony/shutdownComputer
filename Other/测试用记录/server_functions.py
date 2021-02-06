import json
import socketserver
import os
import time


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
        self.recieved_dct = eval(self.content)
        self.recieved_dct['serverFindIP'] = self.come_ip
        # this `ready` is the json data transmitted from client
        # ! i modified here
        # ready = json.loads(self.content)
        # 加载 json
        ready = json.loads(str(self.recieved_dct).replace("'", '"'))
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
            print('有 {} 发来的消息：\n{}'.format(self.come_ip,
                                           json_thing["extraInfo"]))
        # the client wants the server to execute multiple commands
        elif json_thing["mode"] == 'exec-command':
            print('{} 希望执行 {} 个命令'.format(self.come_ip,
                                          len(json_thing["cmdList"])))
            self.exec_multi_cmd(json_thing["cmdList"])


def check_dir() -> None:
    """ check whether a directory exists """
    if not os.path.exists('online_devices'):
        os.mkdir('online_devices')
        print('Folder online_devices has been created')
    else:
        print('Directory {} fond'.format('online_devices'))

def start_server() -> None:
    """
    # The most *Basic* function to start a server
    if you directly call this function,
    the current thread will be blocked
    """
    os.system('del online_devices\*')
    with open('server.json', 'r') as f:
        a = json.load(f)
    PORT = a['port']
    IP = a['ip']
    server = socketserver.TCPServer((IP, PORT), MyTCPHandler)
    check_dir()
    print('服务已启动：', IP, PORT)
    server.serve_forever()

if __name__ == '__main__':
    start_server()
