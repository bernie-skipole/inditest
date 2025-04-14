# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "indipyclient",
#     "valkey"
# ]
# ///


import asyncio
from indipyclient.queclient import QueClient

import valkey.asyncio as valkey


async def sendvector(vk, devicename, vectorname, vectdict):

    # Saves the vector attributes to valkey, apart from members
    mapping = {key:value for key,value in vectdict.items() if key != "members"}
    for key,val in mapping.items():
        if isinstance(val, bool):
            mapping[key] = "True" if val else "False"
        if val is None:
            mapping[key] = "None"
    await vk.hset(f'attributes:{devicename}:{vectorname}', mapping=mapping)

    # save list of member names
    # get list of member names sorted by label
    memberdict = vectdict["members"]
    memberlist = list(memberdict.keys())
    memberlist.sort(key=lambda x: memberdict[x]['label'])
    for membername in memberlist:
        await vk.sadd(f'members:{devicename}:{vectorname}', membername)   # add membername to 'members:<propertyname>:<devicename>'
        memberatts = memberdict[membername]
        for key,val in memberatts.items():
            if isinstance(val, bool):
                memberatts[key] = "True" if val else "False"
            if val is None:
                memberatts[key] = "None"
        await vk.hset(f'memberattributes:{devicename}:{vectorname}:{membername}', mapping=memberatts)


async def handle_rxevents(vk, rxque, channel, inc_blob):
    """On being called when an event is received, this saves any changes to valkey

       vk is a Valkey connection
       rxque is an asyncio.Queue providing events which are named tuples with attributes:

       eventtype -  a string, one of Message, getProperties, Delete, Define, DefineBLOB, Set, SetBLOB,
                    these indicate data is received from the client, and the type of event. It could
                    also be the string "snapshot", which does not indicate a received event, but is a
                    response to a snapshot request received from txque, or "TimeOut" which indicates an
                    expected update has not occurred, or "State" which indicates you have just transmitted
                    a new vector, and therefore the snapshot will have your vector state set to Busy.
       devicename - usually the device name causing the event, or None if not applicable.
       vectorname - usually the vector name causing the event, or None if not applicable.
       timestamp -  the event timestamp, None for the snapshot request.
       snapshot -   For anything other than eventtype 'snapshot' it will be a full snapshot of the client.
                    If the eventtype is 'snapshot' and devicename and vectorname are None, it will be a
                    client snapshot, if devicename only is given it will be a device snapshot, or if both
                    devicename and vectorname are given it will be a vector snapshot."""

    while True:

        event = await rxque.get()

        eventtype = event.eventtype
        devicename = event.devicename
        vectorname = event.vectorname
        snapshot = event.snapshot

        rxque.task_done()

        if eventtype == "getProperties":
            continue

        if eventtype == "Message":
            if devicename is None:
                await vk.delete("messages")
                messagelist = snapshot.messages
                for m in messagelist:
                    message = f"{m[0].isoformat(sep='T')} {m[1]}"
                    await vk.rpush("messages", message)
            else:
                await vk.delete(f"messages:{devicename}")
                messagelist = snapshot[devicename].messages
                for m in messagelist:
                    message = f"{m[0].isoformat(sep='T')} {m[1]}"
                    await vk.rpush(f"messages:{devicename}", message)

        elif (devicename is not None) and (vectorname is not None):
            if eventtype == "snapshot":
                vectdict = snapshot.dictdump(inc_blob)
            else:
                vectdict = snapshot[devicename][vectorname].dictdump(inc_blob)
            # add the device to vk set 'devices'
            await vk.sadd('devices', devicename)
            await vk.sadd(f'properties:{devicename}', vectorname)   # add property name to 'properties:<devicename>'
            await sendvector(vk, devicename, vectorname, vectdict)

        elif (eventtype == "snapshot") and (devicename is not None):
            # add the device to vk set 'devices'
            await vk.sadd('devices', devicename)
            # device snapshot
            for vname in snapshot.keys():
                vectdict = snapshot[vname].dictdump(inc_blob)
                await vk.sadd(f'properties:{devicename}', vname)   # add property name to 'properties:<devicename>'
                await sendvector(vk, devicename, vname, vectdict)

        elif eventtype == "snapshot":
            for dname in snapshot.keys():
                await vk.sadd('devices', dname)
                for vname in snapshot[dname].keys():
                    vectdict = snapshot[dname][vname].dictdump(inc_blob)
                    await vk.sadd(f'properties:{dname}', vname)   # add property name to 'properties:<devicename>'
                    await sendvector(vk, dname, vname, vectdict)

        await vk.publish(channel, f"{eventtype} {devicename if devicename else "None"} {vectorname if vectorname else "None"}")


async def main():
    try:
        vk = valkey.Valkey(host='raspberrypi', port=6379)
        await vk.flushdb()
        txque = asyncio.Queue(maxsize=4)
        rxque = asyncio.Queue(maxsize=4)
        client = QueClient(txque, rxque, indihost="localhost", indiport=7624, blobfolder=None)
        task1 = asyncio.create_task(handle_rxevents(vk, rxque, "indievent", False))
        await client.asyncrun()
    finally:
        task1.cancel()
        await task1
        await vk.aclose()

if __name__ == "__main__":
    # Start the client
    asyncio.run(main())
