from tkinter import *

class PopoutWindow:
    def __init__(self, imgFile, title, message):
        self.root = Tk()
        # self.root['title'] = title
        self.message = message
        self.photo = PhotoImage(file=imgFile)
        self.leftSide = Frame(self.root)
        self.rightSide = Frame(self.root)
        Label(self.leftSide, image=self.photo).pack()
        Label(self.rightSide, text=self.message).pack()
        self.run()

    def run(self):
        self.leftSide.grid(row=0, column=0)
        self.rightSide.grid(row=0, column=1)
        self.root.mainloop()    
        

if __name__ == '__main__':
    app = PopoutWindow('./img/home.png', 'test', 'hfduivsuhdgfgfhjtrrg')