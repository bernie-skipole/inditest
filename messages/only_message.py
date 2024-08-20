
# for my own testing, please ignore
import sys
sys.path.insert(0, "/home/bernie/git/indipydriver")
sys.path.insert(0, "/home/bernie/git/indipyclient")

import logging
logger = logging.getLogger()
fh = logging.FileHandler("logfile.log")
logger.addHandler(fh)
logger.setLevel(logging.DEBUG)

import asyncio
import indipydriver as ipd


async def sendmessage(server, message):
    "Sends a message every two seconds"
    while True:
        await asyncio.sleep(2)
        await server.send_message(message)


async def main():
    "Create the server with a repeating message"
    server = ipd.IPyServer()
    await asyncio.gather( server.asyncrun(), sendmessage(server, "Hello") )


if __name__ == "__main__":
    asyncio.run(main())


