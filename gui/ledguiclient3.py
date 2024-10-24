
"""An example Dear PyGui client which connects
   to the server created by simulated_led.py
   and displays the LED status and a toggle switch

   simulated_led.py should be set running from another
   command prompt.
"""


import queue, threading


# import the function runqueclient which can
# be run in a thread to operate a QueClient

from indipyclient.queclient import runqueclient

import dearpygui.dearpygui as dpg


class LEDWidgets:
    "Holds reference to widgets, and methods to act on them"

    def __init__(self, txque, rxque, clabel, ledval, ledswitch):
        self.txque = txque
        self.rxque = rxque
        self.snapshot = None
        self.clabel = clabel
        self.ledval = ledval
        self.ledswitch = ledswitch

    def update(self, item):
        """Called on receiving an update,
           Get the snapshot and set the displayed LED value"""
        self.snapshot = item.snapshot
        # check if connected
        if self.checkconnected():
            self.setLED()

    def checkconnected(self):
        "Return True if connected, otherwise False"
        if (self.snapshot is None) or (not self.snapshot.connected):
            if dpg.get_value(self.clabel) == "Not Connected":
                # no change
                return False
            # so previously was connected, change the labels
            dpg.set_value(self.clabel, "Not Connected")
            dpg.set_value(self.ledval, "Unknown")
            dpg.configure_item(self.ledswitch, enabled=False)
            return False
        # So a snapshot is available and this is connected:
        if dpg.get_value(self.clabel) == "Connected":
            # no change
            return True
        # so previously was not connected, change the label
        dpg.set_value(self.clabel, "Connected")
        self.setLED()
        dpg.configure_item(self.ledswitch, enabled=True)
        return True

    def setLED(self):
        "Reads the snapshot and sets the LED value"
        try:
            led = self.snapshot["led"]["ledvector"]["ledmember"]
        except:
            # in case these values are not available
            return
        current_state = dpg.get_value(self.ledval)
        if led == "On" and current_state != "On":
            dpg.set_value(self.ledval, "On")
        elif led == "Off" and current_state != "Off":
            dpg.set_value(self.ledval, "Off")

    def toggle(self):
        "Called when the button is clicked"
        if not self.checkconnected():
            # Not connected, nothing to do
            return
        # send instruction to toggle
        if dpg.get_value(self.ledval) == "On":
            self.txque.put( ("led", "ledvector", {"ledmember": "Off"}) )
        elif dpg.get_value(self.ledval) == "Off":
            self.txque.put( ("led", "ledvector", {"ledmember": "On"}) )



def rungui(txque, rxque):

    dpg.create_context()

    # add a font registry
    with dpg.font_registry():
        default_font = dpg.add_font("Roboto/Roboto-Medium.ttf", 20)

    with dpg.window(tag="Main Window"):
        # set font of window
        dpg.bind_font(default_font)
        # connected label
        clabel = dpg.add_text("Not Connected")
        # LED value label
        ledval = dpg.add_text("Unknown")
        # toggle button
        ledswitch = dpg.add_button(label="Toggle LED", enabled=False)

    with dpg.theme() as button_theme:
        with dpg.theme_component(dpg.mvButton, enabled_state=False):
            dpg.add_theme_color(dpg.mvThemeCol_Text, [0, 0, 0])
            dpg.add_theme_color(dpg.mvThemeCol_Button, [128, 128, 128])
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [128, 128, 128])
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [128, 128, 128])

        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Text, [255, 255, 0])
            dpg.add_theme_color(dpg.mvThemeCol_Button, [0, 0, 150])
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [0, 0, 200])
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [0, 0, 255])

    dpg.bind_theme(button_theme)


    dpg.create_viewport(title='LED Client', width=250, height=120,  min_width=250, min_height=120)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("Main Window", True)

    # create a LEDWidgets object
    ledwidgets = LEDWidgets(txque, rxque, clabel, ledval, ledswitch)

    # add callback to button to widget.toggle()
    dpg.configure_item(ledswitch, callback=ledwidgets.toggle)

    # read rxque in the render loop
    while dpg.is_dearpygui_running():
        try:
            item = rxque.get_nowait()
        except queue.Empty:
            pass
        else:
            ledwidgets.update(item)
        # render the frame
        dpg.render_dearpygui_frame()

    dpg.destroy_context()


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
