# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "indipydriver>=3.0.2",
#     "indipyserver"
# ]
# ///


"""As bincount : sends a vector with four lights binary counting

and with added message as lights change, and a status alert when count goes to zero"""


import asyncio
import indipydriver as ipd

from indipyserver import IPyServer


class BinDriver(ipd.IPyDriver):
    """IPyDriver is subclassed here
       It has device 'bincounter' with a light 'binvector'
       with four members 'binvalue0' to 'binvalue3'
       which it populates with counting binary lights
       The vector is also set with state "Alert" when count is zero"""

    async def hardware(self):
        """Sends the counting binvector with four members
           showing red lights (Alert) for binary 1
           and green lights (Ok) for binary 0"""

        binvector = self['bincounter']['binvector']
        while not self.stop:
            # send a new lights count every second
            for n in range(16):
                await asyncio.sleep(1)
                binstring = f'{n:04b}'       # strings "0000" to "1111" generated as n increments
                binvector['binvalue0'] = "Alert" if binstring[3] == "1" else "Ok"
                binvector['binvalue1'] = "Alert" if binstring[2] == "1" else "Ok"
                binvector['binvalue2'] = "Alert" if binstring[1] == "1" else "Ok"
                binvector['binvalue3'] = "Alert" if binstring[0] == "1" else "Ok"
                state = "Ok" if n else "Alert"
                # include a message with the vector
                await binvector.send_setVector(message=f"Count is {n}", state=state)
                # send a device message
                await self['bincounter'].send_device_message(message=f"Device message: count is {n}")
                # send a system message
                await self.send_message(message=f"System message: count is {n}")



def make_driver():
    "Returns an instance of the driver"

    # create four LightMembers, binvalue0 to binvalue3
    members= []
    for m in range(4):
        members.append( ipd.LightMember( name = f"binvalue{m}",
                                         label = f"Light {m}" )  )


    # create a vector containing these members
    binvector = ipd.LightVector( name="binvector",
                                 label="Light Counter",
                                 group="Values",
                                 state="Ok",
                                 lightmembers=members )

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
    server = IPyServer(driver)
    print(f"Running {__file__}")
    asyncio.run(server.asyncrun())
