import sys
import threading
import socket

# create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()

# host is binded to port to 10006 to listen all incoming requests
port = 10006
try:
    s.bind((host, port))
except socket.error as msg:
    print("bind failed" + str(msg))
    sys.exit()

#started listening to requests ,upto 10
s.listen(10)

''' Lists are created to store socket objects and processes ,whenever a new process is connected to 
the server,it's socket object is stored inprocess_sockets_list and process_list is used to store the 
id of the process.'''

process_sockets_list = []
process_list = []
neighbor_list = []
msg_token = ""

'''function to get the socket object as input parameters and receive messages from that process and send 
it to the next process along the ring.'''

def recv_message(conn):
    while True:
        # try the receive message from process till the message is received
        try:
            received = conn.recv(1024)
            msg_token = received.decode('utf-8')
            print("received token: " + msg_token)
        except:
            continue

        # if the received message has coordinator server
        if "Coordinator: " in msg_token :
            le=msg_token.split()
            leader=le[1]
        
        # storing the index of the process id .
        process_index = process_sockets_list.index(conn)
        
        '''if process sending the message is last in list then the next process is first process, 
        otherwise the next process as the processes are communicating in the ring'''

        if len(process_sockets_list)==process_index+1 :
            to_process=0
        else :
            to_process=process_index+1
        
        # try to send message to next process
        try :
            process_sockets_list[to_process].send(received)
            # redirecting the received message to next process in the ring
            print("sending :" + received.decode('utf-8'))

        # if unable to send the message that means the that process is stopped ,so its socket object and process ids are removed from the respective list.'''

        except :
            '''if the stopped process is not the coordinator then the message is
            redirected towards to the next process in the ring'''

            if process_list[to_process]!=leader :
                process_sockets_list[to_process+1].send(received)
                print("sending :" + received.decode('utf-8'))

            # closing the socket object of the stopped process.
            process_sockets_list[to_process].close()
            # removing the socket object from the list
            process_sockets_list.remove(process_sockets_list[to_process])
            # removing the process id from processes list.
            process_list.remove(process_list[to_process])
            continue

'''Server listens to all incoming connect requests and accepts them and
stores their socket object and fork a new thread for each connection'''
while True:
    # try connecting with client if any exception it throws exception
    try:
        connection, addr = s.accept()
        # appending the new connection's socket and storing it in process_sockets_list
        process_sockets_list.append(connection)
        # Now server receives the clients process_id
        recv_process_id = connection.recv(1024)
        from_to_process = recv_process_id.decode('utf-8')
        # server stores the process id in process_list
        process_list.append(from_to_process)
        print("Process: " + from_to_process)

        '''once server gets process id of the client server forks a new thread to
        client and to recv_message function and passes the connection object'''

        start_thread = threading.Thread(target=recv_message,args=(connection,))
        start_thread.start()
    
    #catches socket error if any and displays the message
    except socket.error as msg:
        print("thread failed"+msg)
    
#closing the connection after all operations are done.
connection.close()
s.close()




