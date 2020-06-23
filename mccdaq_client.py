#!/usr/bin/env python
# 
# This is a simple script to receive data over a TCP port.
# It just prints out the data to the console, but useful for
# testing.
#
# Version 1.0 Dan Puperi      04/01/2020
#
import socket

# Set up the client to match the server.
# The HOST can either be an internal IP address if you are on the same network (ex 192.168.X.X)
# or it can be a external address that the world can see.  If you have your router working
# correctly, either will work from inside your network.
# PORT is the port being used by the server - hopefully a unused TCP port number.
# MSGLEN should match the length of each message from the server.
#
HOST='some.company.com'
#HOST='192.168.X.X'
PORT=XXXXX
MSGLEN=16

# Open the socket and listen for data.
# Assumes that it is receiving floating point data.
s=socket.socket( socket.AF_INET, socket.SOCK_STREAM )
s.connect( (HOST,PORT) )
connected = True
while connected:
	data=s.recv(MSGLEN)
	if data:
	    print( float(data) )
	else:
		connected = False
s.close()
