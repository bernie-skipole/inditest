# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "indipyclient",
#     "textual"
# ]
# ///



import asyncio, queue, threading, logging

from typing import Iterable

from textual.app import App, ComposeResult, SystemCommand
from textual.widgets import Footer, Static, Button
from textual.reactive import reactive
from textual.screen import Screen
from textual.containers import Center
from textual.message import Message

import indipyclient as ipc

# Turn off logging so screen not messed up with messages
logger = logging.getLogger()
logger.addHandler(logging.NullHandler())


class IClient(ipc.IPyClient):

    # Create the IPyClient object that gets the LED status

    async def rxevent(self, event):
        app = self.clientdata['app']

        if self.connected:
            # the connection status
            app.post_message(app.ConnectionStatus(True))
        else:
            app.post_message(app.ConnectionStatus(False))

        if event.devicename == "led" and event.vectorname == "ledvector" and ("ledmember" in event):
            app.post_message(app.LedStatus(event["ledmember"]))




class IsConnected(Static):
    "A widget to display connected status."

    connected = reactive(False)

    def watch_connected(self, connected:bool) -> None:
        if connected:
            self.update("Connected")
        else:
            self.update("Not Connected")


class LedValue(Static):
    "A widget to display LED state"

    state = reactive("Unknown")

    def watch_state(self, state:str) -> None:
        self.update(state)



class LedControl(App):
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

    class ConnectionStatus(Message):
        """Connection status."""

        def __init__(self, status: bool) -> None:
            self.status = status
            super().__init__()


    class LedStatus(Message):
        """LED status."""

        def __init__(self, status: bool) -> None:
            self.status = status
            super().__init__()


    def __init__(self, host="localhost", port=7624):
        self.indihost = host
        self.indiport = port
        self.indiclient = IClient(indihost=host, indiport=port, app=self)
        super().__init__()


    def on_mount(self) -> None:
        """Start the worker which runs self.indiclient.asyncrun()"""
        self.run_worker(self.indiclient.asyncrun(), exclusive=True)


    def on_led_control_connection_status(self, message: ConnectionStatus) -> None:
        self.connected = message.status
        if self.connected:
            self.query_one(Button).disabled = False
            return
        self.state = "Unknown"
        self.query_one(Button).disabled = True


    def on_led_control_led_status(self, message: LedStatus) -> None:
        self.state = message.status


    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Static("LED Control", id="title")
        with Center():
            yield IsConnected("Not Connected", classes="widg").data_bind(LedControl.connected)
        with Center():
            yield LedValue("Unknown", classes="widg").data_bind(LedControl.state)
        with Center():
            yield Button("Toggle LED")
        yield Footer()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
            )

    async def action_quit(self) -> None:
        """An action to quit the program."""
        self.indiclient.shutdown()
        # and wait for it to shutdown
        await self.indiclient.stopped.wait()
        self.exit(0)

    async def action_toggle_LED(self) -> None:
        """An action to toggle the LED."""
        if not self.indiclient.connected:
            # Not connected, nothing to do
            return
        if self.state == "On":
            await self.indiclient.send_newVector("led", "ledvector", members={"ledmember": "Off"})
        elif self.state == "Off":
            await self.indiclient.send_newVector("led", "ledvector", members={"ledmember": "On"})

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed. In this case there
           is only one button, so do not have to be more specific.
           This calls action_toggle_LED, so is the same action as t being pressed"""
        await self.action_toggle_LED()
        return


if __name__ == "__main__":

    # run the terminal LedControl app
    app = LedControl(host="localhost", port=7624)
    app.run()
