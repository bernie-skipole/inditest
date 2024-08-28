# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "indipyclient",
#     "indipydriver",
# ]
# ///


"TextVector with ten members, reading and writing"

import asyncio

import indipydriver as ipd


class RWDriver(ipd.IPyDriver):
    """IPyDriver is subclassed here
       It has one rw TextVector with ten members
       Also sends text every ten seconds"""

    async def rxevent(self, event):
        """On receiving data."""

        match event:

            case ipd.newTextVector(devicename='rwtext',
                                   vectorname='rwvector'):
                # get the received values
                for membername in event:
                    # set the new value into the vector
                    if membername in event.vector:
                        event.vector[membername] = event[membername]
                # transmit the vector back to client to confirm received
                await event.vector.send_setVector()

    async def hardware(self):
        "Every ten seconds, send new text"
        vector = self['rwtext']['rwvector']
        while not self.stop:
            await asyncio.sleep(10)
            for membername in vector:
                # get value number from last character of membername
                vector[membername] = f"Value {membername[-1]}"
            await vector.send_setVector()


def make_driver():
    "Returns an instance of the driver"

    # create ten members
    members = []

    for m in range(10):
        members.append(  ipd.TextMember( name=f"rwvalue{m}",
                                         label=f"Text Member {m}",
                                         membervalue=f"Value {m}" )
                      )

    rwvector = ipd.TextVector( name = 'rwvector',
                               label = "Text",
                               group = 'RW TEXT',
                               perm = "rw",
                               state = "Ok",
                               textmembers = members)

    # create a device with this vector
    rwtext = ipd.Device( devicename="rwtext",
                         properties=[rwvector] )

    # Create the Driver, containing this Device
    driver = RWDriver( rwtext )

    # and return the driver
    return driver


if __name__ == "__main__":

    driver = make_driver()
    server = ipd.IPyServer(driver)
    print(f"Running {__file__}")
    asyncio.run(server.asyncrun())
