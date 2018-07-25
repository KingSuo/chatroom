#! /usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import socket

from server import ADDRESS, PORT

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

RECEIVE_SIZE = 1024


class ChatRoom:
    def __init__(self):
        self.serverAddress = ADDRESS
        self.serverPort = PORT
        logger = logging.getLogger(__name__)

        try:
            self.sockFD = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            logger.info("Create socket file descriptorS %s OK!" % str(self.sockFD))
        except Exception as e:
            logger.error(e)

        try:
            self.sockFD.connect((self.serverAddress, self.serverPort))
            logger.info("Connect to server OK!")
        except Exception as e:
            logger.error(e)

    def _receive(self):
        while True:
            msg = self.sockFD.recv(RECEIVE_SIZE)
            print(msg)
            if msg == "--chat-over" or msg == "--delete-chatroom":
                break

    def run(self):
        self._receive()


if __name__ == "__main__":
    chatroom = ChatRoom()
    chatroom.run()
