# inditest
Contains example and test scripts for the suite of 'indipy' programs

See

## indipydriver

Provides classes you use to create a driver for your instrumentation which sets, updates and reads data.

https://github.com/bernie-skipole/indipydriver

https://pypi.org/project/indipydriver

https://indipydriver.readthedocs.io

## indipyserver

Provides a class to serve your driver (or multiple drivers) on a port

https://github.com/bernie-skipole/indipyserver

https://pypi.org/project/indipyserver/

https://indipyserver.readthedocs.io

## indipyclient

Connects to an INDI port, decodes the INDI protocol and presents the received data as Python classes

https://github.com/bernie-skipole/indipyclient

https://pypi.org/project/indipyclient

https://indipyclient.readthedocs.io

## indipyweb

INDI client, connects to an INDI port, and then acts as a web server, users can connect with their browser to display and control the instrument parameters

https://github.com/bernie-skipole/indipyweb

https://pypi.org/project/indipyweb/

## indipyterm

INDI terminal client, connects to an INDI port and presents a terminal display.

https://github.com/bernie-skipole/indipyterm

https://pypi.org/project/indipyterm/

## indipyconsole

Another INDI terminal client, connects to an INDI port and presents a terminal display. This gives a cruder output, and only runs on Linux. However it has no dependencies, and if the source code is copied the package could be run (with the -m option) without a virtual environment.

https://github.com/bernie-skipole/indipyconsole

https://pypi.org/project/indipyconsole/


Note many of the examples given here have Inline script metadata defining\
their dependencies, and so if copied to your own machine, and if you have\
a tool such as uv, which will automatically pull in dependencies, you\
should be able to very simply run the scripts with:

uv run examplescript.py

and you could run a terminal to connect to the created INDI service with:

uvx indipyterm

If you are running any of the driver scripts on a remote machine, and are connecting across a network, you will have to include host="0.0.0.0" in the IPyServer arguments, otherwise connection will be limited to the default 'localhost'.

#### blobs

Examples transmitting and receiving BLOBs

blobqueclient.py Client script using queclient receiving BLOBs\
getblob.py Driver to receive and save a BLOB file\
multiblobs.py Driver receiving vector with multiple blob members\
sendbigblob.py Driver sending a given file at regular intervals\
sendblob.py Driver creating and sending blocks of measurements at regular intervals\
snoopremote.py Driver snooping on remote running sendblob.py

#### deletingvectors

Examples of vectors being deleted and re-enabled

switches.py Driver with three switch vectors, with two RO vectors having switches counting\
and after 5 seconds the vectors are deleted, after another 5 seconds re-enabled.\
Clients should see the two dissapearing and reappearing.\
One RO vector shares a group with another WO vector, so clients should see that group and vector remaining\
The other RO vector is in its own group, so that group dissapears with the vector.


#### docexamples

The examples used in indipydriver readthedocs documentation

addexdriver.py IPyServer serving executable third part drivers.\
clientevent.py  client illustrating create_clientevent.\
example1.py A driver sending simulated temperature values every 10 seconds.\
example2.py Simulated thermostat with settable target.\
example3.py Window control snooping on thermostat.\
example4.py Illustrating delegation to Device objects.\
led.py Raspberry Pi LED driver.\
printmembers.py client printing vectorname, membername and value.\
queclient.py uses queclient in one thread, prints received temperature on request in main thread.\
temperatureclient.py client printing temperature as it is received.

#### gui

Example GUI clients

ledclient1.py example tkinter gui connecting to the server created by simulated\_led.py\
ledclient2.py example pygtk3 gui connecting to the server created by simulated\_led.py\
ledclient3.py example Dear PyGui client connecting to the server created by simulated\_led.py\
ledclient4.py example textual terminal which connects to the server created by simulated\_led.py\
simulated\_led.py simulated LED driver.\
webterm.py serving indipyterm via a web service so visible in a browser, a textual feature

The following two examples require a Valkey server to be running.

vkclient.py This client uses QueClient to get data which it saves it to a Valkey server\
This could be useful for a display, or multiple displays continuously showing updating values.

vkprint.py Illustrates how INDI parameters stored in a Valkey server using vkclient.py\
can be read. This could be used by a 'display' service to show an instruments output.

#### indipyweb

Examples working with indipyweb

singlescript.py Running drivers,server and serving as web pages in one script.\
getjson.py Every 10 seconds this example calls an indipyweb service running on\
a remote device which is serving a Thermostat, and prints the temperature.\
sshtunnel - doc describing an SSH tunnel used to encrypt the client-server connection.

#### invalid

Duplicate devicenames are not allowed, these tests check if they are detected

duplicatedevice1.py Two drivers, both with the same devicename\
led1.py As simulated\_led.py but set to listen on port 7625 and with devicename led\
led2.py As simulated\_led.py but set to listen on port 7626 and with devicename led

serve\_remotes.py Connects to two remote servers led1.py and led2.py\
Rather than using remote machines, these services are all on one\
machine using different ports. The duplicate names on the remote connections\
should be detected and cause the calling server to shutdown

#### lights

Examples sending lights

bincount.py Driver sending a vector with four lights binary counting

#### messages

bincount\_message.py As bincount.py with an additional messages\
only\_message.py Server with no drivers, but sending a message every two seconds.

#### multidevices

Serving multiple drivers and devices

deletingdevices.py - two devices one repeatedly deleting and reappearing\
lateswitch.py - two devices one inititially disabled, then becomes enabled.\
many.py - multiple drivers and devices\
multi\_led.py - driver controlling three LEDs

#### numbers

Examples transmitting and receiving numbers

counter.py Driver transmitting incrementing integers, and receiving floats.

#### remotes

led1.py As simulated\_led.py but set to listen on port 7625 and with devicename led1

led2.py As simulated\_led.py but set to listen on port 7626 and with devicename led2

sendblob.py As blobs/sendblob.py but set to listen on port 7627

serve\_remotes.py Connects to remote servers led1.py, led2.py and sendblob.py\
Rather than using remote machines, these services are all on\
one machine using different ports.

serve\_with\_logging.py This adds logging, so a logfile is created, for the remote link to led1

thirdpartyremote.py Connect to third party 'indiserver' process

#### snapshot

Testing the use of the client snapshot with a threaded function.

simpledriver.py Driver prints and sends an incrementing number\
and receives and prints a number.

threadedclient.py Client which receives a number, takes a snapshot of\
the client state and passes that to a threaded blocking function which\
manipulates the number and sends it back to the driver.

vectorjson.py client which creates and prints a json dump of the received vector

#### switches

Examples transmitting and receiving switch information

anyofmany.py Driver with one vector and multiple anyofmany switches
switches.py Several SwitchVectors illustrating switch rules\
OneOfMany AtMostOne AnyOfMany and ReadOnly

#### text

Examples transmitting and receiving text

rwtext.py TextVector with ten members, reading and writing\
Together with another vector controlling a longer 15 second task\
txrxtext.py Driver transmitting text vector with multiple members
