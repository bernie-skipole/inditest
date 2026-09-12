# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "indipydriver>=3.0.2",
#     "indipyserver"
# ]
# ///


"""A measurement and a target device
The target gets an alert as the measurement moves away from it
Logger level is set to debug, and prints debug logs"""


import asyncio
import logging, sys

import indipydriver as ipd
from indipyserver import IPyServer

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)


class MeasurementDriver(ipd.IPyDriver):

    async def rxevent(self, event):
        "On receiving data from the client, this is called"

        if event.devicename != 'Target':
            # No other device data is expected, ignore anything
            # without the correct devicename
            return

        if isinstance(event, ipd.newNumberVector):
            if event.vectorname == "tvector" and 'tmember' in event:
                # a new target value has been received from the client
                # set this new value into the vector and
                # send the updated vector back to the client
                event.vector['tmember'] = event['tmember']
                await event.vector.send_setVector(state="Ok")



    async def hardware(self):
        """This coroutine starts when the driver starts
           It simulates an increasing then decreasing measurement"""
        measurement = 3.0
        delta = 1.0

        measurementvector = self['Measurement']['mvector']
        targetvector = self['Target']['tvector']

        while not self.stop:
            await asyncio.sleep(2)

            # simulate a rising and falling measurement
            if measurement >= 10.0:
                delta = -1.0
            elif measurement <= -10.0:
                delta = 1.0
            measurement += delta

            # send this measurement to the client
            measurementvector["mmember"] = str(measurement)
            await measurementvector.send_setVector()

            targetval = ipd.getfloat(targetvector["tmember"])

            if measurement > targetval + 2.0:
                await targetvector.send_setVector(state="Alert", message="Too High", allvalues=False)
            elif measurement < targetval - 2.0:
                await targetvector.send_setVector(state="Alert", message="Too Low", allvalues=False)
            else:
                await targetvector.send_setVector(state="Ok", message="Just right", allvalues=False)

            # These alerts should only be sent as the measurement crosses thresholds, and
            # should not be continuously repeated.
            # The target value should not be included, as it has not changed.
            # The debug trace should show this as warnings
            # that values are not being sent


 

def make_driver():
    "Returns an instance of the driver"

    # NOTE : two vectors could be created and added to a single device,
    # however this illustration creates two separate devices, just to
    # show that can be done.

    # Make a NumberMember holding the measurement
    mmember = ipd.NumberMember( name="mmember",
                                label= "Measurement",
                                format='%3.1f',
                                membervalue=3.0 )

    # Make a ro NumberVector instance, containing mmember
    mvector = ipd.NumberVector( name="mvector",
                                  label="Measurement",
                                  group="Values",
                                  perm="ro",
                                  state="Ok",
                                  numbermembers=[mmember] )
    # Make a Device
    Measurement = ipd.Device( devicename="Measurement",
                              properties=[mvector] )


    # Make a NumberMember holding the target
    tmember = ipd.NumberMember( name="tmember",
                                label= "Target",
                                format='%3.1f',
                                membervalue=3.0 )

    # Make a wo NumberVector instance, containing tmember
    tvector = ipd.NumberVector( name="tvector",
                                  label="Target",
                                  group="Values",
                                  perm="wo",
                                  state="Ok",
                                  numbermembers=[tmember] )
    # give this an initial message
    tvector.message="Starting value is just right"

    # Make a Device
    Target = ipd.Device( devicename="Target",
                             properties=[tvector] )

    # Create the Driver which will contain these Devices,
    driver = MeasurementDriver( Measurement, Target )

    # and return the driver
    return driver



if __name__ == "__main__":

    # serve the driver on localhost, port 7624
    driver = make_driver()
    # enable debugging
    driver.debug_enable = True
    server = IPyServer(driver)
    print(f"Running {__file__}")
    asyncio.run(server.asyncrun())
