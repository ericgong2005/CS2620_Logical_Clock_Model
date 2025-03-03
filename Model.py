import sys
import socket
import selectors
from queue import Queue
import time

class SelectorData:
    def __init__(self):
        self.inbound : bytes = b""
        self.queue : Queue[str] = Queue()

def model(host : any, self_port : int, other_ports : list[int]):

    self_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self_socket.bind((host, self_port))
    self_socket.listen(5)
    print(f"Model on {self_port} listening on {(host, self_port)}")
    self_socket.setblocking(False)

    selector = selectors.DefaultSelector()
    selector.register(self_socket, selectors.EVENT_READ, data=None)

    # sleep for a while to get all models running
    time.sleep(1)

    print(f"Model on {self_port} connecting to others")

    other_keys = []

    for value in other_ports:
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        connection.connect((host, value))
        selector.register(connection, events, data = SelectorData())

    try:
        while True:
            events = selector.select(timeout=None)
            for key, mask in events:
                # Add new connection from new User Processes
                if key.data is None:
                    connection, address = key.fileobj.accept()
                    print(f"Model on {self_port} accepted connection from {address}")
                    connection.setblocking(False)
                    events = selectors.EVENT_READ | selectors.EVENT_WRITE
                    selector.register(connection, events, data=SelectorData())
                    other_keys.append(key)
                else:
                    cur_socket = key.fileobj

                    # Communications From Other to Current
                    if mask & selectors.EVENT_READ:
                        recieve = cur_socket.recv(1024)
                        if recieve:
                            key.data.inbound += recieve
                        else:
                            print(f"Process closing connection to {key.data.address}")
                            selector.unregister(cur_socket)
                            cur_socket.close()

                    # Communications From Current to Other
                    if mask & selectors.EVENT_WRITE:
                        pass
    except Exception as e:
        print(f"Model on {self_port} encountered error {e}")
    finally:
        print("Closing Model")
        selector.close()



if __name__ == "__main__":
    # Confirm validity of commandline arguments
    if len(sys.argv) != 5:
        print("Usage: python Model.py HOSTNAME SELF_PORT OTHER_PORT_1 OTHER_PORT_2")
        sys.exit(1)
    other = [int(port) for port in sys.argv[3:]]
    host, self_port = sys.argv[1], int(sys.argv[2])
    model(host, self_port, other)


