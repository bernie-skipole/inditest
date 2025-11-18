# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "indipyserver"
# ]
# ///

import asyncio

from indipyserver import IPyServer


async def sendmessage(server, message):
    "Sends a message every two seconds"
    while True:
        await asyncio.sleep(2)
        await server.send_message(message)


async def main():
    "Create the server with a repeating message"
    server = IPyServer()
    await asyncio.gather( server.asyncrun(), sendmessage(server, "Hello") )


if __name__ == "__main__":
    print(f"Running {__file__}")
    asyncio.run(main())
