# inditest
Contains example and test scripts for indipydriver and indipyclient

See

https://github.com/bernie-skipole/indipydriver

https://github.com/bernie-skipole/indipyclient


Note these examples have Inline script metadata defining their\
dependencies on indipydriver and indipyclient, and so if copied\
to your own machine, and if you have a tool such as uv, which\
will automatically pull in dependencies, you should be able to\
very simply run the scripts with:

uv run examplescript.py

and a client console with

uvx indipyclient

Any client example using the console will not run on windows,\
as these use the curses package.


#### docexamples
The examples used in indipydriver readthedocs documentation

led.py Raspberry Pi LED driver.\
simulated\_led.py Simulates gpiozero.LED so can be run without an actual LED\
example1.py Simulated thermostat driver.\
example2.py Simulated thermostatwith settable target.\
example3.py Window control snooping on thermostat.\
addexdriver.py IPyServer serving executable third part drivers.\
temperatureclient.py client printing temperature as it is received.\
driverclient.py combining console client and driver in one script.

#### snapshot
Testing the use of the client snapshot with a threaded function.

simpledriver.py Driver prints and sends an incrementing number\
and receives and prints a number.

threadedclient.py Client which receives a number, takes a snapshot of\
the client state and passes that to a threaded blocking function which\
manipulates the number and sends it back to the driver.

#### blobs

Examples transmitting and receiving BLOBs

sendblob.py Driver sending short files of measurements at regular intervals\
getblob.py Driver to receive and save a BLOB file\
multiblobs.py Driver receiving vector with multiple blob members\
snoopremote.py Driver snooping on remote running sendblob.py

#### text

Examples transmitting and receiving text

rwtext.py Driver with ten rw members, also sends values every ten seconds\
txrxtext.py Driver transmitting text vector with multiple members

#### lights

Examples sending lights

bincount.py Driver sending a vector with four lights binary counting

#### switches

Examples transmitting and receiving switch information

anyofmany.py Driver with one vector and multiple anyofmany switches

#### numbers

Examples transmitting and receiving numbers

counter.py Driver transmitting incrementing integers, and receiving floats.

#### messages

led\_message.py As simulated\_led.py with an additional message sent every two seconds

only_message.py Server with no drivers, but sending a message every two seconds.

#### remotes

led1.py As simulated\_led.py but set to listen on port 7625 and with devicename led1

led2.py As simulated\_led.py but set to listen on port 7626 and with devicename led2

serve\_remotes.py Connects to two remote servers led1.py and led2.py\
Rather than using remote machines, these three services are all on\
one machine using different ports.

#### invalid

Duplicate devicenames are not allowed, these tests check if they are detected

duplicatedevice1.py Two drivers, both with the same devicename

duplicatedevice2.py One driver but with two devices with the same name

led1.py As simulated\_led.py but set to listen on port 7625 and with devicename led

led2.py As simulated\_led.py but set to listen on port 7626 and with devicename led

serve\_remotes.py Connects to two remote servers led1.py and led2.py\
Rather than using remote machines, these three services are all on\
one machine using different ports. The duplicate names on the remote connections\
should be detected and cause the calling server to shutdown
