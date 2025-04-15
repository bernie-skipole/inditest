# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "indipyclient",
#     "valkey"
# ]
# ///


"""
This client uses QueClient to get snapshots of data and saves it to a Valkey server

This could be useful for a display, or multiple displays to continuously show updating values

An example of accessing the valkey server is given in file vkprint.py
"""

import asyncio
from indipyclient.queclient import QueClient

import valkey.asyncio as valkey


async def _sendvector(vk, devicename, vectorname, vectdict):
    """Function to save a vector dictionary to valkey
       Note, boolean values are saved as strings of either 'True' or 'False'
       None values are saved as the string 'None'
    """

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


async def handle_rxevents(vk, rxque, channel, inc_blob, nbr=8):
    """On being called when an event is received, this saves data to valkey

       vk is a Valkey async connection, which should be created using valkey.asyncio.Valkey
       rxque is an asyncio.Queue which will provide events from a QueClient
       channel is a pubsub channel string, notifications of an event will be published on this channel
       inc_blob is True if BLOBs are to be saved in the valkey database, False if not
       nbr is the number of received system and device messages to keep in valkey lists

       Valkey keys used:

       "messages" - list of system messages, being strings of "timestamp space message", at most nbr items in the list.
      f"messages:{devicename}" - list of device messages, being strings of "timestamp space message", at most nbr items in the list.
       "devices" - set of device names
      f"properties:{devicename}" - set of vector names for the device
      f"attributes:{devicename}:{vectorname}" - a mapping of each vector attribute with its value, for the given vector
      f"members:{devicename}:{vectorname}" - a set of member names for the vector
      f"memberattributes:{devicename}:{vectorname}:{membername}" - a mapping of each member attribute with its value, for the given member
                                                                   this will include the actual member value

      The attributes referred to above are those indi attributes specified for a vector and member, such as 'label' etc., with a few
      useful extras such as 'formattedvalue'.

      As events are received on rxque, the Valkey database is populated with keys as given above. Also an event notification
      will be published using:

      vk.publish(channel, f"{eventtype}")    - if no devicename or vectorname are given in the event, for example a system message.
      vk.publish(channel, f"{eventtype} {devicename}")  - if a devicename is given, but no vectorname
      vk.publish(channel, f"{eventtype} {devicename} {vectorname}")  - if the event has both a devicename and vectorname

      This could be used by an appropriate client to listen for events, and only read the database when an event occurs.

      The eventtype is that received from QueClient, it is a string:

      One of Message, getProperties, Delete, Define, DefineBLOB, Set, SetBLOB,
      these indicate data is received from the client, and the type of event. It could
      also be the string "snapshot", which does not indicate a received event, but is a
      response to a snapshot request received from txque, or "TimeOut" which indicates an
      expected update has not occurred, or "State" which indicates you have just transmitted
      a new vector, and therefore the vector state will be set to Busy.

"""

    # set nbr to a value used by ltrim to reduce the number of messages in the list
    nbr = -nbr

    while True:

        event = await rxque.get()

        eventtype = event.eventtype
        devicename = event.devicename
        vectorname = event.vectorname
        timestamp = event.timestamp
        snapshot = event.snapshot

        rxque.task_done()

        if eventtype == "getProperties":
            continue

        if eventtype == "Message":
            if devicename is None:
                # system wide message
                messagelist = snapshot.messages
                # a message consists of a timestamp and string
                # get the message from the snapshot that this event refers to
                for message in messagelist:
                    if message[0] == timestamp:
                        mt,ms = message
                        break
                else:
                    continue
                # place <timestamp><space><message string> into list with key 'messages'
                await vk.rpush("messages", f"{mt.isoformat(sep='T')} {ms}")
                await vk.ltrim("messages", nbr, -1)
            else:
                # a device message
                messagelist = snapshot[devicename].messages
                # a message consists of a timestamp and string
                # get the message from the snapshot that this event refers to
                for message in messagelist:
                    if message[0] == timestamp:
                        mt,ms = message
                        break
                else:
                    continue
                # place <timestamp><space><message string> into list with key 'messages<devicename>'
                await vk.rpush(f"messages:{devicename}", f"{mt.isoformat(sep='T')} {ms}")
                await vk.ltrim(f"messages:{devicename}", nbr, -1)

        elif (devicename is not None) and (vectorname is not None):
            if eventtype == "snapshot":
                vectdict = snapshot.dictdump(inc_blob)
            else:
                vectdict = snapshot[devicename][vectorname].dictdump(inc_blob)
            # add the device to vk set 'devices'
            await vk.sadd('devices', devicename)
            await vk.sadd(f'properties:{devicename}', vectorname)   # add property name to 'properties:<devicename>'
            await _sendvector(vk, devicename, vectorname, vectdict)

        elif (eventtype == "snapshot") and (devicename is not None):
            # add the device to vk set 'devices'
            await vk.sadd('devices', devicename)
            # device snapshot
            for vname in snapshot.keys():
                vectdict = snapshot[vname].dictdump(inc_blob)
                await vk.sadd(f'properties:{devicename}', vname)   # add property name to 'properties:<devicename>'
                await _sendvector(vk, devicename, vname, vectdict)

        elif eventtype == "snapshot":
            for dname in snapshot.keys():
                await vk.sadd('devices', dname)
                for vname in snapshot[dname].keys():
                    vectdict = snapshot[dname][vname].dictdump(inc_blob)
                    await vk.sadd(f'properties:{dname}', vname)   # add property name to 'properties:<devicename>'
                    await _sendvector(vk, dname, vname, vectdict)

        # publish a note on a channel to indicate a change has occurred
        if vectorname:
            await vk.publish(channel, f"{eventtype} {devicename} {vectorname}")
        elif devicename:
            await vk.publish(channel, f"{eventtype} {devicename}")
        else:
            await vk.publish(channel, f"{eventtype}")


async def main():
    try:
        vk = valkey.Valkey(host='localhost', port=6379)
        await vk.flushdb()
        txque = asyncio.Queue(maxsize=4)  # txque is not used in this example, but could be used to send data
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
