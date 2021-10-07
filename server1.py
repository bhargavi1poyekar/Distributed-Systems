from rpyc.utils.server import ThreadedServer
from car_service import Car 
import pandas as pd
from timeit import default_timer as timer
from dateutil import parser
import threading
import datetime
import socket
import time
import random
import subprocess
import shlex
import pickle

#### START ELECTION ALGO CODE###

# Creating socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Retrieving host name
host = socket.gethostname()
# Port number of election server
to_port = 10006
# Connecting to election server
s.connect((host, to_port))
# ID of server
server_id = "10001"
# Sending the server id to the election server
s.send(server_id.encode('utf-8'))
# Initializing the leader variable (co-ordinator) to -1
leader="-1"

# Function for starting election algorithm
def initiate_election(s):
    # Sleep for adding delay in the algorithm
    time.sleep(1)
    # Sending the current server id as token
    s.send(server_id.encode('utf-8'))
    # Displaying the token sent and the message that election is initiated
    print("token sent: " + server_id)
    print("Election initiated")

# Function for implementing Ring Election Algorithm
def Ring_Election_Algorithm(s):
    while True:
        global leader
        try:
            # Timeout is set to 15 seconds. If the message is not received, election algorithm is started
            s.settimeout(15)
            received = s.recv(1024)
            s.settimeout(None)
            # Storing the message in received token list after decoding
            received_token_list = received.decode('utf-8')
        
        # Timeout exception
        except socket.timeout:
            leader = "0"
            # Initiating election algorithm
            initiate_election(s)
            continue

        # If current process had started the election and it received the active list with its id in it
        if server_id in received_token_list and "Coordinator: " not in received_token_list and "check" not in received_token_list:
            # finding the maximum token to elect the leader from the received_token_list
            # print(f'received_token_list: {received_token_list}')
            received_token_list_int = received_token_list.split()
            received_token_list_int = [int(x) for x in received_token_list_int]
            # Finding the id with maximum value and selecting it as leader
            leader = max(received_token_list_int)
            leader = str(leader)

            # Storing the port number of the coordinator
            shared = {"Port_Number": leader}
            with open('shared.pickle', 'wb') as handle:
                pickle.dump(shared, handle, protocol=pickle.HIGHEST_PROTOCOL)
            # fp = open("shared.pkl", "wb")
            # pickle.dump(shared, fp)
            # Passing the message declaring the coordinator to the other nodes in the ring
            forwarding_leader = "Coordinator: " + leader
            time.sleep(1)
            s.send(forwarding_leader.encode('utf-8'))
        
        # If current server id not in the list and it is not the co-ordinator declaration and check message
        elif server_id not in received_token_list and "Coordinator: " not in received_token_list and "check" not in received_token_list :
            print("rec tok: " + received_token_list)
            # Leader variable is set to 0 as coordinator is not yet decided
            leader = "0"
            # Adding the current server id to the list
            received_token_list = received_token_list + " " + server_id
            time.sleep(1)
            # Sending the updated list to next node
            s.send(received_token_list.encode('utf-8'))
            print("adding token: " + received_token_list)
        
        # If the current server is the newly created server
        elif ("check" in received_token_list or "Coordinator: " in received_token_list )and leader=="-1" :
            # The leader variable is set to 0 as this new server does not know the co-ordinator
            leader="0"
            # Initiating election
            initiate_election(s)
        
        # If the message is about informing coordinator but the leader's value is not changed
        elif "Coordinator: " in received_token_list and leader not in received_token_list :
            print(received_token_list)
            # Updating the value of the leader
            le=received_token_list.split()
            leader=le[1]
            time.sleep(1)
            # Sending the message to next node in the ring
            s.send(received_token_list.encode('utf-8'))

        # If the election procedure is going on
        else :
            if leader=="-1" or leader=="0":
                continue
            else :
                #print("coordinator mm :" + leader)
                print(received_token_list)
                # send a check message to the next process so that it understands it is coming from this process
                communicate = "check" + " from " + server_id
                # sleep the current thread to provide delay in the algorithm
                time.sleep(1)
                # send the message to the next process along the ring
                s.send(communicate.encode('utf-8'))
                continue

#### END ELECTION ALGO CODE###

#### START CLOCK SYNCHRONIZATION CODE###

# client thread function used to send time at client side
def sendClockTime(slave_client):
    while True:
        # provide server with clock time at the client
        slave_client.send(str(datetime.datetime.now()).encode())
        time.sleep(60)

# client thread function used to receive synchronized time
def receiveClockTime(slave_client):
    while True:
        # receive data from the server
        Synchronized_time = parser.parse(slave_client.recv(1024).decode())
        # time_string = datetime(*time_tuple).isoformat()
        time_string = str(Synchronized_time.month).zfill(2) + "-"+ str(Synchronized_time.day).zfill(2) + " "+str(Synchronized_time.hour).zfill(2) + "-"+str(Synchronized_time.minute).zfill(2) + "-"+str(Synchronized_time.second).zfill(2)
        print(f'\nSynchronized Time: {time_string}')

# function used to Synchronize client process time
def startSlave(port = 10005):
    slave_client = socket.socket()
    # connect to the clock server on local computer
    slave_client.connect(('localhost', port))
    # start sending time to server
    send_time_thread = threading.Thread(target = sendClockTime, args = (slave_client, ))
    send_time_thread.start()
    # start receiving synchronized from server
    receive_time_thread = threading.Thread(target = receiveClockTime, args = (slave_client, ))
    receive_time_thread.start()

#### END CLOCK SYNCHRONIZATION CODE###

if __name__ == "__main__":
    
    ### CLOCK ###
    # initialize the Slave / Client
    # startSlave(port = 10005)
    #############

    ### ELECTION ALGO ####
    # create a start a thread to implement ring election algorithm
    recv_thread = threading.Thread(target=Ring_Election_Algorithm, args=(s,))
    recv_thread.start()
    #####################
    
    server1=ThreadedServer(Car, port=10001)
    print("\n Server 1 started")
    server1.start()

 