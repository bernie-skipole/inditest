# inditest
Contains example and test scripts for indipydriver and indipyclient

See

https://github.com/bernie-skipole/indipydriver

https://github.com/bernie-skipole/indipyclient

#### docexamples
The examples used in indipydriver readthedocs documentation

led.py Raspberry Pi LED driver.\
example1.py Simulated thermostat driver.\
example2.py Simulated thermostatwith settable target.\
example3.py Window control snooping on thermostat.\
addexdriver.py IPyServer serving executable third part drivers.\
temperatureclient.py client printing temperature as it is received.\
driverclient.py combining console client and driver in one script.

#### snapshot
Testing the use of the client snapshot with a threaded function.

simpledriver.py Driver prints and sends an incrementing number\
and receives and prints a number

threadedclient.py Client which receives a number, takes a snapshot of\
the client state and passes that to a threaded blocking function which\
manipulates the number and sends it back to the driver.

#### blobs

Examples transmitting and receiving BLOBs

sendblob.py Driver sending short files of measurements at regular intervals\
getblob.py Driver to receive and save a BLOB file\
multiblobs.py Driver receiving vector with up to three blob members\
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
