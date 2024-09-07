# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "indipydriver",
# ]
# ///

# uncomment to enable logging
# import logging
# logger = logging.getLogger()
# fh = logging.FileHandler("logfile.log")
# logger.addHandler(fh)
# logger.setLevel(logging.DEBUG)



import asyncio

from indipydriver import (IPyDriver, Device,
                          NumberVector, NumberMember,
                          IPyServer
                         )

# Other vectors, members and events are available,
# this example only imports those used.

class ThermalControl:
    """This is a simulation containing variables only, normally it
       would control a real heater, and take temperature measurements
       from a sensor."""

    def __init__(self):
        """Set start up values"""
        self.temperature = 20
        self.target = 15
        self.heater = "Off"
        self.stop = False

    def shutdown(self):
        self.stop = True

    async def run_thermostat(self):
        """This simulates temperature increasing/decreasing, and turns
           on/off a heater if moving too far from the target."""
        while not self.stop:
            await asyncio.sleep(2)
            if self.heater == "On":
                # increasing temperature if the heater is on
                self.temperature += 0.1
            else:
                # decreasing temperature if the heater is off
                self.temperature -= 0.1

            if self.temperature > self.target+0.5:
                # too hot
                self.heater = "Off"

            if self.temperature < self.target-0.5:
                # too cold
                self.heater = "On"


class ThermoDriver(IPyDriver):

    """IPyDriver is subclassed here, with a method
       to transmit the temperature to the client"""


    async def hardware(self):
        """This is a continuously running coroutine which is used
           to transmit the temperature to connected clients."""

        # get the object controlling the instrument, which is available
        # in the named arguments dictionary 'self.driverdata'.
        thermalcontrol = self.driverdata["thermalcontrol"]

        vector = self['Thermostat']['temperaturevector']
        while not self.stop:
            await asyncio.sleep(10)
            # Send the temperature every 10 seconds
            vector['temperature'] = thermalcontrol.temperature
            # and transmit it to the client
            await vector.send_setVector()


def make_driver(thermalcontrol):
    "Returns an instance of the driver"

    # Make a NumberMember holding the temperature value
    temperaturemember = NumberMember( name="temperature",
                                      format='%3.1f', min=-50, max=99,
                                      membervalue=thermalcontrol.temperature )
    # Make a NumberVector instance, containing the member.
    temperaturevector = NumberVector( name="temperaturevector",
                                      label="Temperature",
                                      group="Values",
                                      perm="ro",
                                      state="Ok",
                                      numbermembers=[temperaturemember] )
    # Make a Device with temperaturevector as its only property
    thermostat = Device( devicename="Thermostat",
                         properties=[temperaturevector] )

    # Create the Driver which will contain this Device,
    #  and the instrument controlling object
    driver = ThermoDriver( thermostat,
                           thermalcontrol=thermalcontrol )

    # and return the driver
    return driver


async def main(thermalcontrol, server):
    "Run the instrument and the server async tasks"
    await asyncio.gather(thermalcontrol.run_thermostat(),
                         server.asyncrun() )


if __name__ == "__main__":

    # Make an instance of the object controlling the instrument
    thermalcontrol = ThermalControl()
    # make a driver for the instrument
    thermodriver = make_driver(thermalcontrol)
    # and a server, which serves this driver
    server = IPyServer(thermodriver)
    # and run them together
    print(f"Running {__file__}")
    asyncio.run( main(thermalcontrol, server) )
