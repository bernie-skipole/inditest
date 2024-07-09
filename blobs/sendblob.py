"""
Illustrates an instrument taking measurements, appending them to a BLOB
and at regular intervals, sending to a client as BLOB .csv files.

The indipyclient needs to have BLOBs enabled with a folder set where
the BLOB files will be saved
"""

import asyncio, io, collections, math

from datetime import datetime, timezone, timedelta

import indipydriver as ipd

# uncomment to enable logging
#
# import logging
# logger = logging.getLogger()
# fh = logging.FileHandler("logfile.log")
# logger.addHandler(fh)
# logger.setLevel(logging.DEBUG)


class MakeBlobs:
    """This is a simulation containing variables only, normally it
       would take measurements from a sensor.

       measurements are added to a io.BytesIO object over a perod of
       'minutes', this object is then added to a que, and a new
       io.BytesIO object is created."""

    def __init__(self, minutes=1):
        """Set start up values"""

        # set logtime for minutes in the future
        self.delta = timedelta(minutes=minutes)
        self.logtime = datetime.now(tz=timezone.utc) + self.delta

        self.blobfiles = collections.deque(maxlen=4)
        # self.blobfiles is a deque containing a number of io.BytesIO objects
        # with the number limited to 4
        # the older buffers can be sent to the client,
        # or if not taken off, will be discarded.

        # measurements will be set in self.currentblob
        self.currentblob = io.BytesIO()


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
           and adds logs to the io.BytesIO() object."""

        t = 0
        while True:
            await asyncio.sleep(2)

            # simulate a varying measurement
            t += 0.5
            value = 20.0 + 10*math.sin(t)

            # set the value and timestamp into the blobfile
            timestamp = datetime.now(tz=timezone.utc)

            # append a log line
            self.appendlog(timestamp, value)


class InstrumentDriver(ipd.IPyDriver):

    """IPyDriver is subclassed here to create a driver for the instrument"""


    async def hardware(self):
        """This is a continuously running coroutine which is used
           to transmit the blob to connected clients."""

        blobcontrol = self.driverdata["blobcontrol"]
        # blobcontrol is a MakeBlobs object

        blobvector = self['instrument']['blobvector']
        while not self.stop:
            # if a blobfile is available, send it as a BLOB
            blobfile = blobcontrol.get_blobfile()
            # this returns None if no blobfile is currently available
            if blobfile:
                blobvector["blobmember"] = blobfile
                # send the blob
                await blobvector.send_setVectorMembers(members=["blobmember"])

            # ensure this function does
            # not block, by giving a sleep here
            await asyncio.sleep(1)


def make_driver():
    "Returns an instance of the driver"

    blobcontrol = MakeBlobs(minutes=2) # create BLOBs every two minutes

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
    instrument = ipd.Device( devicename="instrument",
                             properties=[blobvector] )

    # set the coroutine to be run with the driver
    pollingcoro = blobcontrol.poll_measurement()

    # Create the Driver, containing this device and
    # other objects needed to run the instrument
    driver = InstrumentDriver( instrument,                # the device
                               pollingcoro,               # a coroutine to be awaited
                               blobcontrol=blobcontrol )  # MakeBlobs to place in driverdata

    # and return the driver
    return driver


if __name__ == "__main__":

    driver = make_driver()
    server = ipd.IPyServer(driver)
    # alternatively, to accept remote connections
    # server = ipd.IPyServer(driver, host="0.0.0.0")
    asyncio.run(server.asyncrun())
