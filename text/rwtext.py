
import asyncio

import indipydriver as ipd


class RWDriver(ipd.IPyDriver):
    """IPyDriver is subclassed here
       It has one rw TextVector with three members
       Also sends text every two seconds"""

    async def rxevent(self, event):
        """On receiving data."""

        match event:

            case ipd.getProperties():
                await event.vector.send_defVector()

            case ipd.newTextVector(devicename='rwtext',
                                   vectorname='rwvector'):
                # get the received value(s)
                if 'rwvalue1' in event:
                    # set the new value into the vector
                    event.vector['rwvalue1'] = event['rwvalue1']
                if 'rwvalue2' in event:
                    # set the new value into the vector
                    event.vector['rwvalue2'] = event['rwvalue2']
                if 'rwvalue3' in event:
                    # set the new value into the vector
                    event.vector['rwvalue3'] = event['rwvalue3']
                # transmit the vector back to client to confirm received
                await event.vector.send_setVector()

    async def hardware(self):
        "Every two seconds, send text 'one', 'two', 'three'"

        vector = self['rwtext']['rwvector']
        while not self.stop:
            await asyncio.sleep(2)
            vector['rwvalue1'] = "one"
            vector['rwvalue2'] = "two"
            vector['rwvalue3'] = "three"
            await vector.send_setVector()




def make_driver():
    "Returns an instance of the driver"

    # create three members
    rwvalue1 = ipd.TextMember( name="rwvalue1",
                               label="Text 1",
                               membervalue="one" )
    rwvalue2 = ipd.TextMember( name="rwvalue2",
                               label = "Text 2",
                               membervalue="two" )
    rwvalue3 = ipd.TextMember( name="rwvalue3",
                               label = "Text 3",
                               membervalue="three" )
    rwvector = ipd.TextVector( name = 'rwvector',
                               label = "Text",
                               group = 'RW TEXT',
                               perm = "rw",
                               state = "Ok",
                               textmembers = [rwvalue1, rwvalue2, rwvalue3])


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
    asyncio.run(server.asyncrun())
