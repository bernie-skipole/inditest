# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "indipydriver>=3.0.2",
#     "indipyserver"
# ]
# ///


"""
sendblob.py should be running on a remote device,
('raspberrypi' in this example), which needs its ipyserver host
to be set at 0.0.0.0 so that a connection can be made to it.
This program makes a connection to the remote, and
snoops on the BLOBs it is sending, and saves its own
copies.  It also serves the INDI port for a local client to
connect and sends an Alert light if it is not getting BLOBs.
A client connected here will see both the light and the
blob instrument.
"""

import asyncio, time

import logging, sys
logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)

import indipydriver as ipd

from indipyserver import IPyServer

class LightControl:
    "This times and sets the light value"

    def __init__(self, devicename, seconds):
        """Set initial value of light, and the time in
           seconds to wait before setting an alert"""
        self.devicename = devicename
        self.value = "Idle"
        self._update_time = time.time()
        self.seconds = seconds

    def blob_ok(self):
        """Called when a blob is received, sets value
           and resets the timer"""
        self.value = "Ok"
        self._update_time = time.time()

    def check_status(self):
        "If timer has elapsed, sets value to Alert"
        elapsed_time = time.time() - self._update_time
        if elapsed_time > self.seconds:
            self.value = "Alert"


class _SnoopBLOBDriver(ipd.IPyDriver):

    """IPyDriver is subclassed here. This snoops on 'instrument' and has a single
       light member which goes Ok when a file is received, and Alert if one is
       not received after three minutes"""

    async def hardware(self):
        """Update client with light value, and send getProperties to
           initiate a snoop on the instrument device"""

        # Send an initial getProperties to snoop on instrument
        # This is necessary to inform IPyServer that this driver
        # wants copies of blob data

        self.snoop(self.driverdata["snoopdevice"], "blobvector", timeout=5)

        # get the LightControl object
        lightcontrol = self.driverdata["lightcontrol"]
        # get the light vector
        lightvector = self[lightcontrol.devicename]['lightvector']

        # check lightcontrol
        while not self._stop:
            lightcontrol.check_status()
            if lightcontrol.value == "Ok":
                if lightvector['lightmember'] != "Ok":
                    # update light on client to Ok
                    lightvector['lightmember'] = "Ok"
                    await lightvector.send_setVector(message="Receiving BLOB's", state="Ok")
                # check again after a second
                await asyncio.sleep(1)
            else:
                # Not ok, so send an alert
                newvalue = lightcontrol.value
                lightvector['lightmember'] = newvalue
                await lightvector.send_setVector(message="Not receiving BLOB's", state=newvalue)
                # the instrument could have been turned off, or link disconnected
                # and wait a while, so not continuously sending alerts
                await asyncio.sleep(5)


    async def snoopevent(self, event):
        """Handle receipt of a snoop event from sendblob.py"""

        # get the LightControl object
        lightcontrol = self.driverdata["lightcontrol"]

        # get the devicename of object being snooped
        snoopdevice = self.driverdata["snoopdevice"]

        if isinstance(event, ipd.setBLOBVector):
            if event.devicename==snoopdevice and event.vectorname=="blobvector" and "blobmember" in event:
                # A setBLOBVector has been sent from sendblob
                # and this driver has received a copy, and so can save the file
                blobvalue = event["blobmember"]
                # make filename from timestamp and file extension
                # event.sizeformat is a dictionary of membername:(size, format)
                fileformat = event.sizeformat["blobmember"][1]
                timestampstring = event.timestamp.strftime('%Y%m%d_%H_%M_%S')
                filename = "blob_" + timestampstring + fileformat
                with open(filename, "wb") as fp:
                    # Write bytes to file
                    fp.write(blobvalue)
                    # and update lightcontrol timer to ensure light is Ok
                    lightcontrol.blob_ok()


def make_driver(devicename, snoopdevice, alertseconds):
    "Creates the driver"

    # Create light timer to alert after alertseconds
    lightcontrol = LightControl(devicename, seconds=alertseconds)

    # create member
    lightmember = ipd.LightMember( name="lightmember",
                                   label="BLOB received status",
                                   membervalue=lightcontrol.value )
    # set this member into a vector
    lightvector = ipd.LightVector( name="lightvector",
                                   label="BLOB received status",
                                   group="Status",
                                   state=lightcontrol.value,
                                   lightmembers=[lightmember] )
    # create a Device with this vector
    lightdevice = ipd.Device( devicename=devicename, properties=[lightvector])

    # Create the Driver containing this device and with
    # named arguments lightcontrol and snoopdevice which will be set into driverdata
    driver = _SnoopBLOBDriver(lightdevice, lightcontrol=lightcontrol, snoopdevice=snoopdevice)

    # and return the driver
    return driver


if __name__ == "__main__":

    # This driver is for device lightdevice
    # which snoops on device blobmaker and saves a copy of the blobs
    # and send an alert if nothing received in 150 seconds
    # blobs should normally be received every 2 minutes, 120 seconds

    driver = make_driver("lightdevice", "blobmaker", 150)
    server = IPyServer(driver)
    # make a connection to the remote sendblob service
    server.add_remote(host="raspberrypi",
                      port=7624,
                      blob_enable="Also",
                      debug_enable=True)
    print(f"Running {__file__} with indipydriver version {ipd.version}")
    asyncio.run(server.asyncrun())
