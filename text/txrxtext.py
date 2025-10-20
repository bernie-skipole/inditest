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


class TxRxDriver(ipd.IPyDriver):
    """IPyDriver is subclassed here
       It receives text in rxvector
       and has another txvector with five members
       which it populates by adding * to front and end
       of the received value. It sends this new vector"""

    async def rxevent(self, event):
        """On receiving data, this is called, manipulates and sends
           the received value in a vector with multiple members."""

        match event:

            case ipd.newTextVector(devicename='txrxtext',
                                   vectorname='rxvector') if 'rxvalue' in event:
                # get the received value
                newvalue = event['rxvalue']
                # and set the new value into the vector, and
                # transmit the vector back to client to confirm received
                event.vector['rxvalue'] = newvalue
                await event.vector.send_setVector()

                # then transmit changed text in another vector
                txvector = self['txrxtext']['txvector']
                # for each member, set text with incrementing number of *'s
                for i in range(1,6):
                    txvector[f'txvalue{i}'] = "*"*i + newvalue + "*"*i
                await txvector.send_setVector()

def make_driver():
    "Returns an instance of the driver"

    # create a member and vector for received text
    rxvalue = ipd.TextMember( name="rxvalue",
                              label = "Text to send" )
    rxvector = ipd.TextVector( name = 'rxvector',
                               label = "Text to send",
                               group = 'Sender',
                               perm = "wo",
                               state = "Ok",
                               textmembers = [rxvalue])


    # create a vector with multiple text members
    txvalue1 = ipd.TextMember( name="txvalue1",
                               label = "Member 1" )
    txvalue2 = ipd.TextMember( name="txvalue2",
                               label = "Member 2" )
    txvalue3 = ipd.TextMember( name="txvalue3",
                               label = "Member 3" )
    txvalue4 = ipd.TextMember( name="txvalue4",
                               label = "Member 4" )
    txvalue5 = ipd.TextMember( name="txvalue5",
                               label = "Member 5" )
    txvector = ipd.TextVector( name="txvector",
                               label="From Driver",
                               group="Values",
                               perm="ro",
                               state="Ok",
                               textmembers=[txvalue1, txvalue2, txvalue3, txvalue4, txvalue5] )


    # create a device with the two vectors
    txrxtext = ipd.Device( devicename="txrxtext",
                           properties=[rxvector, txvector] )

    # Create the Driver, containing this Device
    driver = TxRxDriver( txrxtext )

    # and return the driver
    return driver


if __name__ == "__main__":

    driver = make_driver()
    server = IPyServer(driver)
    print(f"Running {__file__}")
    asyncio.run(server.asyncrun())
