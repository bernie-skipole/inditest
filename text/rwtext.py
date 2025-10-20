# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "indipydriver>=3.0.2",
#     "indipyserver"
# ]
# ///


"""TextVector with ten members, reading and writing
   Together with another vector controlling a longer 15 second task"""

import asyncio

import indipydriver as ipd

from indipyserver import IPyServer


async def delay_instrument(vector, value):
    """When the driver receives a vector and value for this instrument, this is called
       as a background task, simulating an instrument taking some time to process the data.
       When done, this instrument updates the vector, and sends it back to the client"""
    # simulate instrument processing time
    await asyncio.sleep(15)
    # having processed, set the vector value, and transmit this new value
    vector['tovalue'] = value
    await vector.send_setVector(message="Delayed value sent back")



class RWDriver(ipd.IPyDriver):
    """IPyDriver is subclassed here
       It has a rw TextVector with ten members
       with new text sent every ten seconds
       and a single vector which on receiving new data, only responds
       after 15 seconds, to test timeout functions"""

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

            case ipd.newTextVector(devicename='rwtext',
                                   vectorname='timeoutvector'):
                # get the received value
                value = event.get('tovalue')
                if value is None:
                    # member name not recognised
                    return

                # send this event.vector and value to an instrument which processes the
                # value, then sends an acknowledgement back to the client
                # In this example, this is simulated by the 'delay_instrument' function

                # create a job to run in the background
                self.add_background(delay_instrument(event.vector, value))

                # As this task is now running in the background, this rxevent method
                # can now end, and will not block further functionality of the driver.


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

    # create a rw vector with ten members
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


    # Create a vector with one member that has a 15 second time delay
    # and a suggested timeout of 8 seconds. This should cause a client
    # to show Busy after eight seconds, and alert after ten.

    timeoutmember = ipd.TextMember( name="tovalue",
                                    label="Timeout Member",
                                    membervalue="Starting value" )

    timeoutvector = ipd.TextVector( name = 'timeoutvector',
                                    label = "Timeout Vector",
                                    group = 'RW TEXT',
                                    perm = "rw",
                                    state = "Ok",
                                    textmembers = [timeoutmember])

    # set a vector timeout of eight seconds
    timeoutvector.timeout = 8

    # create a device with these vectors
    rwtext = ipd.Device( devicename="rwtext",
                         properties=[rwvector, timeoutvector] )

    # Create the Driver, containing this Device

    # This driver operates an instrument by running background tasks
    # store these tasks in the driver to stop them being garbage collected

    driver = RWDriver( rwtext )

    # and return the driver
    return driver


if __name__ == "__main__":

    driver = make_driver()
    server = IPyServer(driver)
    print(f"Running {__file__}")
    asyncio.run(server.asyncrun())
