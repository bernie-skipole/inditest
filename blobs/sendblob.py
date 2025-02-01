# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "indipydriver",
#     "indipyclient"
# ]
# ///



"""
Illustrates an instrument taking measurements, appending them to a BLOB
and at regular intervals, sending to a client as BLOB .csv files.

The indipyclient needs to have BLOBs enabled with a folder set where
the BLOB files will be saved
"""

import asyncio, io, collections, math

from datetime import datetime, timezone, timedelta

import indipydriver as ipd


class MakeBlobs:
    """This is a simulation containing variables only, normally it
       would take measurements from a sensor.

       measurements are added to a io.BytesIO object over a perod of
       'minutes', this object is then added to a que, and a new
       io.BytesIO object is created."""

    def __init__(self, devicename, minutes=1):
        """Set start up values"""

        self.devicename = devicename

        # set logtime for minutes in the future
        self.delta = timedelta(minutes=minutes)
        self.logtime = datetime.now(tz=timezone.utc) + self.delta

        self.blobfiles = collections.deque(maxlen=4)
        # self.blobfiles is a deque containing a number of io.BytesIO objects
        # with the number limited to 4
        # the older objects can be sent to the client,
        # or if not taken off, will be discarded.

        # measurements will be set in self.currentblob
        self.currentblob = io.BytesIO()

        # shutdown if self._stop is True
        self._stop = False

    def shutdown(self):
        self._stop = True


    def get_blobfile(self):
        "If a finished blobfile is available, return it, otherwise return None"
        try:
            oldest = self.blobfiles.popleft()
        except IndexError:
            return
        return oldest


    def appendlog(self, timestamp, value):
        """Appends a log to the currentblob, and every delta
           time create a new one
           """
        # If logtime is reached, create new currentblob
        if timestamp > self.logtime:
            self.blobfiles.append(self.currentblob)
            self.currentblob = io.BytesIO()
            # and set logtime to delta time in the future
            self.logtime = timestamp + self.delta

        # log time/value into the current blob in a nice csv format
        log = f"{timestamp.isoformat(sep='T')[:21]},{value:.2f}\n"
        self.currentblob.write(log.encode())


    async def poll_measurement(self):
        """This simulates an increasing/decreasing measurement,
           and adds logs to the io.BytesIO() object every two seconds."""

        t = 0
        while not self._stop:
            await asyncio.sleep(2)

            # simulate a varying measurement
            t += 0.5
            value = 20.0 + 10*math.sin(t)

            # set the value and timestamp into the blobfile
            timestamp = datetime.now(tz=timezone.utc)

            # append a log line
            self.appendlog(timestamp, value)


class _BLOBDriver(ipd.IPyDriver):

    """IPyDriver is subclassed here to create a driver for the instrument"""


    async def hardware(self):
        """This is a continuously running coroutine which is used
           to transmit the blob to connected clients."""

        blobcontrol = self.driverdata["blobcontrol"]
        # blobcontrol is a MakeBlobs object

        # start poll_measurement()
        poll_task = asyncio.create_task(blobcontrol.poll_measurement())

        devicename = blobcontrol.devicename

        blobvector = self[devicename]['blobvector']
        while not self._stop:
            # if a blobfile is available, send it as a BLOB
            blobfile = blobcontrol.get_blobfile()
            # this returns None if no blobfile is currently available
            if blobfile:
                blobvector["blobmember"] = blobfile
                # send the blob
                await blobvector.send_setVectorMembers(members=["blobmember"])

            # ensure this function does not block, by giving a sleep here
            # and wait a while before testing if another blob is available
            # to send
            await asyncio.sleep(10)

        # loop ended, stop creating blobs
        blobcontrol.shutdown()
        # wait for poll_task to end
        await poll_task


def make_driver(devicename, minutes):
    "Returns an instance of the driver"

    blobcontrol = MakeBlobs(devicename, minutes)

    # create blobvector, there is no member value to set at this point
    blobmember = ipd.BLOBMember( name="blobmember",
                                 label="Measurement logs",
                                 blobformat = ".csv" )
    blobvector = ipd.BLOBVector( name="blobvector",
                                 label="Logs",
                                 group="Measurement Files",
                                 perm="ro",
                                 state="Ok",
                                 blobmembers=[blobmember] )

    # create a device with this vector
    blobdevice = ipd.Device( devicename=devicename,
                             properties=[blobvector] )

    # Create the Driver, containing this device and
    # other objects needed to run the instrument
    driver = _BLOBDriver( blobdevice,                # the device
                          blobcontrol=blobcontrol )  # MakeBlobs to place in driverdata

    # and return the driver
    return driver



if __name__ == "__main__":
    driver = make_driver("blobmaker", minutes=2) # create BLOBs every two minutes
    server = ipd.IPyServer(driver)
    print(f"Running {__file__}")
    asyncio.run( server.asyncrun() )
