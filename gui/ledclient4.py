
import asyncio, queue, threading, logging

from typing import Iterable

from textual.app import App, ComposeResult, SystemCommand
from textual.widgets import Footer, Static, Button
from textual.reactive import reactive
from textual.screen import Screen
from textual.containers import Center

from indipyclient.queclient import runqueclient

# Turn off logging so screen not messed up with messages
logger = logging.getLogger()
logger.addHandler(logging.NullHandler())


# create two queues
# RXQUE giving received data
RXQUE = queue.Queue(maxsize=4)
# TXQUE transmit data
TXQUE = queue.Queue(maxsize=4)


class IsConnected(Static):
    "A widget to display connected status."

    connected = reactive(False)

    def render(self) -> str:
        if self.connected:
            return "Connected"
        return "Not Connected"


class LedValue(Static):
    "A widget to display LED state"

    state = reactive("Unknown")

    def validate_state(self, state: str) -> str:
        """Validate state."""
        if state in ("On", "Off"):
            return state
        return "Unknown"

    def render(self) -> str:
        return self.state



class LEDControl(App):
    """A Textual app to manage an INDI controlled LED."""

    CSS = """

            Screen {
               align: center middle;
               }

            #title {
               background: $primary;
               color: $text;
               padding-left: 2;
               dock: top;
               }

            .widg {
                   width: 16;
                   text-align: center;
                   margin: 2;
                  }


         """

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode"),
                ("t", "toggle_LED", "Toggle LED"),
                ("q", "quit", "Quit")]

    ENABLE_COMMAND_PALETTE = False

    state = reactive("Unknown")
    connected = reactive(False)

    def on_mount(self) -> None:
        """Event handler called when widget is added to the app."""
        # Check the RXQUE every 0.1 of a second
        self.set_interval(1 / 10, self.check_rxque)

    def check_rxque(self) -> None:
        """Method to handle received data."""
        try:
            item = RXQUE.get_nowait()
        except queue.Empty:
            return
        self.connected = item.snapshot.connected
        if not self.connected:
            self.state = "Unknown"
            self.query_one(Button).disabled = True
            return
        self.query_one(Button).disabled = False
        # so connected, check the led
        if item.devicename == "led" and item.vectorname == "ledvector":
            self.state = item.snapshot["led"]["ledvector"].get("ledmember")

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Static("LED Control", id="title")
        with Center():
            yield IsConnected("Not Connected", classes="widg").data_bind(LEDControl.connected)
        with Center():
            yield LedValue("Unknown", classes="widg").data_bind(LEDControl.state)
        with Center():
            yield Button("Toggle LED")
        yield Footer()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    def action_quit(self) -> None:
        """An action to quit the program."""
        self.exit(0)

    def action_toggle_LED(self) -> None:
        """An action to toggle the LED."""
        if not self.connected:
            # Not connected, nothing to do
            return
        # send instruction to toggle the led onto TXQUE
        if self.state == "On":
            TXQUE.put( ("led", "ledvector", {"ledmember": "Off"}) )
        elif self.state == "Off":
            TXQUE.put( ("led", "ledvector", {"ledmember": "On"}) )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed. In this case there
           is only one button, so do not have to be more specific.
           This calls action_toggle_LED, so is the same action as t being pressed"""
        self.action_toggle_LED()
        return


if __name__ == "__main__":

    # run the queclient in its own thread
    clientthread = threading.Thread(target=runqueclient, args=(TXQUE, RXQUE))
    # The args argument could also have hostname and port specified
    # if the LED server is running elsewhere
    clientthread.start()

    # run the terminal LEDControl app
    app = LEDControl()
    app.run()
    # When the LEDControl app stops, transmit a None value to shut down the queclient
    TXQUE.put(None)
    # and wait for the clientthread to stop
    clientthread.join()
