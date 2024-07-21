
import asyncio
import indipydriver as ipd


class BinDriver(ipd.IPyDriver):
    """IPyDriver is subclassed here
       It has device 'bincounter' with a light 'binvector'
       with four members 'binvalue0' to 'binvalue3'
       which it populates with counting binary lights"""

    async def hardware(self):
        """Sends the counting binvector with four members
           showing red lights (Alert) for binary 1
           and green lights (Ok) for binary 0"""

        binvector = self['bincounter']['binvector']
        while not self.stop:
            # send a new lights count every second
            for n in range(16):
                await asyncio.sleep(1)
                binstring = f'{n:04b}'       # strings "0000" to "1111"
                binvector['binvalue0'] = "Alert" if binstring[3] == "1" else "Ok"
                binvector['binvalue1'] = "Alert" if binstring[2] == "1" else "Ok"
                binvector['binvalue2'] = "Alert" if binstring[1] == "1" else "Ok"
                binvector['binvalue3'] = "Alert" if binstring[0] == "1" else "Ok"
                await binvector.send_setVector()


def make_driver():
    "Returns an instance of the driver"

    # create multiple LightMembers
    binvalue0 = ipd.LightMember( name = "binvalue0",
                                 label = "Light 0" )
    binvalue1 = ipd.LightMember( name = "binvalue1",
                                 label = "Light 1" )
    binvalue2 = ipd.LightMember( name = "binvalue2",
                                 label = "Light 2" )
    binvalue3 = ipd.LightMember( name = "binvalue3",
                                 label = "Light 3" )

    # create a vector containing these members
    binvector = ipd.LightVector( name="binvector",
                                 label="Light Counter",
                                 group="Values",
                                 state="Ok",
                                 lightmembers=[binvalue0, binvalue1, binvalue2, binvalue3] )

    # create a device with this vector
    bincounter = ipd.Device( devicename="bincounter",
                             properties=[binvector] )

    # Create the Driver, containing this Device
    driver = BinDriver( bincounter )

    # and return the driver
    return driver


if __name__ == "__main__":

    # serve the driver on localhost, port 7624
    driver = make_driver()
    server = ipd.IPyServer(driver)
    asyncio.run(server.asyncrun())
