
from tkinter import *
from tkinter import ttk
from tkinter import font

import queue

from .messages import MessageScreen


def appframe(root):

    frame = ttk.Frame(root, padding="3 3 3 3")
    frame.grid(column=0, row=0, sticky=(N, W, E, S))
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(1, weight=1)
    return frame



def rungui(txque, rxque):
    """txque is the queue to transmit data
       rxque is the queue of received data"""
    root = Tk()
    root.title("Indi Client")
    root.minsize(600, 450)  # width, height
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    # create screen
    screen = MessageScreen(txque, rxque, root)
    # run screen
    screen.readrxque()
    root.mainloop()
    txque.put(None)
