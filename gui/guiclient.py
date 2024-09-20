
from tkinter import *
from tkinter import ttk
from tkinter import font

import queue

def localtimestring(t):
    "Return a string of the local time (not date)"
    localtime = t.astimezone(tz=None)
    # convert microsecond to integer between 0 and 100
    ms = localtime.microsecond//10000
    return f"{localtime.strftime('%H:%M:%S')}.{ms:0>2d}"

def appframe(root):
    root.title("Indi Client")
    root.minsize(600, 400)  # width, height
    frame = ttk.Frame(root, padding="3 3 3 3")
    frame.grid(column=0, row=0, sticky=(N, W, E, S))
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(1, weight=1)
    return frame



class ParentScreen:

    def __init__(self, txque, rxque, root, applicationframe, snapshot=None):
        self.txque = txque
        self.rxque = rxque
        self.root = root
        self.applicationframe = applicationframe
        self.tframe = self.topframe(applicationframe)
        self.mainframe = self.middleframe(applicationframe)
        self.butframe = self.buttonframe(applicationframe)
        self.rxrecieved = None
        # This is the current working snapshot of the client
        self.snapshot = snapshot
        if snapshot is None:
            # request a snapshot
            self.tx_data('snapshot')


    def readrxque(self):
        "Read rxque, and if something available, set it into rxrecieved"
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

    def topframe(self, applicationframe):
        frame = ttk.Frame(applicationframe, padding="3 3 12 12", borderwidth=5)
        frame.grid(column=0, row=0, sticky=(N, W, E))
        frame.columnconfigure(0, weight=1)
        return frame


    def middleframe(self, applicationframe):
        frame = ttk.Frame(applicationframe, padding="3 3 3 12", borderwidth=5, relief='groove')
        frame.grid(column=0, row=1, sticky=(N, W, E, S))
        return frame


    def buttonframe(self, applicationframe):
        frame = ttk.Frame(applicationframe, padding="3 3 3 3", borderwidth=5)
        frame.grid(column=0, row=2, sticky=(N, W, E, S))
        # Create buttons and set them in the frame
        self.m_butt = ttk.Button(frame, text="Messages")
        self.m_butt.grid(column=1, row=0)
        self.d_butt = ttk.Button(frame, text="Devices")
        self.d_butt.grid(column=2, row=0)
        self.v_butt = ttk.Button(frame, text="Vectors")
        self.v_butt.grid(column=3, row=0)
        self.q_butt = ttk.Button(frame, text="Quit", command=lambda: self.tx_data(None))
        self.q_butt.grid(column=4, row=0)
        frame.columnconfigure(0, weight=2)
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=1)
        frame.columnconfigure(3, weight=1)
        frame.columnconfigure(4, weight=1)
        frame.columnconfigure(5, weight=2)
        return frame

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
        if data is None:
            # destroy root
            self.root.destroy()




class MessageScreen(ParentScreen):

    def __init__(self, txque, rxque, root, applicationframe, snapshot=None):
        super().__init__(txque, rxque, root, applicationframe, snapshot)
        # top frame
        mtitle = ttk.Label(self.tframe, text="Messages")
        mtitle.grid(column=0, row=0, sticky=W)

        # get a bold font by obtaining the font from the mtitle label
        # this will be used to set the title bold, and also message labels bold
        self.bold_font = font.Font(root, mtitle.cget("font"))
        self.bold_font.configure(weight=font.BOLD)
        mtitle.configure(font=self.bold_font)

        self.status = ttk.Label(self.tframe, text="Not connected")
        self.status.grid(column=0, row=1)

        # main frame
        self.message_widgets = []
        for r in range(8):
            m = ttk.Label(self.mainframe, text="")
            m.grid(column=0, row=r, pady=3, sticky=W)
            self.message_widgets.append(m)

        # reverse the widget order so when messages added, the current one is at the bottom
        self.message_widgets.reverse()
        self.message_widgets[0].configure(font=self.bold_font)

        ttk.Separator(self.mainframe, orient=HORIZONTAL).grid(column=0, row=9, pady=20, sticky=(W, E))
        ttk.Label(self.mainframe, text="hello").grid(column=0, row=11)

        # set mainframe grid to expand
        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.rowconfigure(12, weight=1)

        # button frame
        # remove messages and vectors buttons
        self.hide_button("Messages")
        self.hide_button("Vectors")

        # initially disable Devices button
        self.disable_button("Devices")

        self.connected = False
        self.enable = False

        # and start the checking readrxque
        self.readrxque()


    def updatescreen(self):
        "To handle received messages"
        # recieved item has attributes 'eventtype', 'devicename', 'vectorname', 'timestamp', 'snapshot'

        if self.snapshot is None:
            self.snapshot = self.rxrecieved.snapshot
            self.connected = self.snapshot.connected
            self.enable = self.snapshot.enable
            if self.connected:
                self.status['text'] = "Connected"
            else:
                self.status['text'] = "Not Connected"
            if self.enable:
                self.enable_button("Devices")
            else:
                self.disable_button("Devices")
        else:
            connected = self.rxrecieved.snapshot.connected
            enable = self.rxrecieved.snapshot.enable
            if self.connected != connected:
                # connected state has changed
                self.connected = connected
                if connected:
                    self.status['text'] = "Connected"
                else:
                    self.status['text'] = "Not Connected"
            if self.enable != enable:
                # enabled devices has changed
                self.enable = enable
                if enable:
                    self.enable_button("Devices")
                else:
                    self.disable_button("Devices")
            # and set self.snapshot equal to the current received snapshot
            self.snapshot = self.rxrecieved.snapshot

        if self.rxrecieved.eventtype == "Message" and self.rxrecieved.devicename is None:
            messages = self.rxrecieved.snapshot.messages
            # messages is a list of (Timestamp, message) tuples
            mlist = [ localtimestring(t) + "  " + m for t,m in messages ]
            if mlist:
                 for index,lbl in enumerate(self.message_widgets):
                    try:
                        lbl['text'] = mlist[index]
                    except IndexError:
                        lbl['text'] = ""
        self.rxrecieved = None




def rungui(txque, rxque):
    """txque is the queue to transmit data
       rxque is the queue of received data"""

    root = Tk()
    applicationframe = appframe(root)
    screen = MessageScreen(txque, rxque, root, applicationframe)
    root.mainloop()
    txque.put(None)
