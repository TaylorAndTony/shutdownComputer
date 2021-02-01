"""
此文件仅保留本地文件管理、命令发送功能
客户端的连接依靠 server_functions.py 进行
server_functions.py 依赖文件夹 online_devices，用于记录客户端的json数据
此 py 依赖文件夹 server_logged_devices，用于确定发送命令的ip
使用时先运行 server_functions.py 记录客户端，完成记录后关闭server_functions.py
随后运行此 py，点击同步记录，将自动复制记录的json到server_logged_devices
"""
import json
import os
import socket
from pprint import pp, pprint
from tkinter import *
from tkinter import messagebox, ttk

import pyperclip

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


def construct_cmd_data(cmd=[]) -> dict:
    """ 构建用于通讯的字典数据 """
    print('正在获取硬件信息...')
    data = {"cmdList": cmd}
    return data


# -------------------------------------------
#  useful commands
# -------------------------------------------


def asscociate_num_and_ip():
    """ asscociate a self-increament num with ip listed in the folder """
    dct = {}
    all_ip = [i[:-5] for i in os.listdir('server_logged_devices')]
    for k, v in zip(range(1, len(all_ip) + 1), all_ip):
        dct[k] = v
    return dct


def check_dir() -> None:
    """ check whether a directory exists """
    if not os.path.exists('server_logged_devices'):
        os.mkdir('server_logged_devices')
        print('Folder server_logged_devices has been created')
    else:
        print('Directory {} fond'.format('server_logged_devices'))


def find_all_server_logged_devices() -> list:
    """
    go through all json files in the folder ./server_logged_devices
    to find all online clients' ip
    """
    files = os.listdir('./server_logged_devices')
    # ['127.0.0.1.json']
    ips = []
    for i in files:
        ip = str(i)[:9]
        ips.append(ip)
    return ips



# -------------------------------------------
#  GUI here!
# -------------------------------------------


class GUI:
    def __init__(self):
        self.root = Tk()
        self.root.title('自动关机')
        self.pad = {'padx': 10, 'pady': 10}
        # 界面分两部分，上面的控制按钮和下面的列表
        self.upper_frame = Frame(self.root)
        self.bottom_frame = Frame(self.root)

    def layout_buttons(self):
        # ! 把这里改成同步列表数据
        ttk.Button(self.upper_frame,
                   text='同步记录数据',
                   command=self.button_sync_data).grid(row=0,
                                                              column=0,
                                                              **self.pad)

        ttk.Button(self.upper_frame,
                   text='刷新列表',
                   command=self.button_refresh_list).grid(row=0,
                                                          column=1,
                                                          **self.pad)

        ttk.Button(self.upper_frame,
                   text='发送命令',
                   command=self.button_send_command).grid(row=0,
                                                          column=2,
                                                          **self.pad)

        ttk.Button(self.upper_frame, text='清空选择',
                   command=self.button_clear).grid(row=0, column=3, **self.pad)

        ttk.Button(self.upper_frame,
                   text='读取文本文档 IP',
                   command=self.button_read_ip).grid(row=0,
                                                     column=4,
                                                     **self.pad)

        ttk.Button(self.upper_frame,
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
        self.tree = ttk.Treeview(self.bottom_frame,
                                 show="headings",
                                 height=8,
                                 columns=("a", "b", "c", "d"))
        self.vbar = ttk.Scrollbar(self.bottom_frame,
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

    def button_sync_data(self):
        with open('server.json', 'r', encoding='utf-8') as f:
            settings = json.load(f)
        src = settings['copyFrom']
        dst = settings['copyTo']
        os.system('del {}\\*'.format(dst))
        os.system('xcopy {} {}'.format(src, dst))

    def button_refresh_list(self):
        all_file_path = os.listdir('server_logged_devices')
        for file in all_file_path:
            print('处理：', file)
            with open(f'./server_logged_devices/{file}', 'r', encoding='utf-8') as f:
                data = json.load(f)
                # ! ip issues
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
            messagebox.showinfo('注意', '请复制需要执行的命令，软件即将读取剪切板')
            cmd = pyperclip.paste()
            messagebox.showinfo('结果','将执行以下命令：\n{}'.format(cmd))
            self.let_multiple_client_exec_cmd(clientIPs, cmd,)
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
        self.selected_client_index = {}
        self.finally_selected_client = []
        messagebox.showinfo('清空', '选择列表已清空')
        print('选择列表已清空')

    def btn_load_all_ip(self):
        all_file_path = os.listdir('server_logged_devices')
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
        with open('server.json', 'r') as f:
            a = json.load(f)
        CMDPORT = a['cmd_port']
        data = construct_cmd_data(cmd)
        self.send_json(client_ip, CMDPORT, data)


    def let_multiple_client_exec_cmd(self, clientIPs: list, cmd: str):
        for each_client in clientIPs:
            print('当前执行命令的客户端 IP ：{}'.format(each_client))
            self.let_client_exec_cmd(each_client, cmd)


    def run(self):
        self.layout_buttons()
        self.layout_tree()
        self.upper_frame.pack(**self.pad)
        self.bottom_frame.pack(**self.pad)
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


def GUImain():
    app = GUI()
    app.run()


if __name__ == "__main__":
    GUImain()
