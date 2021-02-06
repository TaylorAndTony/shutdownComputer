import tkinter as tk
from datetime import datetime

def give_me_date():
    """get the current date and time"""
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

class SimpleGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.ipLabel = tk.Label(self.root, text='IP地址：')
        self.commPort = tk.Label(self.root, text='通讯端口：')
        self.cmdPort = tk.Label(self.root, text='命令端口：')
        self.msg = tk.Text(self.root)
        self.clearButton = tk.Button(self.root, text='清空', command=self.clear)

    def setIp(self, ip):
        self.ipLabel['text'] = f'IP地址：{ip}'

    def setCommPort(self, commPort):
        self.commPort['text'] = f'IP地址：{commPort}'

    def setCmdPort(self, cmdPort):
        self.cmdPort['text'] = f'IP地址：{cmdPort}'
    
    def addOutput(self, msg):
        self.msg.insert(tk.END, give_me_date() + msg + '\n')
        self.msg.see(tk.END)

    def clear(self):
        self.msg.delete(0.0, tk.END)

    def layout(self):
        self.ipLabel.pack()
        self.commPort.pack()
        self.cmdPort.pack()
        self.msg.pack()
        self.clearButton.pack()

    def run_before_start(self):
        self.addOutput('已记录客户端启动')
        self.addOutput('数据发送已启动')
        self.addOutput('命令监听已启动')

    def run(self):
        self.layout()
        self.root.mainloop()


if __name__ == '__main__':
    app = SimpleGUI()
    app.run_before_start()
    app.run()