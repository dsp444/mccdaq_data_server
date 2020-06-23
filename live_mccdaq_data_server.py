#!/usr/bin/env python
#
# Script to send data collected from a MCC DAQHAT 118 on a Raspberry Pi over
# TCP port for remote access
#
# Best way to run the script is in background mode with nohup so that
# you can log off of the Rasberry Pi after kicking it off.  For example:
# > nohup python -u ./live_mccdaq_data_server.py &
#
# Version 1.0 Dan Puperi      04/01/2020
#
# Must have the daqhats library installed
import socket, threading, sys
from daqhats import mcc118
from multiprocessing import Queue
from time import sleep

# Set up the host and port
# Set up the host, port, and file that contains data to be sent
# The host IP address will be the INTERNAL IP address of the computer (eg 192.168.X.X)
# The port can be any TCP port, preferably an unused 5 digit port - you will have to open
# the port and forward to the Rsapberry Pi IP address on yoru router
# The file name is a .csv file located in your the same directory as this script.
# The file just needs a column of real number data that matches the length of the message
# length the Raspberry Pi is sending (MSGLEN constant)
# 
HOST = '192.168.X.X'
PORT = XXXX

# Set up the MCC DAQ channel to use.  This script works in 'differential mode', so must
# provide 2 channels.  MCCDAQ_CHANNEL_0 is the signal; MCCDAQ_CHANNEL_G is the reference
# You can hook this to ground on the MCCDAQ if that is the intent.
MCCDAQ_CHANNEL_0 = 0
MCCDAQ_CHANNEL_G = 1

# Set the speed at which to send data to the clients
SPEED = 400.0      #  Hz

# Set the number of bytes to send at a time in each message
MSGLEN = 16

# SocketServer class does the work in listening for connections over the 
# host and port.  It also spawns off a separate thread to send the data
# to all the clients which have connected
class SocketServer:

# Init function runs when class is instantiated.  Connects to the queue object
# that the data is being written to.  Sets up a blank list of connected clients and
# initializes to start listening.
    def __init__( self, queue ):
        self.queue = queue
        self.CLIENTS = []
        self.listening = True

# Start server is the function that is kicked off into its own thread and starts
# listening for connections
    def startServer( self ):

# Start a thread that will continuously read data from the queue and send it to all
# listening clients
        self.dataserverThread = threading.Thread( target=self.sendData )
        self.dataserverThread.start()

# Open a socket and start listening for connections
        self.socket = socket.socket()
        print( 'Trying to start server')
        started = False
        while not started:
            try:
                self.socket.bind( (HOST, PORT) )
                started = True
            except OSError as err:
                print( 'Address is in use.  Will try again in 5 seconds')
                sleep( 5 )
        self.socket.listen( 1 )
        print( 'Listening for connections' )

# Listen until the listening flag is set to false.  When a connection happens,
# print a message and append the new client to the list of clients.
        while self.listening:
            conn, addr = self.socket.accept()
            conn.setblocking(0)
            print( 'Connected with ' + addr[0] )
            self.CLIENTS.append( (conn,addr) )
        self.socket.close()
        self.dataserverThread.join()

# Function to cause the socket server to stop listening for new connections and close the socket.
    def stop( self ):
        self.listening = False

# Function to read data from the queue and send it to each client.  Repeat this as long as the socket
# is listening.  Send data every only at certain intervales so that there is some sense of time being kept.
# and client can plot data with respect to time.  (sleep function accomplishes this)
    def sendData( self ):
        while self.listening:

# If nothing in the queue, just send 0.0 as the message
            try:
                msg = float(self.queue.get( True ))
            except:
                msg = 0.0

# The message is formatted as a string with the length defined by MSGLEN. There is room for
# a negative sign and two digits (10s and 1s) before the decimal point. The rest of the data is
# to the right of the decimal point. The string will be padded with zeros to both the left and 
# right so that the message sent to clients is a consistent length.
            msg = '{0:0{width}.{decimals}f}'.format( msg, width=MSGLEN, decimals=(MSGLEN-4) )

# Send the data to each client - if get an error from clients, just kick them out of the list so
# as not to mess up the other clients
            for (client,address) in self.CLIENTS:
                try:
                    ret = client.send( msg.encode( 'utf-8' ) )
                    if ret < MSGLEN:
                        raise RuntimeError( "socket connection broken" )
                except ( BrokenPipeError, ConnectionResetError, TimeoutError  ) as err:
                    self.CLIENTS.remove( (client,address) )
                    print( 'Disconnected with ' + address[0] )
                    print( err )
                except:
                    self.CLIENTS.remove( (client,address) )
                    err = sys.exc_info()[0]
                    print( 'New error from client ' + address[0] )
                    print( err )
            sleep( 1/SPEED )
        

# The MCCDAQ_DataServer class is what sets everything up and spawns the two main threads:
# 1) the SocketServer thread
# 2) the thread that collects data from the MCCDAQ and puts in the Queue
class MCCDAQ_DataServer:

# Run when class is instantiated.  Set up queue, the MCCDAQ hat and the SocketServer
# Then start running everything
    def __init__( self ):
        self.queue = Queue()
        self.running = True
        self.a0 = 0
        self.hat = mcc118( 0 )
        self.server = SocketServer( self.queue )
        self.start()
        self.putDataInQueue()

# Starts running the threads to collect data and listen for clients
    def start( self ):
        self.running = True
        self.dataThread = threading.Thread( target=self.run )
        self.dataThread.start()
        self.serverThread = threading.Thread( target=self.server.startServer )
        self.serverThread.start()

# Stops the socket server and shuts down everything nicely
    def stop( self ):
        self.running = False
        self.serverThread.stop()
        self.serverThread.join()
        self.dataThread.join()

# Collects data from the MCC DAQ hat
    def run( self ):
        while self.running:
            a0 = self.hat.a_in_read( MCCDAQ_CHANNEL_0 )
            a1 = self.hat.a_in_read( MCCDAQ_CHANNEL_G )
            self.a0 = a0-a1


# Takes the data from the MCC DAQ hat and places it in the queue at certain intervals
    def putDataInQueue( self ):
        while self.running:
            sleep( 1/SPEED )
            self.queue.put( self.a0, True )

# Entry point into the program.  All this does is create and instance of the MCCDAQ_DataServer
if __name__ == '__main__':
    server_app = MCCDAQ_DataServer()
