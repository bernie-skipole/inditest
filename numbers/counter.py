
import asyncio
import indipydriver as ipd


class CountDriver(ipd.IPyDriver):
    """IPyDriver is subclassed here
       It has device 'counter' with two vectors
       a ro vector with four incrementing members
       and a wo vector with ten members"""

    async def hardware(self):
        """Sends the counting vector with four members"""

        countvector = self['counter']['countvector']
        while not self.stop:
            # send new counts every second
            await asyncio.sleep(1)
            for m in range(4):
                currentvalue = countvector[f"count{m}"]
                currentfloat = self.indi_number_to_float(currentvalue)
                # set new value, in this case controlling the format by setting to a string
                countvector[f"count{m}"] = str( int(currentfloat) + 1 )
            await countvector.send_setVector()


    async def rxevent(self, event):
        """On receiving data."""

        match event:

            case ipd.getProperties():
                await event.vector.send_defVector()

            case ipd.newNumberVector(devicename='counter',
                                     vectorname='rxvector'):
                # get the received values
                for membername in event:
                    # set the new value into the vector
                    if membername in event.vector:
                        event.vector[membername] = event[membername]
                # transmit the vector back to client to confirm received
                await event.vector.send_setVector()


def make_driver():
    "Returns an instance of the driver"

    # create four NumberMembers, count0 to count3
    # with initial values 0,2,4,6
    countmembers= []
    for m in range(4):
        countmembers.append( ipd.NumberMember( name = f"count{m}",
                                               label = f"Counter {m}",
                                               format = "%d",
                                               membervalue=m*2 )  )

    # create a vector containing these members
    countvector = ipd.NumberVector( name="countvector",
                                    label="Counter",
                                    group="Values",
                                    state="Ok",
                                    perm="ro",
                                    numbermembers=countmembers )

    # create ten NumberMembers, rxmember0 to rxmember9
    # with initial values 0
    rxmembers= []
    for m in range(10):
        rxmembers.append( ipd.NumberMember( name = f"rxmember{m}",
                                            label = f"Input Value",
                                            format = "%4.2f" )  )

    # create a vector containing these members
    rxvector = ipd.NumberVector( name="rxvector",
                                 label="Values to send",
                                 group="Values",
                                 state="Ok",
                                 perm="rw",
                                 numbermembers=rxmembers )

    # create a device with these vectors
    counter = ipd.Device( devicename="counter",
                          properties=[countvector, rxvector] )

    # Create the Driver, containing this Device
    driver = CountDriver( counter )

    # and return the driver
    return driver


if __name__ == "__main__":

    # serve the driver on localhost, port 7624
    driver = make_driver()
    server = ipd.IPyServer(driver)
    asyncio.run(server.asyncrun())
