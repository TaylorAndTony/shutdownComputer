from tkinter import *
from tkinter import ttk

class InputBox:
    """
    一个用于获取用户输入的输入框，用法如下：
    ib = InputBox('hello', '请输入信息：')
    print(ib.result)
    """
    def __init__(self, title, description):
        self.root = Tk()
        self.root.title(title)
        self.desc = description
        self.entry = Entry(self.root, width=40)
        self.button = ttk.Button(self.root, text='确定', command=self.getText)
        self.result = ''
        self.layout()
        self.run()
    
    def layout(self):
        Label(self.root, text=self.desc).pack(padx=10, pady=10)
        self.entry.pack(padx=10, pady=10)
        self.button.pack(padx=10, pady=10)

    def getText(self):
        self.result = self.entry.get()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == '__main__':
    ib = InputBox('hello', '请输入信息：')
    print(ib.result)