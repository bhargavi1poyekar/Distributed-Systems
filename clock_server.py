from functools import reduce
from dateutil import parser
import threading
import datetime
import socket
import time
import win32api

# data structure used to store client address and clock data
client_data = {}

# function used to initiate the Clock Server / Master Node
def startClockServer(port = 10005):
    master_server = socket.socket()
    master_server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
    print("Socket at master node created successfully\n")
    master_server.bind(('', port))

    # Start listening to requests
    master_server.listen(10)
    print("Clock server started...\n")

    # start making connections
    print("Starting to make connections...\n")
    master_thread = threading.Thread(target = connectToSlave, args = (master_server, ))
    master_thread.start()

    # start synchronization
    print("Starting synchronization parallelly...\n")
    sync_thread = threading.Thread(target = synchronizeSlaves, args = ())
    sync_thread.start()

''' nested thread function used to receive clock time from a connected client '''
def receiveClockTime(connector, address):
    while True:
        clock_time_string = connector.recv(1024).decode()
        clock_time = parser.parse(clock_time_string)
        print(f'Time received from slave with address {str(address)}:{clock_time_string}\n\n')
        clock_time_diff = datetime.datetime.now() - clock_time
        client_data[address] = {"clock_time": clock_time,"time_difference": clock_time_diff,"connector": connector}
        time.sleep(60)

def connectToSlave(master_server):
    # fetch clock time at slaves / clients
    while True:
        # accepting a client / slave clock client
        master_slave_connector, addr = master_server.accept()
        slave_address = str(addr[0]) + ":" + str(addr[1])
        print(slave_address + " got connected successfully")
        current_thread = threading.Thread(target = receiveClockTime, args = (master_slave_connector, slave_address, ))
        current_thread.start()

# subroutine function used to fetch average clock difference
def calculateAvgClockDifference():
    current_client_data = client_data.copy()
    time_difference_list = list(client['time_difference'] for client_addr, client in client_data.items())
    sum_of_clock_difference = sum(time_difference_list,datetime.timedelta(0, 0))
    average_clock_difference = sum_of_clock_difference /(len(client_data)+1) # +1 for clock_server
    return average_clock_difference

''' master sync thread function used to generate cycles of clock synchronization in the network '''
def synchronizeSlaves():
    while True:
        print("\n ========================== New synchroniztion cycle started ========================== \n")
        print("\nNumber of slaves to be synchronized: " + str(len(client_data)))
        if len(client_data) > 0:
            average_clock_difference = calculateAvgClockDifference()
            print(f'Average-{average_clock_difference}\n')
            print(f'Day: {average_clock_difference.days}\n')
            for client_addr, client in client_data.items():
                try:
                    synchronized_time = datetime.datetime.now()
                    if average_clock_difference.days < 0:
                        synchronized_time = datetime.datetime.now() + abs(average_clock_difference)
                        
                    else:
                        synchronized_time = datetime.datetime.now() - average_clock_difference
                        client['connector'].send(str(synchronized_time).encode())
                        print("\nSynchronized time at the slave is: " + str(synchronized_time))
                except Exception as e:
                    print("\nSomething went wrong while sending synchronized time through " + str(client_addr))
                    print("\nsynchronized_time: ",synchronized_time)
                    

            time.sleep(60)
        else :
            print("No slave data. Synchronization not applicable.")
            print("\n\n")
            time.sleep(60)

# Driver function
if __name__ == '__main__':
    # Trigger the Clock Server
    startClockServer(port = 10005)



