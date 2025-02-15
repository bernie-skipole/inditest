
"""An example pygtk3 gui which connects
   to the server created by simulated_led.py
   and displays the LED status and a toggle switch

   simulated_led.py should be set running from another
   command prompt.
"""


import queue, threading

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

# import the function runqueclient which can
# be run in a thread to operate a QueClient

from indipyclient.queclient import runqueclient


class LEDWindow:

    def __init__(self, topwin, txque, rxque):

        self.topwin = topwin
        self.rxque = rxque
        self.txque = txque

        # request a snapshot
        self.txque.put((None, None, 'snapshot'))
        # This is the current working snapshot of the client
        self.snapshot = None

        # create a scrolled window and add it to the topwin:

        self.swin = Gtk.ScrolledWindow()
        self.topwin.add(self.swin)

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.swin.add(self.box)

        # connected label, on row 0
        self.clabel = Gtk.Label(label="Not Connected")
        self.box.pack_start(self.clabel, True, True, 0)

        # The LED value, on row 1
        self.ledval = Gtk.Label(label="Unknown")
        self.box.pack_start(self.ledval, True, True, 0)


        # The LED switch, on row 2
        self.ledswitch = Gtk.Button.new_with_label("Toggle LED")
        self.ledswitch.set_halign(Gtk.Align.CENTER)
        self.ledswitch.set_sensitive(False)
        self.ledswitch.connect("clicked", self.toggle)
        self.box.pack_start(self.ledswitch, True, False, 0)


    def checkconnected(self):
        "Return True if connected, otherwise False"
        if (self.snapshot is None) or (not self.snapshot.connected):
            if self.clabel.get_text() == "Not Connected":
                # no change
                return False
            # so previously was connected, change the labels
            self.clabel.set_text("Not Connected")
            self.ledval.set_text("Unknown")
            self.ledswitch.set_sensitive(False)
            return False
        # So a snapshot is available and this is connected:
        if self.clabel.get_text() == "Connected":
            # no change
            return True
        # so previously was not connected, change the label
        self.clabel.set_text("Connected")
        self.setLED()
        self.ledswitch.set_sensitive(True)
        return True


    def toggle(self, button):
        "Called when the button is clicked"
        if not self.checkconnected():
            # Not connected, nothing to do
            return
        # send instruction to toggle
        if self.ledval.get_text() == "On":
            self.txque.put( ("led", "ledvector", {"ledmember": "Off"}) )
        elif self.ledval.get_text() == "Off":
            self.txque.put( ("led", "ledvector", {"ledmember": "On"}) )


    def setLED(self):
        "Reads the snapshot and sets the LED value"
        try:
            led = self.snapshot["led"]["ledvector"]["ledmember"]
        except:
            # in case these values are not available
            return
        current_state = self.ledval.get_text()
        if led == "On" and current_state != "On":
            self.ledval.set_text("On")
        elif led == "Off" and current_state != "Off":
            self.ledval.set_text("Off")


    def readrxque(self):
        "Read rxque, and if something available, call self.setLED()"
        try:
            item = self.rxque.get_nowait()
        except queue.Empty:
            pass
        else:
            # Get the snapshot and set the displayed LED value
            self.snapshot = item.snapshot
            if self.checkconnected():
                self.setLED()
        # as this is a timeout call, return True to continue calling
        return True



def rungui(txque, rxque):
    """Creates the Gtk window and runs the gui loop
       txque is the queue to transmit data
       rxque is the queue of received data"""

    topwin = Gtk.Window(title="LED Client")
    topwin.set_default_size(200, 100)  # width, height
    topwin.connect("destroy", Gtk.main_quit)

    # create the application window
    ledwindow = LEDWindow(topwin, txque, rxque)

    # every 100ms call ledwindow.readrxque
    timeout_id = GLib.timeout_add(100, ledwindow.readrxque)

    topwin.show_all()
    # run the gui loop
    Gtk.main()


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
    # When the gui loop ends, transmit a None value to shut down the queclient
    txque.put(None)
    # and wait for the clientthread to stop
    clientthread.join()
