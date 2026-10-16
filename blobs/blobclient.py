# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "indipyclient",
# ]
# ///

"""Uses all defaults to make a call to localhost and set incoming BLOBs to the local folder"""

import asyncio
import indipyclient as ipc


# Makes call to localhost

ipclient = ipc.IPyClient()

# Receives BLOBS and places them in the current folder

ipclient.BLOBfolder = "./"

asyncio.run(ipclient.asyncrun())
