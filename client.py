#! /usr/bin/python3
# -*- coding: utf-8 -*-

import socket
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s')
ADDRESS = "127.0.0.1"
PORT = 3333
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

    def register(self, username=None, password=None):
        self.send("--register %s %s" % (username, password))

    def receive(self):
        msg = self.socketFD.recv(RECEIVE_SIZE).decode('utf-8')
        print(msg)

    def send(self, msg):
        self.socketFD.send(str(msg).encode('utf-8'))


if __name__ == "__main__":
    client = Client()
    client.register()
    while True:
        client.receive()
        client.send(input().encode('utf-8'))
