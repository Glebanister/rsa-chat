import socket
import threading
import sys
import rsa
from colors import colors
from functions import *

DATA_PORTION = 1024
HOST = 'localhost'
PORT = 2000
CONNECTED_TO_SERVER = r'CID: *'
CHAT_REQUEST_TYPE = r'[0-9][0-9][0-9].[0-9][0-9][0-9].REQUEST*'
CHAT_ACCEPT_TYPE = r'[0-9][0-9][0-9].[0-9][0-9][0-9].ACCEPTED*'
CHAT_MESSAGE_TYPE = r'[0-9][0-9][0-9].[0-9][0-9][0-9].MESSAGE*'
FROM_SERVER_TYPE = r'[0-9][0-9][0-9].[0-9][0-9][0-9].SERVER*'


def info(s):
    print(colors.WARNING + s + colors.ENDC)


def danger(s):
    print(colors.FAIL + "FAIL: " + s + colors.ENDC)


def success(s):
    print(colors.OKGREEN + s + colors.ENDC)


class Client:
    def __init__(self, host, port):
        self.sock = socket.socket()
        self.sock.connect((host, port))
        self.log("created", "")
        self.log("started making keys")
        self.keys = rsa.rsa()
        self.log("finished")
        self.private, self.public, self.module = self.keys[
            "private"], self.keys["public"], self.keys["module"]
        self.curCoModule = -1
        self.curCoPublic = -1
        self.curCoCid = -1
        self.cid = -1

    def log(self, message, color="", inform=True):
        string = "CLIENT: [{}]".format(message) if inform else message
        if (color == "ok"):
            success(string)
        elif (color == "info"):
            info(string)
        elif (color == "danger"):
            danger(string)
        else:
            print(string)

    def processMessage(self, message):
        # self.log(message.decode())
        decoded = message.decode()
        if (isMatch(decoded, CONNECTED_TO_SERVER)):
            self.cid = getNumbersFromString(decoded)[0]
            self.log("--- Connected successfully ---", "ok")
            self.log("YOUR CID: " + str(self.cid), 'info')
        elif (isMatch(decoded, CHAT_REQUEST_TYPE)):
            self.log("Creating chat", "info")
            nums = getNumbersFromString(decoded)
            self.curCoCid, self.curCoPublic, self.curCoModule = nums[0], nums[2], nums[3]
            self.sendRequest("ACCEPTED.public:{}.module:{}".format(
                self.public, self.module))
        elif isMatch(decoded, CHAT_ACCEPT_TYPE):
            nums = getNumbersFromString(decoded)
            self.curCoCid, self.curCoPublic, self.curCoModule = nums[0], nums[2], nums[3]
            self.sendMessage("**created chat**")
            self.log("--- Chat created ---", "ok")
        elif isMatch(decoded, CHAT_MESSAGE_TYPE):
            self.log("Someone: " +
                     self.decodeMessage(throwPrefix(decoded, r'MESSAGE.')), inform=False)
        elif isMatch(decoded, FROM_SERVER_TYPE):
            self.log("SERVER: [{}]".format(
                throwPrefix(decoded, r'SERVER.')), inform=False)

    def startChat(self, cid):
        self.sendRequest("REQUEST.public:{}.module:{}".format(
            self.public, self.module), cid)

    def listenMessages(self):
        while True:
            data = self.sock.recv(DATA_PORTION)
            if (data):
                self.processMessage(data)

    def packRequestFromTo(self, message, to=-1):
        if (to != -1):
            return "%03d" % self.cid + '.' + "%03d" % to + '.' + message
        else:
            return "%03d" % self.cid + '.' + "%03d" % self.curCoCid + '.' + message

    def packMessageFromTo(self, message):
        return "%03d" % self.cid + '.' + "%03d" % self.curCoCid + '.' + 'MESSAGE.' + message

    def encodeMessage(self, message):
        return self.packMessageFromTo(rsa.encrypt(message, self.curCoPublic, self.curCoModule)).encode()

    def sendRequest(self, message, to=-1):
        self.sock.send(self.packRequestFromTo(message, to).encode())

    def decodeMessage(self, message):
        return rsa.decrypt(message, self.private, self.module)

    def sendMessage(self, msg):
        self.sock.send(self.encodeMessage(msg))

    def start(self):
        messListener = threading.Thread(target=self.listenMessages)
        messListener.start()
        self.log("listeners started")

    def close(self):
        self.sock.close()


def main():
    success("======\nCLIENT\n======")
    input("Press ENTER to start\n")
    info("'q' to quit")
    info("'c' to get online clients CID's")
    info("'cid: ' to start chat")
    info("'me: ' before message to send message")
    c = Client(HOST, PORT)
    c.start()
    MESSAGE = r'me: *'
    CID = r'cid: *'
    EXIT = r'q'
    CLIENTS = r'c'
    inChat = False
    while True:
        req = input()
        if (isMatch(req, MESSAGE)):
            c.sendMessage(req[3:])
        elif (isMatch(req, CID)):
            if (inChat):
                c.sendMessage("**left the chat**")
            c.startChat(getNumbersFromString(req)[0])
            inChat = True
        elif (isMatch(req, EXIT)):
            c.sendMessage("**left the chat**")
            c.close()
            sys.exit()
            inChat = False
        elif (isMatch(req, CLIENTS)):
            c.sendRequest("CLIENTS", 0)


if (__name__ == "__main__"):
    main()
