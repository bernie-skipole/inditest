
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
    load_window = Toplevel(root)
    schooser = ScreenChooser()
    # create screens
    screens = {
                "Devices": DevicesScreen(txque, rxque, load_window, schooser),
                "Messages": MessageScreen(txque, rxque, load_window, schooser),
              }
    schooser.addscreens(screens)

    # run screen
    screens["Messages"].readrxque()

    root.mainloop()
    txque.put(None)
