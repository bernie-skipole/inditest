# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "indipydriver>=3.0.2",
#     "indipyserver"
# ]
# ///


import asyncio

import indipydriver as ipd

from indipyserver import IPyServer

class CounterDriver(ipd.IPyDriver):
    """IPyDriver is subclassed here
       It prints and transmits an incrementing count to the client
       and receives and prints a number from the client"""

    async def rxevent(self, event):
        """On receiving data, this is called, and prints the received value."""

        match event:

            case ipd.newNumberVector(devicename='Counter',
                                 vectorname='rxvector') if 'rxvalue' in event:
                # Print the received value
                newvalue = event['rxvalue']
                print(f"                       rx:{newvalue}")
                # and set the new value into the vector,
                # then transmit the vector back to client.
                event.vector['rxvalue'] = newvalue
                await event.vector.send_setVector()


    async def hardware(self):
        """This is a continuously running coroutine which is used
           to transmit an incrementing count to connected clients."""

        # counterval is a value to be incremented and sent
        counterval = 0
        vector = self['Counter']['txcount']
        # This vector has member name 'txvalue'
        while not self.stop:
            await asyncio.sleep(2)
            # Update, print and send the countval every 2 seconds
            counterval += 1
            print(f"tx:{counterval}")
            vector['txvalue'] = counterval
            # and transmit it to the client
            await vector.send_setVector()


def make_driver():
    "Returns an instance of the driver"

    # create a vector with one number 'txvalue' as its member
    txvalue = ipd.NumberMember( name="txvalue",
                                format='%3.1f', min=0, max=0,
                                membervalue=0 )
    txcount = ipd.NumberVector( name="txcount",
                                label="Counter",
                                group="Values",
                                perm="ro",
                                state="Ok",
                                numbermembers=[txvalue] )

    # create a vector with one number 'rxvalue' as its member
    rxvalue = ipd.NumberMember( name="rxvalue",
                                format='%3.1f', min=0, max=0,
                                membervalue=0 )
    rxvector = ipd.NumberVector( name="rxvector",
                                 label="Send Value",
                                 group="Values",
                                 perm="rw",
                                 state="Ok",
                                 numbermembers=[rxvalue] )

    # note the rxvector has permission rw so the client can set it

    # create a device with the two vectors
    counter = ipd.Device( devicename="Counter",
                          properties=[txcount, rxvector] )

    # Create the Driver, containing this Device
    driver = CounterDriver( counter )

    # and return the driver
    return driver


if __name__ == "__main__":

    driver = make_driver()
    server = IPyServer(driver)
    print(f"Running {__file__}")
    asyncio.run(server.asyncrun())
