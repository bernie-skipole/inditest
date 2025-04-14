# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "valkey"
# ]
# ///


"""
Illustrates how INDI parameters stored in a Valkey server using vkclient.py
can be read. This could be used by a 'display' service to show an instruments output
"""


import pprint

import valkey


def main(vk, channel):

    p = vk.pubsub(ignore_subscribe_messages=True)
    p.subscribe(channel)

    print("This prints the INDI parameters stored in a Valkey service")
    print("with all items decoded from their byte values")
    messages = vk.lrange('messages', 0, -1)
    print("KEY - 'messages'")
    pprint.pp(messages)
    print("------------------")
    devicenames = vk.smembers('devices')
    print("KEY - 'devices'")
    pprint.pp(devicenames)
    print("------------------")
    for devicename in devicenames:
        key = f"messages:{devicename}"
        print(f"KEY - '{key}'")
        messages = vk.lrange(key, 0, -1)
        pprint.pp(messages)
        print("------------------")
        key = f"properties:{devicename}"
        print(f"KEY - '{key}'")
        vectornames = vk.smembers(key)
        pprint.pp(vectornames)
        print("------------------")
        for vectorname in vectornames:
            key = f"attributes:{devicename}:{vectorname}"
            print(f"KEY - '{key}'")
            attdict = vk.hgetall(key)
            pprint.pp(attdict)
            print("------------------")
            key = f"members:{devicename}:{vectorname}"
            print(f"KEY - '{key}'")
            membernames  = vk.smembers(key)
            pprint.pp(membernames)
            print("------------------")
            for membername in membernames:
                key = f"memberattributes:{devicename}:{vectorname}:{membername}"
                print(f"KEY - '{key}'")
                mattdict = vk.hgetall(key)
                pprint.pp(mattdict)
                print("------------------")

    for message in p.listen():
        items = message['data'].split(" ")
        if len(items) != 3:
            continue
        if items[0] in ("Delete", "Define", "DefineBLOB", "Set", "SetBLOB"):
            devicename = items[1]
            vectorname = items[2]
            membernames  = vk.smembers(f"members:{devicename}:{vectorname}")
            for membername in membernames:
                key = f"memberattributes:{devicename}:{vectorname}:{membername}"
                print(f"KEY - '{key}'")
                mattdict = vk.hgetall(key)
                pprint.pp(mattdict)
                print("------------------")

if __name__ == "__main__":
    vk = valkey.Valkey(host='raspberrypi', port=6379, decode_responses=True)
    main(vk, "indievent")
