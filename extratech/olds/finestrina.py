#finestrina
import threading
from tkinter import *
from tkthread import tk, TkThread



class Finestrina():
    def __init__(self, eventoFinaleTremendo, tc):
        self.tc                = tc
        self.finished         = eventoFinaleTremendo
        # self.start()
        self.window = tk.Tk()
        self.tkThread = TkThread(self.window)
        self.window.title('hallo')
        self.window.attributes("-fullscreen", False)
        self.window.resizable(width=True, height=True)
        self.window.geometry('600x200')
        self.finestrina= Frame(self.window, highlightbackground=self.rgb_hack((10,240,10)) ,highlightcolor=self.rgb_hack((10,240,10)), highlightthickness=3)
        self.finestrina.place(in_=self.window, anchor="c", relx=.5, rely=.5)
        self.label = Label(self.finestrina, text=self.tc).grid(row=1, column=1, columnspan=3, padx=25, pady=(15, 0))
   
    def run(self):
        def looppa():
            if not self.finished.is_set():
                self.label.text = self.tc

                self.window.update()
                self.window.mainloop()
        looppoTredd = threading.Thread(target=looppa).start()
        
    def rgb_hack(self, rgb):
        return "#%02x%02x%02x" % rgb  
