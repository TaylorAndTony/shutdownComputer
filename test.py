from tkinter import *
from tkinter import ttk


class PopoutWindow:
    def __init__(self, imgFile, title, message):
        self.llayout = {'padx': 10, 'pady': 10}
        self.root = Tk()
        self.root.title(title)
        # self.root['title'] = title
        self.message = message
        self.photo = PhotoImage(file=imgFile)
        self.leftSide = Frame(self.root)
        self.rightSide = Frame(self.root)
        self.place_main()
        self.place_button()
        self.run()

    def place_main(self):
        Label(self.leftSide, image=self.photo).pack(**self.llayout)
        Label(self.rightSide, text=self.message
              ).pack(**self.llayout)

    def place_button(self):
        ttk.Button(self.root, text='确认', command=lambda: quit()
                   ).grid(row=1, columnspan=2, **self.llayout)

    def run(self):
        self.leftSide.grid(row=0, column=0)
        self.rightSide.grid(row=0, column=1)
        self.root.mainloop()


if __name__ == '__main__':
    PopoutWindow('./img/trash.png', '清空', '已清空选择列表')
