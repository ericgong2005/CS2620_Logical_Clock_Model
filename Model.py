import sys
import socket
import selectors
from queue import Queue
import time
import random
import math

RUN_TIME = 60
MAX_CLOCK_TICKS  = 6
MAX_EVENT_NUM = 10

class SelectorData:
    def __init__(self):
        self.inbound : bytes = b""
        self.outbound : Queue[bytes] = Queue()

class Transmit:
    @staticmethod
    def serialize(input: list[str]) -> bytes:
        return ("\n" + " ".join(input) + "\n").encode("utf-8")
    
    def deserialize(input: bytes) -> list[str]:
        return input.decode("utf-8").strip().split(" ")
    
    def get_one(input : bytes) -> tuple[bytes, bytes]:
        if not input or input == b"":
            return (b"",b"")
        if input[0] != ord("\n"):
            raise Exception("Invalid Initial Byte")
        split_point = input.find(b"\n\n")
        if split_point == -1:
            if input[-1] == ord(b"\n"):
                return (input, b"")
            else:
                return (b"", input)
        else:
            first = input[:split_point + 1]
            rest = input[split_point + 1:]
            return first, rest

def model(host : any, self_port : int, other_ports : list[int]):

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
    interval = 1/random.randint(1, MAX_CLOCK_TICKS)
    next_time = start_time + interval

    logical_clock = 0

    print(f"Process on {self_port} starts on {start_time:.3f} on interval {interval:.3f}")

    with open(f"Model_Logs/Log_{self_port}.txt", "w") as file:
        file.write("COMMAND\tLOGICAL_TIME\tTRUE_TIME\tQUEUE_SIZE\tSELF_PORT\tSELF_INTERVAL\n")

    while True:
        if time.perf_counter() - start_time > RUN_TIME:
            break
        elif time.perf_counter() > next_time:
            command = -1
            if queue_len != 0:
                queue_len -= 1
                current = Transmit.deserialize(inbound_queue.get())
                logical_clock = max(logical_clock, int(current[1])) + 1
            else:
                command = random.randint(1, MAX_EVENT_NUM)
                message = Transmit.serialize([str(self_port), str(logical_clock), str(time.perf_counter())])
                if command == 1 or command == 3:
                    other_keys[0].data.outbound.put(message)
                if command == 2 or command == 3:
                    other_keys[1].data.outbound.put(message)
                logical_clock += 1
            print(f"Process on {self_port} takes action {command} at {(time.perf_counter() - start_time):.5f}")
            with open(f"Model_Logs/Log_{self_port}.txt", "a") as file:
                file.write(f"{command if command < 4 else 4}\t{logical_clock}\t" + 
                           f"{time.perf_counter() - start_time}\t{queue_len}\t" + 
                           f"{self_port}\t{interval}\n")
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
    if len(sys.argv) != 5:
        print("Usage: python Model.py HOSTNAME SELF_PORT OTHER_PORT_1 OTHER_PORT_2")
        sys.exit(1)
    other = [int(port) for port in sys.argv[3:]]
    host, self_port = sys.argv[1], int(sys.argv[2])
    model(host, self_port, other)