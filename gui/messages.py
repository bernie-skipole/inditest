from tkinter import *
from tkinter import ttk
from tkinter import font

import queue

from .parent import ParentScreen, localtimestring

class MessageScreen(ParentScreen):

    def __init__(self, txque, rxque, root, sc, snapshot=None):
        super().__init__(txque, rxque, root, sc, snapshot)
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

        # main frame  This has two columns, uses columnspan=2
        self.message_widgets = []
        for r in range(8):
            m = ttk.Label(self.mainframe, text="")
            m.grid(column=0, row=r, columnspan=2, pady=3, sticky=W)
            self.message_widgets.append(m)

        # reverse the widget order so when messages added, the current one is at the bottom
        self.message_widgets.reverse()
        self.message_widgets[0].configure(font=self.bold_font)

        ttk.Separator(self.mainframe, orient=HORIZONTAL).grid(column=0, row=9, columnspan=2, pady=20, sticky=(W, E))

        self.bloblabel = ttk.Label(self.mainframe, text="Enable BLOBs:")
        self.bloblabel.grid(column=0, row=10, padx=3, sticky=E)

        self.blobbutton = ttk.Button(self.mainframe, text="Enable")
        self.blobbutton.grid(column=1, row=10, padx=3, sticky=W)

        # set mainframe grid to expand
        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.columnconfigure(1, weight=1)
        self.mainframe.rowconfigure(9, weight=1)

        # button frame
        # remove messages and vectors buttons
        self.hide_button("Messages")
        self.hide_button("Vectors")

        # initially disable Devices button
        #self.disable_button("Devices")

        self.connected = False
        self.enable = False


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
         #   if self.enable:
         #       self.enable_button("Devices")
         #   else:
         #       self.disable_button("Devices")
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
          #      if enable:
          #          self.enable_button("Devices")
          #      else:
          #          self.disable_button("Devices")
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
