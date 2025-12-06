# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "indipydriver>=3.0.4",
#     "indipyserver"
# ]
# ///

# When run on a Raspberry pi, reports its temperature every ten seconds

import subprocess, asyncio, re
import indipydriver as ipd

from indipyserver import IPyServer


def get_temp() -> float|None:
    "Return the temperature, return None on error"
    try:
        # cp is a CompletedProcess object
        cp = subprocess.run(["/usr/bin/vcgencmd", "measure_temp"], capture_output=True)
        # cp.stdout is a bytestring such as b"temp=50.0'C", So just extract the number part
        m = re.search(rb'-?\d*\.?\d+', cp.stdout)
        if m.group() is None:
            # nothing matching a number has been found
            return
        # convert to float
        floattemp = float(m.group())
    except Exception:
        return
    return floattemp



class RPITempDriver(ipd.IPyDriver):

    """IPyDriver is subclassed here"""

    async def hardware(self):
        """This coroutine starts when the driver starts, and starts any
           devices devhardware() tasks"""

        for device in self.values():
            self.add_background(device.devhardware())


class RPITempDevice(ipd.Device):

    """Device is subclassed here, to transmit the temperature to the client"""

    async def devhardware(self):
        """This coroutine is added as a background task by the driver's
           hardware method."""

        vector = self['temperaturevector']
        while not self.stop:
            await asyncio.sleep(10)
            temperature = get_temp()
            # Send the temperature every 10 seconds
            if temperature is not None:
                vector['celsius'] = temperature
                vector['fahrenheit'] = 32 + temperature * 9.0/5.0
                # and transmit it to the client
                await vector.send_setVector()  # change to vector with two members, centgrade and farenheiht


 
def make_driver(devicename):
    "Returns an instance of the driver"

    current_temperature = get_temp()
    if current_temperature is None:
        current_temperature = 0.0

    # Make a NumberMember holding the temperature value in degrees Celsius
    celsius = ipd.NumberMember( name="celsius",
                                label= "Celsius",
                                format='%3.1f', min=-50, max=99,
                                membervalue=current_temperature )
    # Make a NumberMember holding the temperature value in degrees Fahrenheit
    fahrenheit = ipd.NumberMember( name="fahrenheit",
                                   label="Fahrenheit",
                                   format='%3.1f', min=-50, max=99,
                                   membervalue=32 + current_temperature * 9.0/5.0)
    # Make a NumberVector instance, containing the members.
    temperaturevector = ipd.NumberVector( name="temperaturevector",
                                          label="Temperature",
                                          group="Values",
                                          perm="ro",
                                          state="Ok",
                                          numbermembers=[celsius, fahrenheit] )
    # Make a Device with temperaturevector as its only property
    # and with the given devicename
    rpi = RPITempDevice( devicename=devicename,
                             properties=[temperaturevector] )

    # Create the Driver which will contain this Device,
    # and the instrument controlling object
    driver = RPITempDriver( rpi )

    # and return the driver
    return driver



if __name__ == "__main__":

    # create and serve the driver
    # the devicename has to be unique in a network of devices,
 
    # in this case we'll set the devicename as "RaspberryPi",

    # make a driver for the instrument
    rpidriver = make_driver("RaspberryPi")
    # and a server, which serves this driver
    server = IPyServer(rpidriver)
    print(f"Running {__file__} with indipydriver version {ipd.version}")
    asyncio.run(server.asyncrun())
