
import asyncio, queue, threading, time, collections


import sys
sys.path.insert(0, "/home/bernard/git/indipyclient")

import indipyclient as ipc

from .guiclient import rungui


# events could be one of
# delProperty, Message, VectorTimeOut
# defSwitchVector, defTextVector, defNumberVector, defLightVector, defBLOBVector,
# setSwitchVector, setTextVector, setNumberVector, setLightVector, setBLOBVector

EventItem = collections.namedtuple('EventItem', ['eventtype', 'devicename', 'vectorname', 'timestamp', 'snapshot'])


class _Client(ipc.IPyClient):

    """Overrides IPyClient
       On receiving an event, appends a client snapshot into eventque
       Which will pass to Guiclient"""

    async def rxevent(self, event):
        """Add event type and client snapshot to snapque"""
        snapque = self.clientdata['snapque']
        item = EventItem(event.eventtype, event.devicename, event.vectorname, event.timestamp, self.snapshot())
        snapque.put_nowait(item)


if __name__ == "__main__":

    # create queue where client will put snapshots
    snapque = queue.Queue()
    # create que of things to send
    txqueue = queue.Queue()
    # create a _Client object
    client = _Client(indihost="localhost", indiport=7624, snapque = snapque, txqueue = txqueue)

    # run guiclient in its own thread
    clientapp = threading.Thread(target=rungui, args=(snapque, txqueue))
    clientapp.start()
    print(f"Running {__file__}")
    asyncio.run(client.asyncrun())
