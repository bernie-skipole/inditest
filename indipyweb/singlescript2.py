# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "indipydriver>=3.0.2",
#     "indipyserver",
#     "indipyweb",
#     "uvicorn"
# ]
# ///

# A single script to run the thermostat and window drivers,
# indipyserver and the indipyweb service.

import asyncio
import uvicorn
from indipyserver import IPyServer
from indipyweb import make_app, get_dbhost, get_dbport



# Assuming the thermostat example is example2.py,
# and the window example is example3.py

import example2, example3


def make_indi_server():
    # make the thermostat driver
    thermodriver = example2.make_driver("Thermostat", 15)
    # make the window driver
    windowdriver = example3.make_driver("Window", "Thermostat")
    # make the server, note if web server is set to call different INDI ports, these will have to match
    indiserver = IPyServer(thermodriver, windowdriver, host="localhost", port=7624, maxconnections=5)
    return indiserver


def make_web_server():
    app = make_app(dbfolder=None, securecookie = False, basepath = '')
    config = uvicorn.Config(app=app, host=get_dbhost(), port=get_dbport(), log_level="error")
    webserver = uvicorn.Server(config)
    return webserver


async def run_all():
    indiserver = make_indi_server()
    webserver = make_web_server()
    try:
        async with asyncio.TaskGroup() as tg:
            # run the indi server, together with its drivers
            tg.create_task( indiserver.asyncrun() )
            # run the web server
            tg.create_task( webserver.serve() )
    finally:
        indiserver.shutdown()

def main():
    "Run the program"
    asyncio.run(run_all())


if __name__ == "__main__":
    main()
    print("Application Stopped")
