import pytest
from queue import Queue

from Model import Transmit, action

def test_serialize_deserialize():
    # Check normal serialize and deserialize
    input_list = ["2620", "5", "0.123"]
    serialized = Transmit.serialize(input_list)
    deserialized = Transmit.deserialize(serialized)
    assert deserialized == input_list

def test_get_one_complete_message():
    # Check complete message
    msg = Transmit.serialize(["2620", "5", "0.123"])
    complete, rest = Transmit.get_one(msg)
    assert complete != b""
    assert rest == b""
    assert Transmit.deserialize(complete) == ["2620", "5", "0.123"]

def test_get_one_incomplete_message():
    # check incomplete messages are in rest
    incomplete = b"\n2620 5 0.123"
    complete, rest = Transmit.get_one(incomplete)
    assert complete == b""
    assert rest == incomplete

def test_get_one_invalid_initial_byte():
    # Input that does not start with a newline raises exception
    with pytest.raises(Exception, match="Invalid Initial Byte"):
        Transmit.get_one(b"2620 5 0.123\n")

def test_action():
    
    qself = Queue()
    q1 = Queue()
    q2 = Queue()    

    # Confirm read message if it exists, and logical time updates properly
    qself.put(("2620 10 test").encode("utf-8"))
    assert action(10, 100, qself, 1, q1, q2, 2621) == (-1, 101, 0)
    assert q1.empty()
    assert q2.empty()
    qself.put(("2620 200 test").encode("utf-8"))
    assert action(10, 100, qself, 1, q1, q2, 2621) == (-1, 201, 0)
    assert q1.empty()
    assert q2.empty()

    # Confirm command = 1 updates q1
    assert action(1, 100, qself, 0, q1, q2, 2621) == (1, 101, 0)
    assert not q1.empty()
    assert q2.empty()
    assert Transmit.deserialize(q1.get())[1] == str(100)

    # Confirm command = 2 updates q2
    assert action(2, 100, qself, 0, q1, q2, 2621) == (2, 101, 0)
    assert q1.empty()
    assert not q2.empty()
    assert Transmit.deserialize(q2.get())[1] == str(100)

    # Confirm command = 3 updates q1 and q2
    assert action(3, 100, qself, 0, q1, q2, 2621) == (3, 101, 0)
    assert not q1.empty()
    assert not q2.empty()
    assert Transmit.deserialize(q1.get())[1] == str(100)
    assert Transmit.deserialize(q2.get())[1] == str(100)

    # Confirm command >= 4 is internal
    assert action(4, 100, qself, 0, q1, q2, 2621) == (4, 101, 0)
    assert q1.empty()
    assert q2.empty()
    assert action(100, 100, qself, 0, q1, q2, 2621) == (100, 101, 0)
    assert q1.empty()
    assert q2.empty()