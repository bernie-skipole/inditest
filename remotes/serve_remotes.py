# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "indipydriver",
# ]
# ///

"""Set to connect to remote servers led1.py, led2.py and sendblob.py
   Rather than using remote machines, these three services are all on
   one machine using different ports"""


import asyncio
import indipydriver as ipd


if __name__ == "__main__":

    server = ipd.IPyServer(host="localhost", port=7624, maxconnections=5)

    # connect to two remote servers
    server.add_remote(host="localhost", port=7625)
    server.add_remote(host="localhost", port=7626)
    server.add_remote(host="localhost", port=7627, blob_enable=True)
    # Note blobs are enabled on the link to sendblob.py
    print(f"Running {__file__} with indipydriver version {ipd.version}")
    asyncio.run(server.asyncrun())
