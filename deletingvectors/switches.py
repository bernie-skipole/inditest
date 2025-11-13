# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "indipydriver>=3.0.2",
#     "indipyserver"
# ]
# ///


"""Two switch vectors, the RO vector has switches counting
   and after 5 seconds it is deleted, after another 5 seconds it is re-enabled.
   Clients should see it dissapearing and reappearing."""


import asyncio

import indipydriver as ipd

from indipyserver import IPyServer


class Driver(ipd.IPyDriver):
    """IPyDriver is subclassed here"""

    async def rxevent(self, event):
        """On receiving data."""

        devicename = self.driverdata['devicename']

        match event:

            case ipd.newSwitchVector(devicename=devicename):
                # get the received values and set them into the vector
                for membername, membervalue in event.items():
                    event.vector[membername] = membervalue
                # transmit the vector back to client to confirm received
                await event.vector.send_setVector()


    async def hardware(self):
        """Send  new ro switch values every second"""

        devicename = self.driverdata['devicename']

        rovector = self[devicename]['ROvector']
        while not self.stop:
            # send a new switch values every second
            for s in range(5):
                await asyncio.sleep(1)
                if rovector[f"ROMmember{s}"] == "On":
                    rovector[f"ROMmember{s}"] = "Off"
                else:
                    rovector[f"ROMmember{s}"] = "On"
                await rovector.send_setVector()
            # After count, delete the vector
            await rovector.send_delProperty(message='vector deleted')
            await asyncio.sleep(5)
            # and after another five seconds, re enable it
            rovector.enable = True
            await rovector.send_defVector(message='Reenabled')


def make_driver(devicename):
    "Returns an instance of the driver"

    # create five members with rule OneOfMany

    oom_members = []
    for s in range(5):
        # One member must be On
        if s:
            memval = "Off"
        else:
            memval = "On"

        member = ipd.SwitchMember( name=f"OOMmember{s}",
                                   label=f"Switch {s}",
                                   membervalue=memval )
        oom_members.append(member)


    oom_vector = ipd.SwitchVector( name = 'OOMvector',
                                   label = "OneOfMany WO Vector",
                                   group = 'OneGroup',
                                   perm = "wo",
                                   state = "Ok",
                                   rule = "OneOfMany",
                                   switchmembers = oom_members)


    # create Read Only vector that the client cannot change
    # this will be continuously altered by the driver hardware method
    # to simulate an instrument having switches locally controlled

    ro_members = []
    for s in range(5):
        # Set first member On
        if s:
            memval = "Off"
        else:
            memval = "On"

        member = ipd.SwitchMember( name=f"ROMmember{s}",
                                   label=f"Switch {s}",
                                   membervalue=memval )
        ro_members.append(member)

    ro_vector = ipd.SwitchVector( name = 'ROvector',
                                   label = "AnyOfMany RO Vector",
                                   group = 'OneGroup',
                                   perm = "ro",
                                   state = "Ok",
                                   rule = "AnyOfMany",
                                   switchmembers = ro_members)


    # create a device with these vectors
    switchingdevice = ipd.Device( devicename=devicename,
                         properties=[oom_vector, ro_vector] )

    # Create the Driver, containing this Device
    driver = Driver( switchingdevice, devicename=devicename)

    # and return the driver
    return driver


if __name__ == "__main__":

    driver = make_driver("switches")
    server = IPyServer(driver)
    print(f"Running {__file__}")
    asyncio.run(server.asyncrun())
