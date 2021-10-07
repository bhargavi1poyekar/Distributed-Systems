import rpyc
from datetime import datetime
import numpy
import pandas as pd
import threading
import time

lock = threading.Lock()


def read_carsid():
    carsid = pd.read_excel('Carsid.xlsx', engine='openpyxl')
    return carsid


def update_carsid(carsid):
    carsid.to_excel("Carsid.xlsx")


def read_bookings():
    bookings = pd.read_excel('Bookings.xlsx', engine='openpyxl')
    return bookings


def update_bookings(bookings):
    bookings.to_excel("Bookings.xlsx")


def check_cars():
    cars = pd.read_excel('Cars.xlsx', engine='openpyxl')
    return cars


def update_cars(cars):
    cars.to_excel("Cars.xlsx")


class Car(rpyc.Service):

    def __init__(self):
        pass

    def exposed_checkAvail(self, name):
        lock.acquire()
        print(f'{datetime.now():%H:%M:%S} - {rpyc.Service} acquired the lock \n')
        print(f'{datetime.now():%H:%M:%S} - {name} checking availability of cars\n')
        cars = check_cars()
        carlist = cars.loc[0:, ['CarName', 'Available']]
        lock.release()
        print(f'{datetime.now():%H:%M:%S} - {rpyc.Service} released the lock\n')
        return carlist

    def exposed_addCar(self, name, carname, nocar):
        lock.acquire()
        print(f'{datetime.now():%H:%M:%S} - {rpyc.Service} acquired the lock \n')
        cars = check_cars()
        carsid = read_carsid()
        index = cars.index[(cars['CarName'] == carname)].tolist()
        if(len(index) == 0):
            cars.loc[cars.shape[0]] = [cars.shape[0], carname, 0, nocar, nocar]
        else:
            idx = index[0]
            cars.at[idx, 'Available'] += nocar
            cars.at[idx, 'Total'] += nocar
        cars = cars[cars.filter(regex='^(?!Unnamed)').columns]

        update_cars(cars)

        for i in range(nocar):
            lastid = int(carsid.at[0, 'Carid'])
            carind = 'c'+str(lastid+1)
            carsid.at[0, 'Carid'] = lastid+1
            carsid.loc[carsid.shape[0]] = [
                carsid.shape[0], carind, carname, 'A']
        carsid = carsid[carsid.filter(regex='^(?!Unnamed)').columns]
        update_carsid(carsid)
        print(f'{datetime.now():%H:%M:%S} - {name} added {nocar} of {carname} \n')
        lock.release()
        print(f'{datetime.now():%H:%M:%S} - {rpyc.Service} released the lock\n')
        return

    def exposed_check_idwise_cars(self, name):
        lock.acquire()
        print(f'{datetime.now():%H:%M:%S} - {rpyc.Service} acquired the lock \n')
        print(f'{datetime.now():%H:%M:%S} - {name} wants to remove car\n')
        carsid = read_carsid()
        carsid = carsid[carsid.filter(regex='^(?!Unnamed)').columns]
        lock.release()
        print(f'{datetime.now():%H:%M:%S} - {rpyc.Service} released the lock\n')
        return carsid

    def exposed_removeCar(self, name, cid):
        lock.acquire()
        print(f'{datetime.now():%H:%M:%S} - {rpyc.Service} acquired the lock \n')
        cars = check_cars()
        carsid = read_carsid()
        trans = numpy.array(carsid).T
        trans = trans.tolist()
        carid = trans[1].index(cid)
        carstatus = carsid.at[carid, 'Status']
        if carstatus == 'A':
            carname = carsid.at[carid, 'CarName']
            carsid = carsid.drop(labels=carid, axis=0)
            index = cars.index[(cars['CarName'] == carname)].tolist()
            idx = index[0]
            cars.at[idx, 'Available'] -= 1
            cars.at[idx, 'Total'] -= 1
            cars = cars[cars.filter(regex='^(?!Unnamed)').columns]
            carsid = carsid[carsid.filter(regex='^(?!Unnamed)').columns]
            update_cars(cars)
            update_carsid(carsid)
            print(f'{datetime.now():%H:%M:%S} - {name} removed {carname} id {cid} \n')
            lock.release()
            print(f'{datetime.now():%H:%M:%S} - {rpyc.Service} released the lock\n')
            return carsid
        lock.release()
        print(f'{datetime.now():%H:%M:%S} - {rpyc.Service} released the lock\n')
        return

    def exposed_checkStatus(self, name, carname):
        lock.acquire()
        print(f'{datetime.now():%H:%M:%S} - {rpyc.Service} acquired the lock \n')
        print(f'{datetime.now():%H:%M:%S} - {name} wants to book car\n')
        cars = check_cars()
        index = cars.index[(cars['CarName'] == carname)].tolist()
        if len(index) > 0:
            avail = cars.at[index[0], 'Available']
            if(avail >= 0):
                lock.release()
                print(
                    f'{datetime.now():%H:%M:%S} - {rpyc.Service} released the lock\n')
                return 1
        lock.release()
        print(f'{datetime.now():%H:%M:%S} - {rpyc.Service} released the lock\n')
        return 0

    def exposed_bookCar(self, name, carname, src, dest):
        lock.acquire()
        print(f'{datetime.now():%H:%M:%S} - {rpyc.Service} acquired the lock \n')
        carsid = read_carsid()
        carid = carsid.index[(carsid['CarName'] == carname)].tolist()
        for i in range(len(carid)):
            if carsid.at[carid[i], 'Status'] == 'A':
                carsid.at[carid[i], 'Status'] = 'B'
                cid = carsid.at[carid[i], 'Carid']
                break
        cars = check_cars()
        car = cars.index[(cars['CarName'] == carname)].tolist()
        car = car[0]
        cars.at[car, 'Booked'] += 1
        cars.at[car, 'Available'] -= 1
        cars = cars[cars.filter(regex='^(?!Unnamed)').columns]
        carsid = carsid[carsid.filter(regex='^(?!Unnamed)').columns]
        update_cars(cars)
        update_carsid(carsid)
        bookings = read_bookings()
        bookings.loc[bookings.shape[0]] = [
            bookings.shape[0], name, cid, carname, 'G', src, dest]
        update_cars(cars)
        update_carsid(carsid)
        update_bookings(bookings)
        lock.release()
        print(f'{datetime.now():%H:%M:%S} - {rpyc.Service} released the lock\n')
        return cid
