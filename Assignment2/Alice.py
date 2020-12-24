from zlib import crc32

import sys

from socket import *

def getChecksum(msgByte):
    checksum = crc32(msgByte)
    return str(checksum)

def makePacket(seqNum, checksum, msgByte):
    seqNumStr = str(seqNum)
    packet = seqNumStr.encode() + b'=' + checksum.encode() + b'=' + msgByte
    return packet

def isNotCorrupted(packet, nextAckNum):
    try:
        split = packet.split(b'=', 2)
        ackNum = int(split[0].decode())
        return ackNum == nextAckNum
    except IndexError:
        return False
    except ValueError:
        return False

def printTestMsg(msg):
    message = msg.decode()
    sys.stdout.write('Alice sent: ' + message)

def main():
    serverName = 'localhost'
    serverPort = int(sys.argv[1])
    aliceSocket = socket(AF_INET, SOCK_DGRAM)

    nextSeqNum = 1
    nextAckNum = 2

    while True:
        # 16 bit for header and 48 bit for message
        nextMessage = sys.stdin.read(48)
        # nextMessage = nextMessage.rstrip('\n')
        #if '\r' in nextMessage:
            #nextMessage = nextMessage.replace('\r', '')
            #nextMessage = nextMessage.replace('\n', '')
        if nextMessage == '':
            #continue
            nextMessage = 'close'
        nextMessageByte = nextMessage.encode()
        nextChecksum = getChecksum(nextMessageByte) 
        nextPacket = makePacket(nextSeqNum, nextChecksum, nextMessageByte)
        #print(nextPacket)
        #print(sys.getsizeof(nextPacket))
        #if sys.getsizeof(nextPacket) > 64:
        #    continue
        # printTestMsg(nextPacket)

        waitingForAck = True
        while waitingForAck:
            try:
                aliceSocket.sendto(nextPacket, (serverName, serverPort))
                #print(b"Alice sent message: " + nextPacket)
                aliceSocket.settimeout(0.05)
                recvPacket, serverAddress = aliceSocket.recvfrom(64)
                #print(b"Alice received: " + recvPacket)
                # recvMsg is <ackNum>=ACK
                if (isNotCorrupted(recvPacket, nextAckNum)):
                    waitingForAck = False

            except timeout:
                #print("Timed out")
                continue
        
        nextSeqNum += 1
        nextAckNum += 1
            
    aliceSocket.close()

if __name__ == '__main__':
    main()

