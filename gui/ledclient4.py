
import asyncio, queue, threading

from typing import Iterable

from textual.app import App, ComposeResult, SystemCommand
from textual.widgets import Header, Footer, Static, Button
from textual.reactive import reactive
from textual.screen import Screen

from indipyclient.queclient import runqueclient


# create two queues
# RXQUE giving received data
RXQUE = queue.Queue(maxsize=4)
# TXQUE transmit data
TXQUE = queue.Queue(maxsize=4)


class IsConnected(Static):
    """A widget to display connected status."""

    connected = reactive(False)

    def render(self) -> str:
        if self.connected:
            return "Connected"
        return "Not Connected"


class LedValue(Static):
    """A widget to display LED value."""

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

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode"),
                ("t", "toggle_LED", "Toggle LED")]


    state = reactive("Unknown")
    connected = reactive(False)

    def on_mount(self) -> None:
        """Event handler called when widget is added to the app."""
        header = self.query_one(Header)
        header.icon = "?"
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
        yield Header()
        yield Footer()
        yield IsConnected("Not Connected").data_bind(LEDControl.connected)
        yield LedValue("Unknown").data_bind(LEDControl.state)
        yield Button("Toggle LED")


    def get_system_commands(self, screen: Screen) -> Iterable[SystemCommand]:
        yield from super().get_system_commands(screen)
        yield SystemCommand("Toggle", "Toggle the LED", self.action_toggle_LED)

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    def action_toggle_LED(self) -> None:
        """An action to toggle the LED."""
        if not self.connected:
            # Not connected, nothing to do
            return
        # send instruction to toggle
        if self.state == "On":
            TXQUE.put( ("led", "ledvector", {"ledmember": "Off"}) )
        elif self.state == "Off":
            TXQUE.put( ("led", "ledvector", {"ledmember": "On"}) )


    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        if not self.connected:
            # Not connected, nothing to do
            return
        # send instruction to toggle
        if self.state == "On":
            TXQUE.put( ("led", "ledvector", {"ledmember": "Off"}) )
        elif self.state == "Off":
            TXQUE.put( ("led", "ledvector", {"ledmember": "On"}) )


if __name__ == "__main__":

    # run the queclient in its own thread
    clientthread = threading.Thread(target=runqueclient, args=(TXQUE, RXQUE))
    # The args argument could also have hostname and port specified
    # if the LED server is running elsewhere
    clientthread.start()

    # run the terminal LEDControl
    app = LEDControl()
    app.run()
    # When the LEDControl app stops, transmit a None value to shut down the queclient
    TXQUE.put(None)
    # and wait for the clientthread to stop
    clientthread.join()
