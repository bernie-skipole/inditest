

from tkinter import *
from tkinter import ttk

import queue

def localtimestring(t):
    "Return a string of the local time (not date)"
    localtime = t.astimezone(tz=None)
    # convert microsecond to integer between 0 and 100
    ms = localtime.microsecond//10000
    return f"{localtime.strftime('%H:%M:%S')}.{ms:0>2d}"



class ParentScreen:

    def __init__(self, txque, rxque, root, snapshot=None):
        self.txque = txque
        self.rxque = rxque
        self.root = root
        self.applicationframe = ttk.Frame(root, padding="3 3 3 3")
        self.applicationframe.grid(column=0, row=0, sticky=(N, W, E, S))
        self.applicationframe.columnconfigure(0, weight=1)
        self.applicationframe.rowconfigure(1, weight=1)
        self.tframe = self.topframe()
        self.mainframe = self.middleframe()
        self.butframe = self.buttonframe()
        self.rxrecieved = None
        # This is the current working snapshot of the client
        self.snapshot = snapshot
        if snapshot is None:
            # request a snapshot
            self.tx_data('snapshot')

    def readrxque(self):
        "Read rxque, and if something available, set it into self.rxrecieved"
        if self.rxrecieved is None:
            try:
                item = self.rxque.get_nowait()
            except queue.Empty:
                pass
            else:
                self.rxrecieved = item
                self.updatescreen()
        self.root.after(100, self.readrxque) # 100 ms


    def updatescreen(self):
        "To be overridden by child widgets"
        self.rxrecieved = None

    def topframe(self):
        frame = ttk.Frame(self.applicationframe, padding="3 3 12 12", borderwidth=5)
        frame.grid(column=0, row=0, sticky=(N, W, E))
        frame.columnconfigure(0, weight=1)
        return frame


    def middleframe(self):
        frame = ttk.Frame(self.applicationframe, padding="3 3 3 12", borderwidth=5, relief='groove')
        frame.grid(column=0, row=1, sticky=(N, W, E, S))
        return frame


    def buttonframe(self):
        frame = ttk.Frame(self.applicationframe, padding="3 3 3 3", borderwidth=5)
        frame.grid(column=0, row=2, sticky=(N, W, E, S))
        # Create buttons and set them in the frame
        self.m_butt = ttk.Button(frame, text="Messages")
        self.m_butt.grid(column=1, row=0)
        self.d_butt = ttk.Button(frame, text="Devices")
        self.d_butt.grid(column=2, row=0)
        self.v_butt = ttk.Button(frame, text="Vectors")
        self.v_butt.grid(column=3, row=0)
        self.q_butt = ttk.Button(frame, text="Quit", command=self.quit)
        self.q_butt.grid(column=4, row=0)
        frame.columnconfigure(0, weight=2)
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=1)
        frame.columnconfigure(3, weight=1)
        frame.columnconfigure(4, weight=1)
        frame.columnconfigure(5, weight=2)
        return frame

    def quit(self):
        #self.txque.put(None)
        # destroy root
        self.root.destroy()


    def hide_button(self, buttext):
        for btn in self.butframe.grid_slaves():
            if btn['text'] == buttext:
                btn.grid_remove()

    def show_button(self, buttext):
        if buttext == "Messages":
            self.m_butt.grid(column=1, row=0)
        elif buttext == "Devices":
            self.d_butt.grid(column=2, row=0)
        elif buttext == "Vectors":
            self.v_butt.grid(column=3, row=0)
        elif buttext == "Quit":
            self.q_butt.grid(column=4, row=0)

    def disable_button(self, buttext):
        for btn in self.butframe.grid_slaves():
            if btn['text'] == buttext:
                btn.state(['disabled'])

    def enable_button(self, buttext):
        for btn in self.butframe.grid_slaves():
            if btn['text'] == buttext:
                btn.state(['!disabled'])

    def tx_data(self, data):
        self.txque.put(data)
