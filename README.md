# inditest
Contains example and test scripts for indipydriver and indipyclient

#### docexamples
The examples used in indipydriver readthedocs documentation

led.py Raspberry Pi LED driver.\
example1.py Simulated thermostat driver.\
example2.py Simulated thermostatwith settable target.\
example3.py Window control snooping on thermostat.\
logled.py Raspberry Pi LED driver with debugging logs enabled.\
addexdriver.py IPyServer serving executable third part drivers.

#### snapshot
Testing the use of the client snapshot with a threaded function.

simpledriver.py Driver prints and sends an incrementing number\
and receives and prints a number

threadedclient.py Client which receives a number, takes a snapshot of\
the client state and passes that to a threaded blocking function which\
manipulates the number and sends it back to the driver.
