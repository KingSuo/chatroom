#! /usr/bin/python3
# -*- coding: utf-8 -*-

import socket
import logging
import threading

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s')
ADDRESS = "127.0.0.1"
PORT = 3336
RECEIVE_SIZE = 1024


class Client:
    def __init__(self):
        logger = logging.getLogger(__name__)
        self.serverAddress = ADDRESS
        self.serverPort = PORT

        try:
            self.socketFD = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            logger.info("Create socket file descriptor OK!")
        except Exception as e:
            logger.error(e)

        try:
            self.socketFD.connect((self.serverAddress, self.serverPort))
            logger.info("Connect to server socket OK!")
        except Exception as e:
            logger.error(e)

    def login(self, username, authkey):
        pass

    def register(self, *args, **kwargs):

        if len(args) == 0:
            self._send("--register")
        elif len(args) == 1:
            username = args[0]
            self._send("--register %s" % username)
        elif "username" in kwargs.keys():
            username = kwargs["username"]
            self._send("--register %s" % username)
        elif "username" in kwargs.keys() and "password" in kwargs.keys():
            username = kwargs["username"]
            password = kwargs["password"]
            self._send("--register %s %s" % (username, password))
        else:
            username = args[0]
            password = args[1]
            self._send("--register %s %s" % (username, password))

    def receive(self):
        while True:
            msg = self.socketFD.recv(RECEIVE_SIZE).decode('utf-8')
            print(msg)

    def _send(self, msg):
        self.socketFD.send(str(msg).encode('utf-8'))

    def send(self):
        while True:
            self._send(input())


if __name__ == "__main__":
    client = Client()
    client.register()
    t1 = threading.Thread(target=client.receive)
    t2 = threading.Thread(target=client.send)
    t1.start()
    t2.start()
