# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "indipydriver>=3.0.4",
#     "indipyserver",
#     "minilineplot"
# ]
# ///

# When run on a Raspberry pi, reports its temperature every ten seconds
# and provides a four hour temperature chart

import subprocess, asyncio, re, time
from collections import deque

import minilineplot

import indipydriver as ipd

from indipyserver import IPyServer


def get_temp() -> float|None:
    "Return the temperature, return None on error"
    try:
        # cp is a CompletedProcess object
        cp = subprocess.run(["/usr/bin/vcgencmd", "measure_temp"], capture_output=True)
        # cp.stdout is a bytestring such as b"temp=50.0'C", So just extract the number part
        m = re.search(rb'-?\d*\.?\d+', cp.stdout)
        if m.group() is None:
            # nothing matching a number has been found
            return
        # convert to float
        floattemp = float(m.group())
    except Exception:
        return
    return floattemp


######## for testing on non-rpi
#import random
#def get_temp() -> float|None:
#    "Return the temperature, return None on error"
#    return 49.0 + random.randint(0, 20)/10.0  # float 49 + (0 to 2.0)


def get_chart(history, hours=4):
    "Given history deque, create a chart"
    # get maximums and minimums
    if len(history) < 2:
        return
    points = []
    # get latest timestamp
    lasttimestruct = time.localtime(history[-1][0])
    # seconds at last hour
    sechour = time.mktime((lasttimestruct.tm_year,
                           lasttimestruct.tm_mon,
                           lasttimestruct.tm_mday,
                           lasttimestruct.tm_hour,
                           0,
                           0,
                           lasttimestruct.tm_wday,
                           lasttimestruct.tm_yday,
                           lasttimestruct.tm_isdst))
    maxts = round(sechour + 3600.0)
    mints = round(maxts - (3600 * hours))   # hours back from maxts
    # create time strings
    xstrings = []
    for seconds in range(mints, maxts+3600, 3600):
        xstrings.append(str(time.localtime(seconds).tm_hour)) 
    for ts, tmp in history:
        if ts >= mints:
            points.append((ts, tmp))

    # make chart
    line = minilineplot.Line(values = points, color="red")
    axis = minilineplot.Axis(lines = [line],
                             xstrings = xstrings,
                             xmin = mints,
                             xmax = maxts,
                             title = "Temperature - Time (hours)",
                             description = f"Temperature to : {time.strftime('%a %d %b %Y, %I:%M%p', lasttimestruct)}"
                            )

    axis.auto_y()
    if axis.ymax < 60.0:
        axis.ymax = 60.0  # ymax is 60 or greater
    if axis.ymin > 40.0:
        axis.ymin = 40.0  # ymin is 40 or less

    return axis.to_bytes()


########################################
# Doing this somewhat differently by
# creating a number of background tasks
########################################


async def send_chart(device, history):
    "This is set as a background task"
    chartrequestvector = device["chartrequestvector"]
    chartvector = device['chartvector']
    while not device.stop:
        # every two seconds, check if a request for a chart has come in
        await asyncio.sleep(2)
        # If request vector is On, create and send a chart
        if chartrequestvector["chartrequest"] != "On":
            continue
        chartbytes = get_chart(history)
        if chartbytes is None:
            # no chart is available
            chartrequestvector["chartrequest"] = 'Off'
            # send the updated vector back to the client
            await chartrequestvector.send_setVector(message="Chart unavailable, please try again later", state="Ok")
            continue
        chartvector["chartmember"] = chartbytes
        # send the blob, BLOBs use the send_setVectorMembers method
        await chartvector.send_setVectorMembers(members=["chartmember"])
        # and turn the switch Off again
        chartrequestvector["chartrequest"] = 'Off'
        # send the updated switch vector back to the client
        await chartrequestvector.send_setVector(message=" ", state="Ok")


async def send_temperature(device):
    "This is set as a background task to transmit temperature every 10 seconds"
    temperaturevector = device['temperaturevector']
    while not device.stop:
        await asyncio.sleep(10)
        temperature = get_temp()
        # Send the temperature every 10 seconds
        if temperature is not None:
            temperaturevector['celsius'] = temperature
            temperaturevector['fahrenheit'] = 32 + temperature * 9.0/5.0
            # and transmit it to the client
            await temperaturevector.send_setVector()  # send change to temperaturevector with two members, celsius and farenheiht


async def store_temperature(device, history):
    "This is set as a background task, to store temperature in history every minute"
    while not device.stop:
        await asyncio.sleep(60)
        temperature = get_temp()
        # store the temperature in history
        if temperature is not None:
            history.append((time.time(), temperature))



class RPITempDriver(ipd.IPyDriver):

    """IPyDriver is subclassed here"""

    async def rxevent(self, event):
        """On receiving data, this is called, it sends any received events
           to the appropriate device"""

        if event.devicename in self:
           await self[event.devicename].devrxevent(event)

    async def hardware(self):
        """This coroutine starts when the driver starts, and starts any
           devices devhardware() tasks"""

        for device in self.values():
            self.add_background(device.devhardware())


class RPITempDevice(ipd.Device):

    """Device is subclassed here, to transmit the temperature to the client"""

    async def devrxevent(self, event):
        "On receiving data, this is called by the drivers rxevent method"

        # A switch event requesting a chart is handled

        if not isinstance(event, ipd.newSwitchVector):
            # Only a switch event is expected
            return

        if event.vectorname == "chartrequestvector" and 'chartrequest' in event:
            # a request has been received from the client
            switchvalue = event["chartrequest"]
            if switchvalue == "On":
                # So received a switch value of On, respond with the On value
                event.vector["chartrequest"] = 'On'
                # send the updated vector back to the client
                await event.vector.send_setVector(message="Generating Chart", state="Busy")
            else:
                # This should not normally be received, however, just in case it is
                # set 'Off' into the vector
                event.vector["chartrequest"] = 'Off'
                # send the updated vector back to the client
                await event.vector.send_setVector(message=" ", state="Ok")



    async def devhardware(self):
        """This coroutine is added as a background task by the driver's
           hardware method."""

        # deque object to hold last four hours
        history = self.devicedata['history']

        # start a background task, checking if a chart needs to be transmitted
        self.add_background(send_chart(self, history))

        # start another sending temperature updates
        self.add_background(send_temperature(self))

        # and another adding temperature values to history
        self.add_background(store_temperature(self, history))



            


 
def make_driver(devicename):
    "Returns an instance of the driver"

    # create a deque object to hold several hours of data
    # four hours is 240 minutes, five hours is 300
    history = deque(maxlen=300)

    current_temperature = get_temp()
    if current_temperature is None:
        current_temperature = 0.0

    # Make a NumberMember holding the temperature value in degrees Celsius
    celsius = ipd.NumberMember( name="celsius",
                                label= "Celsius",
                                format='%3.1f',
                                membervalue=current_temperature )
    # Make a NumberMember holding the temperature value in degrees Fahrenheit
    fahrenheit = ipd.NumberMember( name="fahrenheit",
                                   label="Fahrenheit",
                                   format='%3.1f',
                                   membervalue=32 + current_temperature * 9.0/5.0)
    # Make a NumberVector instance, containing the members.
    temperaturevector = ipd.NumberVector( name="temperaturevector",
                                          label="Temperature",
                                          group="Values",
                                          perm="ro",
                                          state="Ok",
                                          numbermembers=[celsius, fahrenheit] )


    # create switch member
    chartswitchmember = ipd.SwitchMember(name="chartrequest",
                                         label="Chart Request",
                                         membervalue='Off')
    # set this member into a vector
    chartswitchvector = ipd.SwitchVector(name="chartrequestvector",
                                 label="Generate Chart",
                                 group="Values",
                                 perm="rw",
                                 rule='AtMostOne',
                                 state="Ok",
                                 switchmembers=[chartswitchmember] )

    # creat a BLOB member
    chartmember = ipd.BLOBMember( name="chartmember",
                                  label="Temperature Chart",
                                  blobformat = ".svg" )
    chartvector = ipd.BLOBVector( name="chartvector",
                                  label="Four Hour temperature chart",
                                  group="Values",
                                  perm="ro",
                                  state="Ok",
                                  blobmembers=[chartmember] )

    # Make a Device with these vectors
    # and with the given devicename, the history deque is set into the Device
    rpi = RPITempDevice( devicename=devicename,
                         properties=[temperaturevector, chartswitchvector, chartvector],
                         history = history )

    # Create the Driver which will contain this Device,
    driver = RPITempDriver( rpi )

    # and return the driver
    return driver



if __name__ == "__main__":

    # create and serve the driver
    # the devicename has to be unique in a network of devices,
 
    # in this case we'll set the devicename as "RaspberryPi",

    # make a driver for the instrument
    rpidriver = make_driver("RaspberryPi")
    # and a server, which serves this driver
    server = IPyServer(rpidriver)
    print(f"Running {__file__} with indipydriver version {ipd.version}")
    asyncio.run(server.asyncrun())
