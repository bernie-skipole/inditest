
from tkinter import *
from tkinter import ttk
from tkinter import font

import queue

from .messages import MessageScreen
from .devices import DevicesScreen
from .parent import ScreenChooser


def rungui(txque, rxque):
    """txque is the queue to transmit data
       rxque is the queue of received data"""
    root = Tk()
    root.title("Indi Client")
    root.minsize(600, 450)  # width, height
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    applicationframe = ttk.Frame(root, padding="3 3 3 3")
    applicationframe.grid(column=0, row=0, sticky=(N, W, E, S))
    applicationframe.columnconfigure(0, weight=1)
    applicationframe.rowconfigure(1, weight=1)


    schooser = ScreenChooser()
    # create screens
    screens = {
                "Devices": DevicesScreen(txque, rxque, root, applicationframe, schooser),
                "Messages": MessageScreen(txque, rxque, root, applicationframe, schooser),
              }
    schooser.addscreens(screens)

    screens["Messages"].readrxque()

    root.mainloop()
    txque.put(None)
