import json
import os
import socket
import socketserver
import threading
import time
import shutil
from pprint import pp, pprint
from tkinter import *
from tkinter import messagebox, ttk

# -------------------------------------------
#  sending message to another client
# -------------------------------------------


def send_msg(host, port, msg) -> None:
    """基本通讯"""
    print('尝试连接', host, ':', port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
        sock.sendall(bytes(msg, "utf-8"))
        print("信息已发送:", msg)
    finally:
        sock.close()


def construct_cmd_data(cmd=[]) -> dict:
    """ 构建用于通讯的字典数据 """
    print('正在获取硬件信息...')
    data = {"cmdList": cmd}
    return data


# -------------------------------------------
#  useful commands
# -------------------------------------------


def asscociate_num_and_ip() -> dict:
    """ 
    asscociate a self-increament num with ip listed in the folder 
    此函数在程序中没有被调用
    但是删除该函数会引发 json 解码 bug
    请勿修改此没用的函数
    """
    dct = {}
    all_ip = [i[:-5] for i in os.listdir('online_devices')]
    for k, v in zip(range(1, len(all_ip) + 1), all_ip):
        dct[k] = v
    return dct


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
#  built-in server
# -------------------------------------------


class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        """
        handel the data sent to this server, the data shoud be like:
        - a json file sent in str format
        - contains key `mode`
        - has an empty key `serverFindIP`
        used to log its online ip, not the local client ip
        """
        # original data
        self.data = self.request.recv(1024).strip()
        # ip
        self.come_ip = self.client_address[0]
        print("{} 连接到此服务器".format(self.come_ip))
        # decoded receved msg
        self.content = str(self.data, 'utf-8')
        self.content = self.content.replace("'", '"')
        self.recieved_dct = eval(self.content)
        # insert the ip address find by this server
        self.recieved_dct['serverFindIP'] = self.come_ip
        # this `ready` is the json data transmitted from client
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


def new_a_folder_in_awesome_way(folderName):
    """
    由于windows的文件夹新建过于神奇
    使用此函数进行新建文件夹
    """
    for _ in range(3):
        try:
            os.mkdir(folderName)
        except FileExistsError:
            pass
        except Exception as e:
            print(f'文件夹新建异常：目标文件夹 {folderName}\n\t抛出 {e}')
            break
        finally:
            # sleep a while to avoid stupid windows things
            time.sleep(0.2)

def start_server() -> None:
    """
    # The most *Basic* function to start a server
    if you directly call this function,
    the current thread will be blocked
    but new a folder under windows seems to be unstable
    """
    # back up connection data
    # first delete last backup folder, 
    # new it first to avoid stupid windows
    new_a_folder_in_awesome_way('online_devices_backup')
    shutil.rmtree('online_devices_backup')
    # then new the folder
    new_a_folder_in_awesome_way('online_devices_backup')
    # and then backup those files
    try:
        shutil.copytree('online_devices', 'online_devices_backup')
    except FileExistsError:
        print('文件夹已检测到')
    print('上次客户端连接数据已备份至 online_devices_backup 文件夹')
    # delete original data, 
    time.sleep(0.3)
    # delete original log folder
    shutil.rmtree('online_devices')
    time.sleep(0.2)
    # then new it 
    new_a_folder_in_awesome_way('online_devices')
    print('原有记录已删除')
    # load profiles
    with open('server.json', 'r') as f:
        a = json.load(f)
    PORT = a['port']
    IP = a['ip']
    # start server
    server = socketserver.TCPServer((IP, PORT), MyTCPHandler)
    print('内置服务器已启动：', IP, PORT)
    server.serve_forever()


# -------------------------------------------
#  GUI here!
# -------------------------------------------


class GUI:
    """ a simple GUI for this main program """
    def __init__(self):
        self.root = Tk()
        self.root.title('自动关机')
        self.pad = {'padx': 10, 'pady': 10}
        # 界面分四部分，从上到下分别为：
        # 状态显示
        # 命令输入
        # 控制按钮
        # 客户端列表
        self.top_message_frame = Frame(self.root)
        self.server_has_started_text = StringVar()
        self.server_has_started_text.set('尚未开启内置服务器')
        self.command_frame = Frame(self.root)
        self.command_entry = Entry(self.command_frame)
        self.button_frame = Frame(self.root)
        self.client_list_frame = Frame(self.root)

    def layout_buttons(self):
        ttk.Button(self.button_frame,
                   text='开启内置服务器',
                   command=self.button_kick_start_server).grid(row=0,
                                                               column=0,
                                                               **self.pad)

        ttk.Button(self.button_frame,
                   text='刷新列表',
                   command=self.button_refresh_list).grid(row=0,
                                                          column=1,
                                                          **self.pad)

        ttk.Button(self.button_frame,
                   text='发送命令',
                   command=self.button_send_command).grid(row=0,
                                                          column=2,
                                                          **self.pad)

        ttk.Button(self.button_frame, text='清空选择',
                   command=self.button_clear).grid(row=0, column=3, **self.pad)

        ttk.Button(self.button_frame,
                   text='读取文本文档 IP',
                   command=self.button_read_ip).grid(row=0,
                                                     column=4,
                                                     **self.pad)

        ttk.Button(self.button_frame,
                   text='读取目录下全部 IP',
                   command=self.btn_load_all_ip).grid(row=0,
                                                      column=5,
                                                      **self.pad)

    def layout_tree(self):
        # 鼠标点击后插入的索引，十六进制的内个，列表中的顺序
        # 使用一个字典，如果点击了偶数次，则视为取消，用于意外处理
        self.selected_client_index = {}
        # 用于插入数据时的左侧唯一编号，自增，该变量插入进 Tree
        self.defenite_id = 0
        # 最终选择的客户端, int
        self.finally_selected_client = []
        # 发送失败的客户端, List[str]
        self.failed = []
        self.matching = {}
        # 定义中心列表区域
        self.tree = ttk.Treeview(self.client_list_frame,
                                 show="headings",
                                 height=24,
                                 columns=("a", "b", "c", "d"))
        self.vbar = ttk.Scrollbar(self.client_list_frame,
                                  orient=VERTICAL,
                                  command=self.tree.yview)
        # 定义树形结构与滚动条
        self.tree.configure(yscrollcommand=self.vbar.set)
        # 表格的标题
        self.tree.column("a", width=80, anchor="center")
        self.tree.column("b", width=160, anchor="center")
        self.tree.column("c", width=160, anchor="center")
        self.tree.column("d", width=160, anchor="center")
        # 用这个顺序编号来判断哪些客户端需要执行命令！
        self.tree.heading("a", text="顺序编号")
        self.tree.heading("b", text="客户端 IP")
        self.tree.heading("c", text="连接时间")
        self.tree.heading("d", text="处理器信息")
        # 调用方法获取表格内容插入及树基本属性设置
        self.tree["selectmode"] = "browse"
        self.tree.grid(row=0, column=0, sticky=NSEW, ipadx=10)
        self.vbar.grid(row=0, column=1, sticky=NS)
        self.tree.bind("<ButtonRelease-1>", self.tree_item_click)
        # testing purposes

    def tree_insert_value(self, clientIP, connectTime, CPU):
        """ 插入列表的基本方法 """
        self.defenite_id += 1
        self.tree.insert("",
                         "end",
                         values=(self.defenite_id, clientIP, connectTime, CPU))
        self.matching[self.defenite_id] = clientIP

    def tree_item_click(self, event):
        """
        当列表某一项被点击时的回调函数，自动处理偶数次点击
        """
        selection = self.tree.selection()[0]
        hexx = str(selection[1:])
        num = int(hexx, 16)
        self.selected_client_index[num] = self.selected_client_index.get(
            num, 0) + 1
        self.tree_process_selected()

    def tree_process_selected(self):
        """
        在选择客户端时，可视化呈现哪些客户端被选择了
        同时记录进 self.finally_selected_client 列表
        用于发送命令
        """
        self.finally_selected_client = []
        for k, v in self.selected_client_index.items():
            if v % 2 != 0:
                self.finally_selected_client.append(k)
        print(self.finally_selected_client)

    def multi_thread_start_server(self):
        check_dir()
        t = threading.Thread(target=start_server)
        t.setDaemon(True)
        t.start()
        self.server_has_started_text.set('内置服务器已开启')

    def button_kick_start_server(self):
        decision = messagebox.askokcancel('注意', '开启服务器将清空连接记录，并备份至备份文件夹。\n在客户端初次连接成功后，可不开启服务器直接点击刷新按钮。\n是否开启服务器？')
        if decision:
            self.multi_thread_start_server()


    def button_refresh_list(self):
        # 删除内容：
        x = self.tree.get_children()
        for item in x:
            self.tree.delete(item)
        # 初始化左侧唯一自增序号
        self.defenite_id = 0
        # 遍历目录
        all_file_path = os.listdir('online_devices')
        # 插入：
        for file in all_file_path:
            print('处理：', file)
            # 查看详细信息：
            with open(f'./online_devices/{file}', 'r', encoding='utf-8') as f:
                data = json.load(f)
                # ip = data['hardware']['IP']
                ip = data['serverFindIP']
                timee = data['time']
                cpu = data['hardware']['CPU']
                self.tree_insert_value(ip, timee, cpu)

    def button_send_command(self):
        if len(self.finally_selected_client) == 0:
            messagebox.showerror('error', '还没有选择客户端')
        else:
            print('以下客户端将被发送命令：')
            clientIPs = []
            for i in self.finally_selected_client:
                clientIPs.append(self.matching[i])
                print(self.matching[i])
            cmd = self.command_entry.get()
            # 又没法取消干脆不提示了
            # messagebox.showinfo('结果', '将执行以下命令：\n{}'.format(cmd))
            self.let_multiple_client_exec_cmd(
                clientIPs,
                cmd,
            )
            print('\n\n发送失败的连接：')
            pp(self.failed)

    def button_read_ip(self):
        with open('manual_set_ip.txt', 'r', encoding='utf-8') as f:
            IPs = f.read().splitlines()
            self.finally_selected_client = [i for i in range(1, len(IPs) + 1)]
        for ip in IPs:
            self.tree_insert_value(ip, 'None', 'None')
        messagebox.showinfo('注意', '将自动选择所有的客户端')

    def button_clear(self):
        self.defenite_id = 0
        self.selected_client_index = {}
        self.finally_selected_client = []
        messagebox.showinfo('清空', '选择列表已清空')
        print('选择列表已清空')

    def btn_load_all_ip(self):
        all_file_path = os.listdir('online_devices')
        all_ip_str = [i[:-5] for i in all_file_path]
        pp(all_ip_str)
        with open('manual_set_ip.txt', 'w') as f:
            f.write('\n'.join(all_ip_str))
        messagebox.showinfo('信息', '所有 IP 已写入文本文档，请点击“读取填写的 IP”按钮')

    def send_json(self, host: str, port: int, dict_data: dict):
        """封装了基本通讯，可以发送一个字典"""
        msg = str(dict_data).replace('\n', '')
        times = 0
        while times <= 2:
            times += 1
            try:
                send_msg(host, port, msg)
                return
            except ConnectionRefusedError:
                print('目标客户端 {}:{} 连接失败，进行第 {} 次尝试'.format(host, port, times))
        print('数据发送失败，当前客户端已加入失败列表')
        self.failed.append(host)

    def let_client_exec_cmd(self, client_ip: str, cmd: str):
        """ let a single client execute cmds """
        with open('server.json', 'r', encoding='utf-8') as f:
            a = json.load(f)
        CMDPORT = a['cmd_port']
        data = construct_cmd_data(cmd)
        self.send_json(client_ip, CMDPORT, data)

    def let_multiple_client_exec_cmd(self, clientIPs: list, cmd: str):
        """ let multiple client execute cmd, just send cmd one by one """
        for each_client in clientIPs:
            print('当前执行命令的客户端 IP ：{}'.format(each_client))
            self.let_client_exec_cmd(each_client, cmd)

    def layout_top_msg_frame(self):
        Label(self.top_message_frame,
              textvariable=self.server_has_started_text).pack(**self.pad)
        self.top_message_frame.pack(**self.pad)

    def layout_command_frame(self):
        Label(self.command_frame, text='执行命令：').grid(
            row=0,
            column=0,
        )
        self.command_entry.grid(row=0, column=1)
        self.command_frame.pack(**self.pad)

    def run(self):
        self.layout_top_msg_frame()
        self.layout_command_frame()
        self.layout_buttons()
        self.layout_tree()
        self.button_frame.pack(**self.pad)
        self.client_list_frame.pack(**self.pad)
        self.root.mainloop()


# -------------------------------------------
#  main prog
# -------------------------------------------


def main() -> None:
    # ! abandoned!
    """# the entrance of this program"""
    print('输入序号 0，1，2 以选择服务端模式')
    print('0 为测试模式，请勿使用')
    print('1 为监听模式，记录所有打开了客户端的数据')
    print('2 为命令发送模式，可以向指定 IP 发送 cmd 命令')
    print('')
    while True:
        mode = input('输入数字：')
        # if mode not in {'1', '2', '0'}:
        #     continue
        # elif mode == '0':
        #     let_client_exec_cmd('127.0.0.1', ['calc'])  # <- testing method
        # elif mode == '1':
        #     kick_start_server()
        # elif mode == '2':
        #     # need to be developed
        #     pass


def GUImain() -> None:
    app = GUI()
    app.run()


if __name__ == "__main__":
    GUImain()
