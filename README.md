# mccdaq_data_server
A collection of python scripts to send data collected by a Measurement Computing MCC 118 DAQ HAT and Raspeberry Pi over a TCP port.

There are 4 related scripts included here - all of which can be run independetly.
1) live_mccdaq_data_server.py - this script reads data (in differential mode) from 2 inputs of the MCC 188 DAQ HAT and sends it in realtime to clients which are connected to the server
2) file_mccdaq_data_server.py - this script reads data from a file and sends the data one point at a time to clients which are connected to the server
3) mccdaq_client.py - a very simple script that connects to the a server, listens for data, and prints the data to the console.  Useful for testing the server.
4) mccdaq_data_writer.py - this script can be used to collect live data from the MCC DAQ and save it to a file so that it can be transmitted to clients using file_mccdaq_data_server.py
