
"""An example tkinter gui which connects
   to the server created by simulated_led.py
   and displays the LED status and a toggle switch

   simulated_led.py should be set running from another
   command prompt.
"""

import queue, threading

from tkinter import *
from tkinter import ttk

# import the function runqueclient which can
# be run in a thread to operate a QueClient

import sys
sys.path.insert(0, "/home/bernard/git/indipyclient")

from indipyclient.queclient import runqueclient


class LEDWindow:

    def __init__(self, root, txque, rxque):

        self.root = root
        self.rxque = rxque
        self.txque = txque

        # create a frame
        self.applicationframe = ttk.Frame(self.root, padding="3 3 3 3")
        self.applicationframe.grid(column=0, row=0, sticky=(N, W, E, S))
        self.applicationframe.columnconfigure(0, weight=1)

        # row 0 will hold the 'connected' label, and will not exapand
        # row 1 will hold the LED status label, and will expand
        # row 2 will hold the switch, and will expand
        self.applicationframe.rowconfigure(1, weight=1)
        self.applicationframe.rowconfigure(2, weight=1)

        # request a snapshot
        self.txque.put('snapshot')
        # This is the current working snapshot of the client
        self.snapshot = None

        # create the frame contents:

        # connected label, on row 0
        self.clabel = ttk.Label(self.applicationframe, text="Not Connected")
        self.clabel.grid(column=0, row=0)

        # The LED value, on row 1
        self.ledval = ttk.Label(self.applicationframe, text="Unknown")
        self.ledval.grid(column=0, row=1)

        # The LED switch, on row 2
        self.ledswitch = ttk.Button(self.applicationframe, text="Toggle LED", command=self.toggle)
        self.ledswitch.grid(column=0, row=2)
        self.ledswitch.state(['disabled'])


    def checkconnected(self):
        "Return True if connected, otherwise False"
        if (self.snapshot is None) or (not self.snapshot.connected):
            if self.clabel["text"] == "Not Connected":
                # no change
                return False
            # so previously was connected, change the labels
            self.clabel["text"] = "Not Connected"
            self.ledval["text"] = "Unknown"
            self.ledswitch.state(['disabled'])
            return False
        # So a snapshot is available and this is connected:
        if self.clabel["text"] == "Connected":
            # no change
            return True
        # so previously was not connected, change the label
        self.clabel["text"] = "Connected"
        self.setLED()
        self.ledswitch.state(['!disabled'])
        return True


    def toggle(self):
        if not self.checkconnected():
            # Not connected, nothing to do
            return
        # send instruction to toggle
        if self.ledval["text"] == "On":
            self.txque.put( ("led", "ledvector", {"ledmember": "Off"}) )
        elif self.ledval["text"] == "Off":
            self.txque.put( ("led", "ledvector", {"ledmember": "On"}) )


    def setLED(self):
        "Reads the snapshot and sets the LED value"
        try:
            led = self.snapshot["led"]["ledvector"]["ledmember"]
        except:
            # in case these values are not available
            return
        current_state = self.ledval["text"]
        if led == "On" and current_state != "On":
            self.ledval["text"] = "On"
        elif led == "Off" and current_state != "Off":
            self.ledval["text"] = "Off"


    def readrxque(self):
        "Read rxque, and if something available, call self.update(item)"
        try:
            item = self.rxque.get_nowait()
        except queue.Empty:
            pass
        else:
            self.update(item)
        # and read again after 100ms
        self.root.after(100, self.readrxque)


    def update(self, item):
        """Called on receiving an update,
           Get the snapshot and set the displayed LED value"""
        self.snapshot = item.snapshot
        # check if connected
        if not self.checkconnected():
            # Not connected, nothing to do
            return
        self.setLED()



def rungui(txque, rxque):
    """Creates the tkinter window and runs the gui loop
       txque is the queue to transmit data
       rxque is the queue of received data"""
    root = Tk()
    root.title("LED Client")
    root.minsize(200, 100)  # width, height
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    # create the application window
    ledwindow = LEDWindow(root, txque, rxque)

    # start checking the rxque
    ledwindow.readrxque()

    # run the gui loop
    root.mainloop()
    # When the loop ends, transmit a None value to shut down the queclient
    txque.put(None)


if __name__ == "__main__":

    # create two queues
    # rxque giving received data
    rxque = queue.Queue(maxsize=4)
    # txque transmit data
    txque = queue.Queue(maxsize=4)

    # run the queclient in its own thread
    clientthread = threading.Thread(target=runqueclient, args=(txque, rxque))
    # The args argument could also have hostname and port specified
    # if the LED server is running elsewhere
    clientthread.start()

    # run the gui code, which displays the window and
    # writes and reads items on these queues
    rungui(txque, rxque)
    # and wait for the clientthread to stop
    clientthread.join()
