import pytest
from Model import Transmit  

def test_serialize_deserialize():
    input_list = ["127.0.0.1", "5", "0.123"]
    serialized = Transmit.serialize(input_list)
    deserialized = Transmit.deserialize(serialized)
    assert deserialized == input_list

def test_get_one_complete_message():
    # Create a complete message as produced by serialize.
    msg = Transmit.serialize(["127.0.0.1", "5", "0.123"])
    complete, rest = Transmit.get_one(msg)
    # For a complete message, the rest should be empty.
    assert complete != b""
    assert rest == b""
    # Verify that deserializing the complete message returns the expected list.
    assert Transmit.deserialize(complete) == ["127.0.0.1", "5", "0.123"]

def test_get_one_incomplete_message():
    # Create an incomplete message (e.g., missing the ending newline).
    incomplete = b"\n127.0.0.1 5 0.123"
    complete, rest = Transmit.get_one(incomplete)
    # Since the message is incomplete, 'complete' should be empty and 'rest' should be unchanged.
    assert complete == b""
    assert rest == incomplete

def test_get_one_invalid_initial_byte():
    # Input that does not start with a newline should raise an Exception.
    with pytest.raises(Exception, match="Invalid Initial Byte"):
        Transmit.get_one(b"127.0.0.1 5 0.123\n")