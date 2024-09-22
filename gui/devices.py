from tkinter import *
from tkinter import ttk
from tkinter import font

import queue

from .parent import ParentScreen, localtimestring

class DevicesScreen(ParentScreen):

    def __init__(self, txque, rxque, root, applicationframe, sc):
        super().__init__(txque, rxque, root, applicationframe, sc)
        # top frame
        ttitle = ttk.Label(self.tframe, text="Devices")
        ttitle.grid(column=0, row=0, sticky=W)

        # get a bold font by obtaining the font from the mtitle label
        # this will be used to set the title bold
        self.bold_font = font.Font(root, ttitle.cget("font"))
        self.bold_font.configure(weight=font.BOLD)
        ttitle.configure(font=self.bold_font)

        self.status = ttk.Label(self.tframe, text="")
        self.status.grid(column=0, row=1)

        # main frame
        # set mainframe grid to expand
        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.columnconfigure(2, weight=1)

        # button frame
        # remove devices and vectors buttons
        self.hide_button("Devices")
        self.hide_button("Vectors")

    def show(self):
        "This updates this screen when it is first shown"
        self.rxrecieved = None
        if self.sc.snapshot is None:
            # no data
            return
        messages = self.sc.snapshot.messages
        if messages:
            t,m = messages[0]
            self.status['text'] = localtimestring(t) + "  " + m
        # clear current devicename buttons
        for widget in self.mainframe.winfo_children():
            widget.destroy()
        # and add current devicename buttons
        rownumber = 0
        for devicename in self.sc.snapshot.keys():
            if self.sc.snapshot[devicename].enable:
                ttk.Button(self.mainframe, text=devicename).grid(column=1, row=rownumber, pady=5, sticky=(E, W))
                rownumber += 1



    def updatescreen(self, item):
        "To handle received item"
        # recieved item has attributes 'eventtype', 'devicename', 'vectorname', 'timestamp', 'snapshot'

        if item.eventtype == "Message" and item.devicename is None:
            # a new 'global' message is received
            messages = item.snapshot.messages
            if messages:
                t,m = messages[0]
                self.status['text'] = localtimestring(t) + "  " + m

        if item.eventtype == "Define" or item.eventtype == "DefineBLOB":
            # and add current devicename buttons
            current_devicenames = set( self.sc.snapshot.keys() )
            if item.devicename not in current_devicenames:
                # add this devicename, first clear current devicename buttons
                for widget in self.mainframe.winfo_children():
                    widget.destroy()
                # update button list of devicenames
                rownumber = 0
                for devicename in item.snapshot.keys():
                    # draw a button for each enabled device
                    if item.snapshot[devicename].enable:
                        ttk.Button(self.mainframe, text=devicename).grid(column=1, row=rownumber, pady=5, sticky=(E, W))
                        rownumber += 1

        if item.eventtype == "Delete":
            # clear current devicename buttons
            for widget in self.mainframe.winfo_children():
                widget.destroy()
            # update button list of devicenames
            rownumber = 0
            for devicename in item.snapshot.keys():
                # draw a button for each enabled device
                if item.snapshot[devicename].enable:
                    ttk.Button(self.mainframe, text=devicename).grid(column=1, row=rownumber, pady=5, sticky=(E, W))
                    rownumber += 1

        # and set self.sc.snapshot equal to the current received snapshot
        self.sc.snapshot = item.snapshot
