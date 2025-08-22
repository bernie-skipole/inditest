# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "indipyclient",
# ]
# ///


"""Connects to the driver of example1 and prints
   the temperature every two seconds, regardless of the frequency of
   incoming data.

   There are other ways to do this, but this illustrates using create_clientevent"""

import asyncio
import indipyclient as ipc


class MyClient(ipc.IPyClient):

    async def rxevent(self, event):
        "Prints the temperature when a temperaturetwosec event is received"
        if event.eventtype == "temperaturetwosec":
            try:
                # only interested in the value of membername "temperature"
                value = event["temperature"]
            except Exception:
                # return if the member does not exist
                return
            print(value)

        # tests for other events could go here


    async def hardware(self):
        "create an event every two seconds"
        while True:
            await asyncio.sleep(2)
            try:
                vector = self["Thermostat"]["temperaturevector"]
                await vector.create_clientevent(eventtype="temperaturetwosec")
                # this creates an event, with eventtype set to the string temperaturetwosec
                # and this event will be a mapping of membername:membervalue for this vector
            except Exception as e:
                # skip if the required vector has not been learnt yet
                pass


myclient = MyClient()

asyncio.run(myclient.asyncrun())
