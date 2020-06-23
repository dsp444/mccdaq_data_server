#!/usr/bin/env python
#
# Script to collected from a MCC DAQHAT 118 on a Raspberry Pi and write to a local file
# Used in conjuction with file_mcc_data_server.py which then can send data from this file
# over the internet.
#
# Version 1.0 Dan Puperi      04/01/2020
#
# Must have the daqhats library installed
from daqhats import mcc118
import time, numpy, os

# Define the channel to read from and output file name
# Set up the MCC DAQ channel to use.  This script works in 'differential mode', so must
# provide 2 channels.  MCCDAQ_CHANNEL_0 is the signal; MCCDAQ_CHANNEL_G is the reference
# You can hook this to ground on the MCCDAQ if that is the intent.
MCCDAQ_CHANNEL_0 = 0
MCCDAQ_CHANNEL_G = 1
OUTPUT_FNAME = 'output_data.csv'

# Set the speed at which to read/write data to the file
SPEED = 400      # Hz

# Set the total time to collect data
HOW_LONG = 20     # sec

# Delay makes sure data at the start is good...just give it a little bit of delay to start
DELAY = 2.0      # sec

# How many of most recent measurements to use for speed correction
CORR_MEASUREMENTS = 50

# Entry point into the program.  Not much complicated about this script other than a list of commands
if __name__ == '__main__':
    hat = mcc118( 0 )

# Want to find the average length of time it takes to read data and write to the disk, so that
# we can have data as close to possible at the desired speed.
    print( 'Computing delay...' )
    delays = []
    starttime = time.time()
    for i in range( 0,CORR_MEASUREMENTS ):
        st = 0
        et = 0
        with open( 'test_file.csv', 'w' ) as testfile:
            st = time.time()
            a0 = hat.a_in_read( MCCDAQ_CHANNEL_0 )
            a1 = hat.a_in_read( MCCDAQ_CHANNEL_G )
            testfile.write( '%s,%18.16f\n' % (st-starttime, a0-a1) )
            time.sleep( 1.0/SPEED )
            et = time.time()
#     The first time will be a little slow so we don't want to include that
        if i != 0: 
            delays.append( et-st )

# Remove the test file and calculate a speed correction based on the average of those trials
    os.remove( 'test_file.csv' )
    average = numpy.mean(delays)
    desired = 1.0/SPEED
    speed_correction = average-desired


# Now read the data from the MCC DAQ and write it to the file
    print( 'Measuring for %d seconds.' % HOW_LONG)
    starttime = time.time()
    elapsed_time = 0.0
    with open( OUTPUT_FNAME, 'w' ) as output_file:
        while elapsed_time < ( HOW_LONG + DELAY ):
            st = time.time()
            a0 = hat.a_in_read( MCCDAQ_CHANNEL_0 )
            a1 = hat.a_in_read( MCCDAQ_CHANNEL_G )
            elapsed_time = time.time() - starttime
            if elapsed_time > DELAY:
                output_file.write( '%s,%016.12f\n' % ( (elapsed_time-DELAY), a0-a1) )
                time.sleep( 1.0/SPEED - speed_correction )