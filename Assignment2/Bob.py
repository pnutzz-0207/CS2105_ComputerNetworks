from zlib import crc32

import sys

from socket import *

def checkPacket(packet):
    if len(packet) == 0:
        return False, None, None, None
    else:
        try:
            split = packet.split(b'=', 3)
            seqNum = split[0]
            seqNumInt = int(seqNum.decode()) # Check if seqNum is corrupted, throws ValueError
            originalChecksum = split[1]
            messageByte = split[2]
            calculatedChecksum = crc32(messageByte)
            calculatedChecksum = str(calculatedChecksum).encode()
            isNotCorrupted = (originalChecksum == calculatedChecksum)
            return isNotCorrupted, seqNumInt, originalChecksum, messageByte 
        except IndexError:
            return False, None, None, None
        except ValueError:
            return False, None, None, None

def isNotDuplicate(seqNumInt, nextSeqNum):
    return seqNumInt == nextSeqNum

def isCloseMessage(msgByte):
    return msgByte == b'close'

def makePacket(nextAckNum):
    nextAckNumStr = str(nextAckNum)
    packet = nextAckNumStr + "=ACK"
    return packet.encode()

def main():
    serverPort = int(sys.argv[1])
    bobSocket = socket(AF_INET, SOCK_DGRAM)
    bobSocket.bind(('', serverPort))

    nextSeqNum = 1
    nextAckNum = 2
    fullMessage = ''

    while True:
        recvPacket, clientAddress = bobSocket.recvfrom(64)
        #print(b"Bob received: " + recvPacket)

        isNotCorrupted, seqNumInt, checksumByte, messageByte = checkPacket(recvPacket)
        packet = b''

        if isNotCorrupted:
            if messageByte == b'close':
                packet = makePacket(nextAckNum)
                bobSocket.sendto(packet, clientAddress)
                fullMessage = fullMessage.rstrip('\n')
                print(fullMessage)
                break
            elif isNotDuplicate(seqNumInt, nextSeqNum):
                packet = makePacket(nextAckNum)
                bobSocket.sendto(packet, clientAddress)
                message = messageByte.decode()
                fullMessage = fullMessage + message
                nextSeqNum += 1
                nextAckNum += 1
            else:
                packet = makePacket(nextAckNum - 1)
                bobSocket.sendto(packet, clientAddress)

        else:
            packet = makePacket(nextSeqNum)
            bobSocket.sendto(packet, clientAddress)

        #print(b'Bob sent: ' + packet)
    
    bobSocket.close()

if __name__ == '__main__':
    main()