import sys

nextBytes = sys.stdin.buffer.read1(2)

while len(nextBytes) > 0:
    size = b''
    pos_e = nextBytes.find(b' ')
    if pos_e >= 0:
        if pos_e == 0:
            size += nextBytes[1:]
        nextByte = sys.stdin.buffer.read1(1)
        while nextByte != b"B":
            size += nextByte
            nextByte = sys.stdin.buffer.read1(1)
        num = int(size.decode())
        data = sys.stdin.buffer.read(num)
        sys.stdout.buffer.write(data)
        sys.stdout.buffer.flush()
    nextBytes = sys.stdin.buffer.read1(2)
