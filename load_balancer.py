import pickle
import datetime

server_ports = [10001, 10002, 10003, 10004]
prev_request_count = 0
with open('request_count.pickle', 'wb') as handle:
    pickle.dump(prev_request_count, handle,protocol=pickle.HIGHEST_PROTOCOL)
current_port = 10001
with open('current_port.pickle', 'wb') as handle:
    pickle.dump(current_port, handle, protocol=pickle.HIGHEST_PROTOCOL)
while True:
    try:
        with open('request_count.pickle', 'rb') as handle:
            new_request_count = pickle.load(handle)
    except:
        continue
    if new_request_count > prev_request_count:
        current_port_index = server_ports.index(current_port)
        print(f'{datetime.datetime.now():%H:%M:%S} - Request served by Server{current_port_index + 1} on Port:- {current_port}')
        new_port_index = (current_port_index + 1) % 4
        new_port = server_ports[new_port_index]
        current_port = new_port
        prev_request_count = new_request_count
        with open('current_port.pickle', 'wb') as handle:
            pickle.dump(new_port, handle, protocol=pickle.HIGHEST_PROTOCOL)
