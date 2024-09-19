
from tkinter import *
from tkinter import ttk


def appframe(root):
    root.title("Indi Client")
    root.minsize(600, 400)  # width, height
    frame = ttk.Frame(root, padding="3 3 3 3")
    frame.grid(column=0, row=0, sticky=(N, W, E, S))
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)
    return frame



class ParentScreen:

    def __init__(self, txque, rxque, root, applicationframe):
        self.txque = txque
        self.rxque = rxque
        self.root = root
        self.applicationframe = applicationframe
        self.tframe = self.topframe(applicationframe)
        self.mainframe = self.middleframe(applicationframe)
        self.butframe = self.buttonframe(applicationframe)


    def topframe(self, applicationframe):
        frame = ttk.Frame(applicationframe, padding="3 3 12 12", borderwidth=5, relief='groove')
        frame.grid(column=0, row=0, sticky=(N, W, E, S))
        return frame


    def middleframe(self, applicationframe):
        frame = ttk.Frame(applicationframe, padding="3 3 12 12", borderwidth=5, relief='groove')
        frame.grid(column=0, row=1, sticky=(N, W, E, S))
        return frame


    def buttonframe(self, applicationframe):
        frame = ttk.Frame(applicationframe, padding="3 3 3 3", borderwidth=5)#, relief='groove')
        frame.grid(column=0, row=2, sticky=(N, W, E, S))

        ttk.Button(frame, text="One").grid(column=1, row=0)
        ttk.Button(frame, text="Two").grid(column=2, row=0)
        ttk.Button(frame, text="Three").grid(column=3, row=0)
        ttk.Button(frame, text="Quit", command=lambda: self.tx_data(None)).grid(column=4, row=0)
        frame.columnconfigure(0, weight=2)
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=1)
        frame.columnconfigure(3, weight=1)
        frame.columnconfigure(4, weight=1)
        frame.columnconfigure(5, weight=2)
        return frame


    def tx_data(self, data):
        self.txque.put(data)
        if data is None:
            # destroy root
            self.root.destroy()




class MessageScreen(ParentScreen):

    def __init__(self, txque, rxque, root, applicationframe):
        super().__init__(txque, rxque, root, applicationframe)
        self.feet = StringVar()
        feet_entry = ttk.Entry(self.mainframe, width=7, textvariable=self.feet)
        feet_entry.grid(column=2, row=1, sticky=(W, E))
        self.meters = StringVar()

        ttk.Label(self.mainframe, textvariable=self.meters).grid(column=2, row=2, sticky=(W, E))
        ttk.Button(self.mainframe, text="Calculate", command=self.calculate).grid(column=3, row=3, sticky=W)

        ttk.Label(self.mainframe, text="feet").grid(column=3, row=1, sticky=W)
        ttk.Label(self.mainframe, text="is equivalent to").grid(column=1, row=2, sticky=E)
        ttk.Label(self.mainframe, text="meters").grid(column=3, row=2, sticky=W)

        for child in self.mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)

        feet_entry.focus()


    def calculate(self, *args):
        try:
            value = float(self.feet.get())
            self.meters.set(int(0.3048 * value * 10000.0 + 0.5)/10000.0)
        except ValueError:
            pass


def rungui(txque, rxque):
    """txque is the queue to transmit data
       rxque is the queue of received data"""

    root = Tk()
    applicationframe = appframe(root)
    screen = MessageScreen(txque, rxque, root, applicationframe)
    root.mainloop()
    txque.put(None)
