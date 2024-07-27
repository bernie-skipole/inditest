
import asyncio

import indipydriver as ipd


class Driver(ipd.IPyDriver):
    """IPyDriver is subclassed here"""

    async def rxevent(self, event):
        """On receiving data."""

        match event:

            case ipd.getProperties():
                await event.vector.send_defVector()

            case ipd.newSwitchVector(devicename='switch',
                                     vectorname='vector'):
                # get the received values and set them into the vector
                for membername, membervalue in event.items():
                    event.vector[membername] = membervalue
                # transmit the vector back to client to confirm received
                await event.vector.send_setVector()


def make_driver():
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
    switch = ipd.Device( devicename="switch",
                         properties=[vector] )

    # Create the Driver, containing this Device
    driver = Driver( switch )

    # and return the driver
    return driver


if __name__ == "__main__":

    driver = make_driver()
    server = ipd.IPyServer(driver)
    asyncio.run(server.asyncrun())
