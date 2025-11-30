# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///


import json
import urllib.request
from time import sleep

# Every 10 seconds this example calls indipyweb running on a device 'raspberry5' which
# is serving a Thermostat device, and prints the temperature

while True:

    # get a snapshot

    with urllib.request.urlopen('http://raspberry5/api/') as f:
        snapshot = f.read().decode('utf-8')

    # snapshot is a string snapshot of the state of the client

    nesteddict = json.loads(snapshot)

    # nesteddict is a nested dictionary, in this case of the Thermostat example.
    # It would be worth doing a pretty print of this to see how the dictionary is laid out
    # or simply call the URL with a browser to view the JSON layout.

    # In this case, just to get the temperature value:

    t = nesteddict['devices']['Thermostat']['vectors']['temperaturevector']['members']['temperature']['formattedvalue']

    # key 'devices' contains all the devices
    # within 'devices' key 'Thermostat' is the name of the particular device we want
    # within a specific device, key 'vectors' contains all the vectors of that device
    # within 'vectors', 'temperaturevector' is the name of the particular vector we want
    # within a specific vector, key 'members' contains all the members of that vector
    # within 'members', 'temperature' is the name of the particular member we want
    # within a specific number member, key 'formattedvalue' gives a string of the number

    print(t)

    sleep(10)
