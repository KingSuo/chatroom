#! /usr/bin/python3
# -*- coding: utf-8 -*-

import os
import logging
import socket

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ADDRESS = "127.0.0.1"
PORT = 3333


class Server:
    def __init__(self, address=ADDRESS, port=PORT):
        self.address = address
        self.port = port
        self.UserProfile = []
        self.usernameSet = set()

    def register(self, username, password):
        logger = logging.getLogger(__name__)
        try:
            result = os.popen("cat ./ServerFolder/usernameset.txt | grep %s" % username)
            if result == '':

                with open("./ServerFolder/usernameset.txt", 'a') as f:
                    f.write(username)
                    logger.info("Add new username to usernameset.txt.")
            else:
                logger.warning("username: %s has been used! Please choose other name!")
                return

        except Exception as e:
            logger.error(e)
            return

    def run(self):
        pass

    def receive(self):
        pass

    def send(self):
        pass
