
import asyncio, queue, threading, collections

import sys
sys.path.insert(0, "/home/bernard/git/indipyclient")

import indipyclient as ipc

from .guiclient import rungui


EventItem = collections.namedtuple('EventItem', ['eventtype', 'devicename', 'vectorname', 'timestamp', 'snapshot'])


class QueClient(ipc.IPyClient):

    """Overrides IPyClient
       On receiving an event, appends a snapshot into self.rxque
       Gets contents of self.txque and transmits updates"""


    def __init__(self, indihost="localhost", indiport=7624):
        super().__init__(indihost, indiport)
        # create queue where client will put snapshots on receiving data
        self.rxque = queue.SimpleQueue()
        # create queue of things to send
        self.txque = queue.SimpleQueue()


    async def rxevent(self, event):
        """Add event type and snapshot to self.rxque"""
        item = EventItem(event.eventtype, event.devicename, event.vectorname, event.timestamp, self.snapshot())
        self.rxque.put(item)


    async def optionrxevent(self, event):
        """Add event type and snapshot to self.rxque"""
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
        self.rxque.put(item)


    async def hardware(self):
        """Read self.txque and send data
           Item passed in the queue should be a tuple or list of (devicename, vectorname, value)
           where value is normally a membername to membervalue dictionary
           If value is a string, one of  "Never", "Also", "Only" then an enableBLOB will be sent
           If the item is None, this indicates the client should shut down"""
        while not self._stop:
            try:
                item = self.txque.get_nowait()
            except queue.Empty:
                await asyncio.sleep(0.02)
                continue
            if item is None:
                # A None in the queue is a shutdown indicator
                self.shutdown()
                return
            if len(item) != 3:
                # invalid item
                continue
            if item[2] in ("Never", "Also", "Only"):
                await self.send_enableBLOB(item[2], item[0], item[1])
            else:
                await self.send_newVector(item[0], item[1], members=item[2])


if __name__ == "__main__":

    # create a QueClient object
    client = QueClient(indihost="localhost", indiport=7624)
    # rungui in its own thread
    clientapp = threading.Thread(target=rungui, args=(client.txque, client.rxque))
    clientapp.start()
    print(f"Running {__file__}")
    asyncio.run(client.asyncrun())
