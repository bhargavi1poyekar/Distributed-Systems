import rpyc
import random
from timeit import default_timer as timer
from dateutil import parser
import threading
import socket
import time
import datetime
import win32api
import config
import pickle

ports = [10001, 10002]
port = random.choice(ports)

# with open('shared.pickle', 'rb') as handle:
#     shared = pickle.load(handle)

# print(f'\n Coordinator: {shared["Port_Number"]}')
car = rpyc.connect('localhost', port)


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
        time_string = str(Synchronized_time.month).zfill(2) + "-" + str(Synchronized_time.day).zfill(2) + " "+str(
            Synchronized_time.hour).zfill(2) + "-"+str(Synchronized_time.minute).zfill(2) + "-"+str(Synchronized_time.second).zfill(2)
        print(f'\nSynchronized Time: {time_string}')

# function used to Synchronize client process time


def startSlave(port=10005):
    slave_client = socket.socket()
    # connect to the clock server on local computer
    slave_client.connect(('localhost', port))
    # start sending time to server
    send_time_thread = threading.Thread(
        target=sendClockTime, args=(slave_client, ))
    send_time_thread.start()
    # start receiving synchronized from server
    receive_time_thread = threading.Thread(
        target=receiveClockTime, args=(slave_client, ))
    receive_time_thread.start()

# initialize the Slave / Client
# startSlave(port = 10005)


name = input("\nEnter your name: ")
user = int(input("Are you customer(Press 1) or manager(Press 0)??"))
if user == 1:
    f1 = 1
    while(f1):
        ch = int(input(
            "\n Enter your choice:\n1. See Car Availability\n2. Book a Car\n3. Exit\n"))
        if ch == 1:
            carlist = car.root.checkAvail(name)
            print(carlist)
        elif ch == 2:
            carname = input("Enter the carname you want to book: ")
            stat = car.root.checkStatus(name, carname)
            if stat == 0:
                print("Car is not available for booking")
            else:
                src = input("Enter the source: ")
                dest = input("Enter the destination: ")
                cid = car.root.bookCar(name, carname, src, dest)
                print(f'Car {carname} with carid {cid} is booked successfully')
        else:
            f1 = 0
elif user == 0:
    f2 = 1
    while(f2):
        ch = int(input(
            "\n Enter your choice:\n1. See Car Availability\n2. Add a Car\n3. Remove Car \n4. Exit\n"))
        if ch == 1:
            carlist = car.root.checkAvail(name)
            print(carlist)
        elif ch == 2:
            carname = input("Enter car name to add\n")
            nocar = int(input("Enter no. of cars to add\n"))
            car.root.addCar(name, carname, nocar)
            print("You have succesfully added the cars\n")
        elif ch == 3:
            carsid = car.root.check_idwise_cars(name)
            print("Cars Present:\n")
            print(carsid)
            cid = input("Enter the car id of the car to be removed: ")
            carsid = car.root.removeCar(name, cid)
            if(isinstance(carsid, int)):
                print("Car is booked, cannot remove now, try later")
            else:
                print(carsid)
                print("You have succesfully removed the car\n")
        else:
            f2 = 0
else:
    print("Invalid choice.")
