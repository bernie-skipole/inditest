# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "indipydriver",
# ]
# ///


## ignore these, used for development
#import sys
#sys.path.insert(0, "/home/bernard/git/indipydriver")
#sys.path.insert(0, "/home/bernard/git/indipyclient")


import asyncio, time

import sys
sys.path.insert(0, "/home/bernie/git/indipydriver")


from indipydriver import (IPyServer, IPyDriver, Device,
                          TextVector, TextMember,
                          setNumberVector
                         )

# Other vectors, members and events are available, this example only imports those used.

class WindowControl:
    "This is a simulation containing variables only"

    def __init__(self):
        "Set initial value of window"
        self.window = "Open"
        # window should be "Open" or 'Closed'


    def set_window(self, temperature):
        """Gets new temperature, sets window accordingly"""
        if temperature > 21:
            self.window = "Open"
        if temperature < 18:
            self.window = "Closed"


class WindowDriver(IPyDriver):

    """IPyDriver is subclassed here"""

    async def hardware(self):
        "Update client with window status"

        windowcontrol = self.driverdata["windowcontrol"]
        statusvector = self['Window']['windowstatus']
        while not self.stop:
            # every ten seconds send an update on window position
            await asyncio.sleep(10)
            # get the current window status
            statusvector['status'] = windowcontrol.window
            # and transmit it to the client
            await statusvector.send_setVector(allvalues=False)
            # allvalues=False means that not all values will be sent, only
            # values that have changed, so this avoids unnecessary data
            # being transmitted


    async def snoopevent(self, event):
        """Handle receipt of an event from the Thermostat."""
        windowcontrol = self.driverdata["windowcontrol"]
        match event:
            case setNumberVector(devicename="Thermostat",
                                 vectorname="temperaturevector") if "temperature" in event:
                # A setNumberVector has been sent from the thermostat to the client
                # and this driver has received a copy, and so can read the temperature
                try:
                    temperature = self.indi_number_to_float(event["temperature"])
                except TypeError:
                    # ignore an incoming invalid number
                    return
                # this updates windowcontrol which opens or closes the widow
                windowcontrol.set_window(temperature)


def make_driver(windowcontrol):
    "Creates the driver"

    status = TextMember( name="status",
                         label="Window position",
                         membervalue=windowcontrol.window )
    windowstatus = TextVector( name="windowstatus",
                               label="Window Status",
                               group="Values",
                               perm="ro",
                               state="Ok",
                               textmembers=[status] )

    # make a Device with this vector
    window = Device( devicename="Window",
                     properties=[windowstatus] )

    # Make the WindowDriver containing this Device
    # and the window controlling object
    windowdriver = WindowDriver( window,
                                 windowcontrol=windowcontrol )

    # This driver wants copies of data sent from the thermostat
    windowdriver.snoop(devicename="Thermostat",
                       vectorname="temperaturevector",
                       timeout=30)

    # and return the driver
    return windowdriver


async def main(thermalcontrol, server):
    "Run the instrument and the server async tasks"
    await asyncio.gather(thermalcontrol.run_thermostat(),
                         server.asyncrun() )


# Assuming the thermostat example is example2.py, these would be run with

if __name__ == "__main__":

    import example2

    # Make the thermalcontrol object
    thermalcontrol = example2.ThermalControl()
    # make a driver
    thermodriver = example2.make_driver(thermalcontrol)

    # make the windowcontrol object
    windowcontrol = WindowControl()
    windowdriver = make_driver(windowcontrol)

    server = IPyServer(thermodriver, windowdriver)
    print(f"Running {__file__}")
    asyncio.run( main(thermalcontrol, server) )
