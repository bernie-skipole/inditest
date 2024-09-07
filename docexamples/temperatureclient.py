# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "indipyclient",
# ]
# ///


"""Connects to the driver of example1 and prints
   the temperature as it is received"""

import asyncio
import indipyclient as ipc


class MyClient(ipc.IPyClient):

    async def rxevent(self, event):
        "Prints the temperature as it is received"
        if isinstance(event, ipc.setNumberVector):
            if event.devicename != "Thermostat":
                return
            if event.vectorname != "temperaturevector":
                return
            # use dictionary get method which returns None
            # if this member name is not present in the event
            value = event.get("temperature")
            if value:
                print(value)

myclient = MyClient()

asyncio.run(myclient.asyncrun())
