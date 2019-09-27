import socket
import threading
import sys
import Client
from time import sleep
from collections import deque
from lib.functions import isMatch, getNumbersFromString, throwPrefix
from connection import HOST, PORT

DATA_PORTION = 1024
N_CONNECTIONS = 5
MAX_CONNECTIONS = 256
DELAY = 0.1

REQUEST_CLIENTS = r'[0-9][0-9][0-9].[0-9][0-9][0-9].CLIENTS*'
BREAK_REQUEST = "b"

class clientListener:
    def __init__(self, conn, server, cid):
        self.conn = conn
        self.server = server
        self.cid = cid
        server.log("new listener cid: " + str(cid))

    def listenMessages(self):
        while self.server.live:
            sleep(DELAY)
            try:
                data = self.conn.recv(DATA_PORTION)
                if (data):
                    self.server.queue.append(data)
            except:
                self.server.log("client died cid: " + str(self.cid))
                self.server.freeCids.add(self.cid)
                return

    def start(self):
        self.listener = threading.Thread(target=self.listenMessages)
        self.listener.start()


class connectionThread:
    def __init__(self, host, port):
        try:
            self.sock = socket.socket()
            self.sock.bind((host, port))
        except socket.error:
            print('Failed to create socket')
            sys.exit()
        self.clients = [None for i in range(MAX_CONNECTIONS)]
        self.queue = deque()
        self.freeCids = set([i for i in range(1, MAX_CONNECTIONS)])
        self.log("created")
        self.live = True

    def log(self, message):
        print("SERVER: [{}]".format(message))

    def encodeServerMessage(self, message, to):
        return ("000." + "%03d" % to + "." + "SERVER." + message)

    def getClientsList(self):
        resp = []
        for i in range(1, MAX_CONNECTIONS):
            if (i not in self.freeCids):
                resp.append(i)
        return resp

    def processMessage(self, message):
        decoded = message.decode()
        self.log("recieved message: " + decoded)
        cidTo = getNumbersFromString(decoded)[1]
        cidFrom = getNumbersFromString(decoded)[0]
        if (cidTo not in self.freeCids):
            if (cidTo != 0):
                self.sendMessage(decoded, cidTo)
            else:
                if (isMatch(decoded, REQUEST_CLIENTS)):
                    self.sendMessage(self.encodeServerMessage("all clients: " + str(self.getClientsList()), cidTo), cidFrom)
                else:
                    self.sendMessage(self.encodeServerMessage("this is server's cid", cidTo), cidFrom)

        else:
            self.sendMessage(self.encodeServerMessage("cid doesn't exist", cidTo), cidFrom)

    def sendMessage(self, message, clientId):
        self.clients[clientId].send(message.encode())
        self.log("message sent: " + message)

    def listenInput(self):
        while self.live:
            sleep(DELAY)
            request = input(">> ")
            if (request == BREAK_REQUEST):
                for conn in self.clients:
                    if (conn):
                        conn.close()
                self.live = False
                sys.exit()

    def listenConnections(self):
        self.sock.listen(N_CONNECTIONS)
        while self.live:
            sleep(DELAY)
            if (not len(self.freeCids) == 0):
                conn, address = self.sock.accept()
                newCid = self.freeCids.pop()
                newClientListener = clientListener(conn, self, newCid)
                newClientListener.start()
                self.clients[newCid] = conn
                self.sendMessage("CID: " + str(newCid), newCid)
                self.log('client connected: {}'.format(address))

    def listenMessages(self):
        while self.live:
            sleep(DELAY)
            while (len(self.queue)):
                message = self.queue.popleft()
                self.processMessage(message)

    def start(self):
        self.log("started")
        connListener = threading.Thread(target=self.listenConnections)
        messListener = threading.Thread(target=self.listenMessages)
        # inputListener = threading.Thread(target=self.listenInput)
        connListener.start()
        messListener.start()
        # inputListener.start()


def main():
    print("======\nSERVER. 'b' to disconnect all clients\n======")
    input("Press ENTER to start")
    connections = connectionThread(HOST, PORT)
    connections.start()

main()
