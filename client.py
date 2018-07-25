#! /usr/bin/python3
# -*- coding: utf-8 -*-

import socket

from server import ADDRESS, PORT


class Client:
    def __init__(self):
        self.serverAddress = ADDRESS
        self.serverPort = PORT

    def login(self, username, authkey):
        pass

    def receive(self):
        pass

    def send(self):
        pass
