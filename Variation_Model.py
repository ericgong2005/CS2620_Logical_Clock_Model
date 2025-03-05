import sys
import socket
import selectors
from queue import Queue
import time
import random
import math
from pathlib import Path

from Model import SelectorData, Transmit, action

SPEED_UP = 60
RUN_TIME = 60

def model(host : any, self_port : int, other_ports : list[int], max_event_num, ticks, max_ticks):

    self_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self_socket.bind((host, self_port))
    self_socket.listen(5)
    print(f"Process on {self_port} listening on {(host, self_port)}")
    self_socket.setblocking(False)

    selector = selectors.DefaultSelector()
    selector.register(self_socket, selectors.EVENT_READ, data=None)

    # sleep for a while to get all processes running
    time.sleep(1)

    print(f"Process on {self_port} connecting to others")

    queue_len = 0
    inbound_queue = Queue()

    for value in other_ports:
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        connection.connect((host, value))
        selector.register(connection, events, data=SelectorData())
        
    other_keys = []

    start_time = math.ceil(time.perf_counter()) + 1
    interval = 1/ticks
    interval = interval/SPEED_UP
    next_time = start_time + interval

    logical_clock = 0

    print(f"Process on {self_port} starts on {start_time:.3f} on interval {interval:.3f}")

    file_path = Path(f"Variation_Logs/Trials/T{max_ticks}N{max_event_num}")

    with open((file_path / f"Log_{self_port}.txt"), "w") as file:
        file.write("COMMAND\tLOGICAL_TIME\tTRUE_TIME\tQUEUE_SIZE\tSELF_PORT\tSELF_INTERVAL\n")

    while True:
        if time.perf_counter() - start_time > RUN_TIME/SPEED_UP:
            break
        elif time.perf_counter() > next_time:
            command, logical_clock, queue_len = action(random.randint(1, max_event_num), logical_clock, 
                             inbound_queue, queue_len, 
                             other_keys[0].data.outbound, 
                             other_keys[1].data.outbound, 
                             self_port)
            print(f"Process on {self_port} takes action {command} at {((time.perf_counter() - start_time)*SPEED_UP):.5f}")
            with open((file_path / f"Log_{self_port}.txt"), "a") as file:
                file.write(f"{command if command < 4 else 4}\t{logical_clock}\t" + 
                           f"{(time.perf_counter() - start_time)*SPEED_UP}\t{queue_len}\t" + 
                           f"{self_port}\t{interval*SPEED_UP}\n")
            next_time += interval
            
        events = selector.select()
        for key, mask in events:
            # Add new connection from Other Process
            if key.data is None:
                connection, address = key.fileobj.accept()
                print(f"Process on {self_port} accepted connection from {address}")
                connection.setblocking(False)
                events = selectors.EVENT_READ | selectors.EVENT_WRITE
                new_key = selector.register(connection, events, data=SelectorData())
                other_keys.append(new_key)
            else:
                cur_socket = key.fileobj

                # Recieve Communications From Other to Current
                if mask & selectors.EVENT_READ:
                    recieve = cur_socket.recv(1024)
                    if recieve:
                        key.data.inbound += recieve
                        current, key.data.inbound = Transmit.get_one(key.data.inbound)
                        while current != b"":
                            inbound_queue.put(current)
                            queue_len += 1
                            current, key.data.inbound = Transmit.get_one(key.data.inbound)

                    else:
                        print(f"Process closing connection")
                        selector.unregister(cur_socket)
                        cur_socket.close()

                # Communications From Current to Other
                if mask & selectors.EVENT_WRITE:
                    if not key.data.outbound.empty():
                        message = key.data.outbound.get()
                        cur_socket.sendall(message)
    
    print(f"Closing Process on {self_port}")
    selector.close()



if __name__ == "__main__":
    # Confirm validity of commandline arguments
    if len(sys.argv) != 8:
        print("Usage: python Model.py HOSTNAME SELF_PORT OTHER_PORT_1 OTHER_PORT_2 EVENT_NUM TICKS MAX_TICKS")
        sys.exit(1)
    other = [int(port) for port in sys.argv[3:5]]
    host, self_port = sys.argv[1], int(sys.argv[2])
    model(host, self_port, other, int(sys.argv[5]), int(sys.argv[6]), int(sys.argv[7]))