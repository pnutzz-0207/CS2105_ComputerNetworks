import zlib
import sys

path = sys.argv[1]

with open(path, "rb") as f:
    bytes = f.read()
    checksum = zlib.crc32(bytes)

print(checksum)