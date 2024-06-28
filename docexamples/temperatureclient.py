
# Connects to the driver of example1 and prints
# the temperature as it is received

import asyncio
import indipyclient as ipc

# uncomment to enable logging
#
# import logging
# logger = logging.getLogger()
# fh = logging.FileHandler("logfile.log")
# logger.addHandler(fh)
# logger.setLevel(logging.DEBUG)

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
