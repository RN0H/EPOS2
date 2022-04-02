#from epos2 import *
#from epos2_plotter import *
from tkinter import*
from tkinter.ttk import*
import tkinter as tk
from tkinter import ttk
# from ttkthemes import ThemedStyle


class driver():
    def __init__ (self,master):
        self.master = master
        self.master.geometry("600x600")
        self.master.title("Our_Epos2_Studio")
        # theme = ThemedStyle(self.master)
        # theme.set_theme('radiance')
        self.configs = {
                  "nodeID":       2,            #nodeID = 2
                  "baudrate":     1000000,      #baudrate = 1000000
                  "timeout":      500,          #timeout = 500
                  "acceleration": 5000,         #up to 1e7 would be possible
                  "deceleration": 5000
                  }
        self.wait = False                       #Queue
        self.cnt = StringVar();                 #Play Count
        self.flag = Label(self.master)          #Flag label
        self.ps = Label(self.master)            #position label
        self.cr = Label(self.master)            #current label
        b1 = Button(self.master,text="Set Home",command=self.Home)
        b2 = Button(self.master,text="Set parameters",command=self.set_parameters)
        b3 = Button(self.master,text="Halt",command=self.halt)
        b4 = Button(self.master,text="Signal",command = self.signal)
        b5 = Button(self.master,text="Play",command=self.play)
        e1 = Entry(self.master,textvariable=self.cnt)
        for _ in (b1,b2,b3,b4,self.flag):
            _.pack()
        e1.place(x=230,y=300)
        x = Label(self.master, text = "Counter =>")
        x.place(x = 150, y = 300)

    def set_parameters(self):
        try:
            if not self.wait:
                    node2 = Epos2(**self.configs);
        except:
            self.flag.config(text="Error Setting Parameters or Another Process Running..")

    def Home(self):
        try:
            if not self.wait:
                    node2.Homing_Mode(0)                             #Dont Home If posn==0qc else Home
        except:
            self.flag.config(text="Error Setting Home or Another Process Running..")

    def halt(self):
        try:
            if not self.wait:
                    node2.Disable();
        except:
            self.flag.config(text="Error Disabling or Another Process Running..")

    def signal(self):
        try:
            if not self.wait:
                node2.Digiin();
        except:
            self.flag.config(text="Error in Digital Input or Another Process Running")


    def play(self):
        '''
        This is just for purpose of 
        switching modes of the Maxon Motor
        and playing with it in loop.
        '''
        if self.cnt.get()==0:return ""
        elif self.wait:self.flag.config(text="Please Wait")
        else:
            try:                                    
                cnt = self.cnt.get()
                self.wait = True
                while cnt:
                    time.sleep(1)                                #Buffer
                    print("POSITION MODE ----->")
                    node2.Position_Mode(1100000,2000)            #Position mode
                    time.sleep(2)                                #Buffer
                    print("CURRENT MODE ------>")
                    node2.Current_Mode(node2.pos_current+500)    #Current draw in position mode + 700
                    time.sleep(3)                                #Buffer
                    node2.Go_Home(0,2000)                        #Back to Home
                    cnt-=1
                self.wait = False
                node2.Disable();                                 #Disable
                print("Done")
            except:
                self.flag.config(text="Error Playing or Another Process Running..")

if __name__ =="__main__":
        master = tk.Tk()
        driver(master)
        master.mainloop()
