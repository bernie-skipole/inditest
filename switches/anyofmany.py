# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "indipydriver>=3.0.2",
#     "indipyserver"
# ]
# ///


"SwitchVector with ten members which can be set by the client"

import asyncio

import indipydriver as ipd

from indipyserver import IPyServer


class Driver(ipd.IPyDriver):
    """IPyDriver is subclassed here"""

    async def rxevent(self, event):
        """On receiving data."""

        devicename = self.driverdata['devicename']

        match event:

            case ipd.newSwitchVector(devicename=devicename,
                                     vectorname='vector'):
                # get the received values and set them into the vector
                for membername, membervalue in event.items():
                    event.vector[membername] = membervalue
                # transmit the vector back to client to confirm received
                await event.vector.send_setVector()


def make_driver(devicename):
    "Returns an instance of the driver"

    # create ten members
    members = []
    for s in range(10):
        member = ipd.SwitchMember( name=f"value{s}",
                                   label=f"Switch {s}",
                                   membervalue="Off" )
        members.append(member)


    vector = ipd.SwitchVector( name = 'vector',
                               label = "Switch",
                               group = 'Switches',
                               perm = "wo",
                               state = "Ok",
                               rule = "AnyOfMany",
                               switchmembers = members)


    # create a device with this vector
    switch = ipd.Device( devicename=devicename,
                         properties=[vector] )

    # Create the Driver, containing this Device
    driver = Driver( switch, devicename=devicename)

    # and return the driver
    return driver


if __name__ == "__main__":

    driver = make_driver("switch")
    server = IPyServer(driver)
    print(f"Running {__file__}")
    asyncio.run(server.asyncrun())
