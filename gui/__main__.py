
import asyncio, queue, threading, time, collections


import sys
sys.path.insert(0, "/home/bernard/git/indipyclient")

import indipyclient as ipc

from .guiclient import rungui


EventItem = collections.namedtuple('EventItem', ['eventtype', 'devicename', 'vectorname', 'timestamp', 'snapshot'])


class GuiClient(ipc.IPyClient):

    """Overrides IPyClient
       On receiving an event, appends a snapshot into rxque
       Which will pass to Guiclient"""

    async def rxevent(self, event):
        """Add event type and snapshot to rxque"""
        rxque = self.clientdata['rxque']
        if event.eventtype == "Define":
            item = EventItem(event.eventtype, event.devicename, event.vectorname, event.timestamp, event.vector.snapshot())
        elif event.eventtype == "DefineBLOB":
            item = EventItem(event.eventtype, event.devicename, event.vectorname, event.timestamp, event.vector.snapshot())
        elif event.eventtype == "Set":
            item = EventItem(event.eventtype, event.devicename, event.vectorname, event.timestamp, event.vector.snapshot())
        elif event.eventtype == "SetBLOB":
            item = EventItem(event.eventtype, event.devicename, event.vectorname, event.timestamp, event.vector.snapshot())
        elif event.eventtype == "Delete":
            item = EventItem(event.eventtype, event.devicename, event.vectorname, event.timestamp, event.device.snapshot())
        elif event.eventtype == "Message":
            if event.devicename is None:
                # state wide message
                item = EventItem(event.eventtype, event.devicename, event.vectorname, event.timestamp, list(self.messages))
            else:
                item = EventItem(event.eventtype, event.devicename, event.vectorname, event.timestamp, list(event.device.messages))
        elif event.eventtype == "TimeOut":
            item = EventItem(event.eventtype, event.devicename, event.vectorname, event.timestamp, event.vector.snapshot())
        else:
            return
        while not self._stop:
            try:
                rxque.put_nowait(item)
            except queue.Full:
                asyncio.sleep(0.01)
            else:
                break

    async def hardware(self):
        "Read txque and send data"
        txque = self.clientdata['txque']
        while not self._stop:
            try:
                item = txque.get_nowait()
            except queue.Empty:
                asyncio.sleep(0.02)
            else:
                if item is None:
                    # A None in the queueis a shutdown indicator
                    self.shutdown()
                    return
                await self.send_newVector(item.devicename, item.vectorname, members=item.members):


if __name__ == "__main__":

    # create queue where client will put snapshots on receiving data
    rxque = queue.Queue(maxsize=3)
    # create queue of things to send
    txque = queue.Queue(maxsize=3)
    # create a GuiClient object
    client = GuiClient(indihost="localhost", indiport=7624, txque = txque, rxque = rxque)

    # rungui in its own thread
    clientapp = threading.Thread(target=rungui, args=(txque, rxque))
    clientapp.start()
    print(f"Running {__file__}")
    asyncio.run(client.asyncrun())
