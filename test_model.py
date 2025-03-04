import math
import selectors
import socket
import time
import pytest
from Model import model 

# Dummy implementations to simulate socket and selector behavior.
class DummySocket:
    def __init__(self, *args, **kwargs):
        pass
    def setsockopt(self, *args, **kwargs):
        pass
    def bind(self, address):
        pass
    def listen(self, backlog):
        pass
    def setblocking(self, flag):
        pass
    def accept(self):
        # Simulate accepting a connection.
        return (DummySocket(), ('127.0.0.1', 5001))
    def connect(self, address):
        pass
    def sendall(self, message):
        pass
    def recv(self, bufsize):
        # Return empty bytes to simulate no data.
        return b""
    def close(self):
        pass

class DummySelector:
    def __init__(self):
        self.registered = []
    def register(self, fileobj, events, data):
        key = type("DummyKey", (), {})()
        key.fileobj = fileobj
        key.events = events
        key.data = data
        self.registered.append(key)
        return key
    def select(self, timeout=None):
        # Return an empty list (no events) to simplify the test.
        return []
    def unregister(self, fileobj):
        pass
    def close(self):
        pass

# A dummy time generator to simulate time progression.
class DummyTime:
    def __init__(self, start=0):
        self.current = start
    def perf_counter(self):
        # Increment time on each call.
        self.current += 1
        return self.current

@pytest.fixture(autouse=True)
def patch_external(monkeypatch, tmp_path):
    # Patch socket.socket to return a dummy socket.
    monkeypatch.setattr(socket, "socket", lambda *args, **kwargs: DummySocket())
    # Patch selectors.DefaultSelector to return a dummy selector.
    monkeypatch.setattr(selectors, "DefaultSelector", lambda: DummySelector())
    # Patch time.sleep to do nothing.
    monkeypatch.setattr(time, "sleep", lambda x: None)
    # Patch time.perf_counter using our dummy time.
    dummy_time = DummyTime(start=0)
    monkeypatch.setattr(time, "perf_counter", dummy_time.perf_counter)
    # Redirect file I/O for logs to a temporary file.
    log_dir = tmp_path / "Model_Logs"
    log_dir.mkdir()
    monkeypatch.setattr("builtins.open", lambda filename, mode: open(log_dir / filename.split("_")[-1], mode))

def test_model_runs_and_creates_log(tmp_path):
    # Run the model with dummy host/ports. The patched time.perf_counter will ensure the loop exits quickly.
    # Since our dummy time increments by 1 each call, eventually time.perf_counter() - start_time > RUN_TIME.
    model("127.0.0.1", 5000, [5001, 5002])
    
    # Verify that the log file was created.
    log_file = tmp_path / "Model_Logs" / "Log_5000.txt"
    assert log_file.exists()
    # Optionally, verify that some log lines were written.
    with open(log_file, "r") as f:
        content = f.read()
        assert "COMMAND" in content  # Check for the header line.
