# inditest
Contains example and test scripts for indipydriver

See

https://github.com/bernie-skipole/indipydriver


Note these examples have Inline script metadata defining their\
dependencies, and so if copied to your own machine, and if you\
have a tool such as uv, which will automatically pull in\
dependencies, you should be able to very simply run the scripts with:

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


#### docexamples

The examples used in indipydriver readthedocs documentation

addexdriver.py IPyServer serving executable third part drivers.\
consoleclient.py Script dedicated to a terminal connecting to a preset host and port\
driverclient.py combining console client and driver in one script.\
example1.py A driver sending simulated temperature values every 10 seconds.\
example2.py Simulated thermostat with settable target.\
example3.py Window control snooping on thermostat.\
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
simulated\_led.py simulated LED driver.

vkclient.py This client uses QueClient to get snapshots of data and saves it to a Valkey server\
This could be useful for a display, or multiple displays to continuously show updating values.

vkprint.py Illustrates how INDI parameters stored in a Valkey server using vkclient.py\
can be read. This could be used by a 'display' service to show an instruments output.

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

rwtext.py Driver with ten rw members, also sends values every ten seconds\
txrxtext.py Driver transmitting text vector with multiple members
