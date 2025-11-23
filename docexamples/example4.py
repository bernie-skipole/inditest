# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "indipydriver>=3.0.2",
#     "indipyserver",
#     "indipyweb"
# ]
# ///

# A single script to run the thermostat and window drivers
# and the indipyweb service.

import asyncio, subprocess, sys

import indipydriver as ipd

from indipyserver import IPyServer

# Assuming the thermostat example is example2.py,
# and the window example is example3.py

import example2, example3
# make the thermostat driver
thermodriver = example2.make_driver("Thermostat", 15)
# make the window driver
windowdriver = example3.make_driver("Window", "Thermostat")

server = IPyServer(thermodriver, windowdriver)

# run indipyweb in a subprocess, first create list of args

args = [ sys.executable,    # The Python executable, ensures the one from the virtual environment is used
         "-m",
         "indipyweb",
         "--port",
         "8000",
         "--host",
         "0.0.0.0"     # Listening host of the web server.
        ]
# run the webservice
p = subprocess.Popen(args,
                     stdin=subprocess.DEVNULL,
                     stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL)

print(f"Web service running on {args[6]}:{args[4]}")

try:
    # run the IPyServer
    asyncio.run( server.asyncrun() )
except KeyboardInterrupt:
    print("Keyboard Interrupt")

# shutdown the web service
p.terminate()
print("Closing application.. Please wait")
try:
    p.wait(4)
except subprocess.TimeoutExpired:
    p.kill()
    p.wait()
print("Application Stopped")
