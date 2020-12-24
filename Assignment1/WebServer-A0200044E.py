import sys
from socket import *

class Parser:
    def __init__(self):
        self.keyStore = KeyStore()
        self.counterStore = CounterStore()
        self.connectionSocket = None

    def connect(self, connectionSocket):
        self.connectionSocket = connectionSocket

    def parse(self, message):
        msgSplit = message.split(b' ', 2)
        method = msgSplit[0]
        method = method.decode().upper()
        path = msgSplit[1]
        #print(b'PATH' + path)
        contentLength = 0
        contentLengthByte = b'0'

        if msgSplit[2] != b'': # Body for POST requests
            body = msgSplit[2]
            bodySplit = body.split(b' ')
            #print(b'BODY:' + body)
            if len(bodySplit) > 3:
                j = len(bodySplit) - 1
                for i in range(len(bodySplit)):
                    if (bodySplit[j-i] == b'content-length'):
                        contentLengthByte = bodySplit[j-i+1]
                        contentLengthStr = contentLengthByte.decode('utf_8')
                        contentLength = int(contentLengthStr)
                        break
            else:
                contentLengthByte = bodySplit[1]
                contentLengthStr = contentLengthByte.decode('utf_8')
                contentLength = int(contentLengthStr)

        content = self.connectionSocket.recv(contentLength)
        #print(b'CONTENT:' + content)
        return self.getRequests(method, path, content, contentLengthByte)


    def getRequests(self, method, path, content, contentLength):
        key = path.split(b'/')[1]
        if key == b'key':
            return self.keyStore.getResponse(method, path, content, contentLength)
        else:
            return self.counterStore.getResponse(method, path)

class KeyStore:
    def __init__(self):
        self.keys = {}
    
    def getResponse(self, method, path, content, contentLength):
        if method == 'GET':
            return self.handleGet(path)
        elif method == 'POST':
            return self.handlePost(path, content, contentLength)
        else:
            return self.handleDelete(path)

    def handleGet(self, path):
        response = self.keys.get(path)
        if response == None:
            return b'404 NotFound  '
        else:
            return b"200 OK " + response

    def handlePost(self, path, content, contentLength):
        value = b"content-length " + contentLength + b"  " + content
        self.keys[path] = value
        return b"200 OK  "

    def handleDelete(self, path):
        response = self.keys.get(path)
        if response == None:
            return b"404 NotFound  "
        else:
            self.keys.pop(path)
            return b"200 OK " + response

class CounterStore:
    def __init__(self):
        self.counters = {}

    def getResponse(self, method, path):
        if method == 'GET':
            return self.handleGet(path)
        else:
            return self.handlePost(path)
    
    def handleGet(self, path):
        count = self.counters.get(path)
        if count == None:
            return b"200 OK content-length 1  0"
        else:
            countEncoded = str(count).encode()
            return b"200 OK content-length 1  " + countEncoded

    def handlePost(self, path):
        count = self.counters.get(path)
        if count == None:
            self.counters[path] = 1
        else:
            self.counters[path] = count + 1
        return b"200 OK  "

def main():
    parser = Parser()
    serverPort = int(sys.argv[1])

    serverSocket = socket(AF_INET, SOCK_STREAM)

    serverSocket.bind(('', serverPort))

    while True:
        serverSocket.listen(1)

        connectionSocket, clientAddr = serverSocket.accept()

        parser.connect(connectionSocket)

        msgByte = connectionSocket.recv(1)
        
        isPrevWhitespace = False
        message = b''
        while len(msgByte) > 0:
            if msgByte == b' ':  # When nextByte is whitespace
                if isPrevWhitespace:
                    #print(message)
                    response = parser.parse(message)
                    #print(response)
                    connectionSocket.send(response)
                    message = b''
                else:
                    message += msgByte
                    isPrevWhitespace = True
            else:
                message += msgByte
                isPrevWhitespace = False
            msgByte = connectionSocket.recv(1)
        connectionSocket.close()


if __name__ == '__main__':
    main()

