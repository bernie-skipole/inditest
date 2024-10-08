# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "indipyclient",
# ]
# ///


"""Connects to server, listens 5 seconds, prints properties, shuts down"""


import asyncio
from indipyclient import IPyClient


async def main():
    "Print all devices, vectors and values then shut down"

    # get an instance of IPyClient, which, using its default
    # values, will connect to a server running on localhost
    client = IPyClient()

    # run the client.asyncrun() method to start the connection
    # and obtain values from the server
    client_task = asyncio.create_task(client.asyncrun())

    # after starting, wait 5 seconds for devices to be learnt
    # by the client
    await asyncio.sleep(5)

    for devicename, device in client.items():
        print(f"Device : {devicename}")
        for vectorname, vector in device.items():
            print(f"  Vector : {vectorname}")
            for membername, value in vector.items():
                print(f"    Member : {membername} Value : {value}")

    # request a shutdown
    client.shutdown()

    # wait for the shutdown
    await client_task


asyncio.run( main() )
