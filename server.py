#! /usr/bin/python3
# -*- coding: utf-8 -*-

import random
import os
import logging
import socket
import threading
from hashlib import sha512

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s')
ADDRESS = "127.0.0.1"
PORT = 3336
MAX_LISTEN_NUM = 20
RECEIVE_SIZE = 1024


class Server:
    def __init__(self, address=ADDRESS, port=PORT, maxListenNum=MAX_LISTEN_NUM):
        logger = logging.getLogger(__name__)
        self.address = address
        self.port = port
        self.client_sockets = []
        self.maxListenNum = maxListenNum
        self.COMMAND_LIST = {
            "--register": self.register, "--login": self.login, "--quit": self.quit,
            "--create-chatroom": self.createchatroom, "--join-chatroom": self.joinchatroom,
            "--quit-chatroom": self.quitchatroom, "--delete-chatroom": self.deletechatroom,
            "--add-friend": self.addfriend, "--delete-friend": self.deletefriend, "--search-user": self.searchuser,
            "--talk-with": self.talkwith
        }
        self.STATUS_LIST = {
            "register": 1, "login": 1, "quit": 1, "create-chatroom": 1, "join-chatroom": 1, "quit-chatroom": 1,
            "delete-chatroom": 1, "add-friend": 1, "delete-friend": 1, "search-user": 1, "talk-with": 1
        }

        try:
            self.socketFD = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            logger.info("Create socket file descriptor OK!")
        except Exception as e:
            logger.error(e)

        try:
            self.socketFD.bind((self.address, self.port))
            logger.info("Bind to %s : %s OK!" % (self.address, self.port))
        except Exception as e:
            logger.error(e)

        try:
            self.socketFD.listen(self.maxListenNum)
            logger.info("Listen to clients OK!")
        except Exception as e:
            logger.error(e)

    def _isValidusername(self, **kwargs):
        logger = logging.getLogger(__name__)
        client_socket = kwargs["client_socket"]
        if "username" in kwargs.keys():
            username = kwargs["username"]
        else:
            self.send(client_socket, "Please enter your username:")
            username = self.receive(client_socket)

        if ' ' in username or '-' in username or '!' in username:
            logger.warning("Invalid character in username %s!" % username)
            try:
                self.send(client_socket, "Invalid character in your username: %s!Please try again!" % username)
            except Exception as e:
                logger.error(e)
            return False
        else:
            return username

    def _register(self, **kwargs):
        logger = logging.getLogger(__name__)
        username = kwargs["username"]
        password = kwargs["password"]
        client_socket = kwargs["client_socket"]
        try:
            result = os.popen("cat ./ServerFolder/UserProfile.txt | grep %s" % username).read()
            print(result)
            if result == '':
                sha = sha512()
                sha.update(str(password).encode('utf-8'))
                password = sha.hexdigest()
                os.system("echo %s:%s >> ./ServerFolder/UserProfile.txt" % (str(username), password))
                logger.info("Add new username to UserProfile.txt.")
                self.send(client_socket, "Successfully register!")
                return True
            else:
                logger.warning("username '%s' has been used! Please choose other name!" % username)
                self.send(client_socket,
                          "username '%s' has been used! Please choose other name!" % username)
                return False
        except Exception as e:
            logger.error(e)
            self.send(client_socket, "Some errors to register!")
            return False

    def register(self, *args, **kwargs):
        logger = logging.getLogger(__name__)
        repeat_times = 0
        client_socket = kwargs["client_socket"]
        if len(args) == 0:  # only --register
            username = False
            while not username:
                repeat_times += 1
                if repeat_times > 5:
                    tempID = random.randint(0, 99)
                    username = "Agan%d" % tempID
                    self.send(
                        client_socket,
                        "OH MY GOD,MAN!YOUR ARE SO GOOD ENOUGH THAT I CANNOT HELP GIVING YOUR A NAME CALLED %s!" % username
                    )
                    logger.info("Automatically assign username: %s" % username)
                    break
                username = self._isValidusername(**kwargs)
            self.send(client_socket, "Please enter your password:")
            password = self.receive(client_socket)
            isRegistered = self._register(username=username, password=password, client_socket=client_socket)
            repeat_times = 0
            while not isRegistered:
                repeat_times += 1
                if repeat_times >= 4:
                    self.send(client_socket, "OH MY GOD!PLEASE GIVE UP NOW!")
                    break
                self.send(client_socket, "Please enter your username:")
                username = self.receive(client_socket)
                self.send(client_socket, "Please enter your password:")
                password = self.receive(client_socket)
                isRegistered = self._register(username=username, password=password, client_socket=client_socket)
        elif len(args) == 1:  # only --register {username}
            kwargs["username"] = args[0]
            username = self._isValidusername(**kwargs)
            while not username:
                kwargs.pop(username)
                repeat_times += 1
                if repeat_times > 5:
                    tempID = random.randint(0, 99)
                    username = "Agan%d" % tempID
                    self.send(
                        client_socket,
                        "OH MY GOD,MAN!YOUR ARE SO GOOD ENOUGH THAT I CANNOT HELP GIVING YOUR A NAME CALLED %s!" % username
                    )
                    logger.info("Automatically assign username: %s" % username)
                    break
                username = self._isValidusername(**kwargs)
            self.send(client_socket, "Please enter your password:")
            password = self.receive(client_socket)
            isRegistered = self._register(username=username, password=password, client_socket=client_socket)
            repeat_times = 0
            while not isRegistered:
                repeat_times += 1
                if repeat_times >= 4:
                    self.send(client_socket, "OH MY GOD!PLEASE GIVE UP NOW!")
                    break
                self.send(client_socket, "Please enter your username:")
                username = self.receive(client_socket)
                self.send(client_socket, "Please enter your password:")
                password = self.receive(client_socket)
                isRegistered = self._register(username=username, password=password, client_socket=client_socket)
        else:  # --register {username} {password}
            print(args)
            kwargs["username"] = args[0]
            kwargs["password"] = args[1]
            username = self._isValidusername(**kwargs)
            while not username:
                kwargs.pop(username)
                repeat_times += 1
                if repeat_times > 5:
                    tempID = random.randint(0, 99)
                    username = "Agan%d" % tempID
                    self.send(
                        client_socket,
                        "OH MY GOD,MAN!YOUR ARE SO GOOD ENOUGH THAT I CANNOT HELP GIVING YOUR A NAME CALLED %s!" % username
                    )
                    logger.info("Automatically assign username: %s" % username)
                    break
                username = self._isValidusername(**kwargs)
            isRegistered = self._register(username=username, password=password, client_socket=client_socket)
            repeat_times = 0
            while not isRegistered:
                repeat_times += 1
                if repeat_times >= 4:
                    self.send(client_socket, "OH MY GOD!PLEASE GIVE UP NOW!")
                    break
                self.send(client_socket, "Please enter your username:")
                username = self.receive(client_socket)
                self.send(client_socket, "Please enter your password:")
                password = self.receive(client_socket)
                isRegistered = self._register(username=username, password=password, client_socket=client_socket)
        logger.info("Register function end!")

    def is_exist(self, *args, **kwargs):
        if "username" in kwargs.keys() and "filename" in kwargs.keys():
            username = kwargs["username"]
            filename = kwargs["filename"]
            result = os.popen("cat %s | grep %s" % (filename, username)).read()
        return False if result == '' else True

    def login(self, *args, **kwargs):
        client_socket = kwargs["client_socket"]

    def quit(self, *args, **kwargs):
        pass

    def createchatroom(self, *args, **kwargs):
        pass

    def joinchatroom(self, *args, **kwargs):
        pass

    def quitchatroom(self, *args, **kwargs):
        pass

    def deletechatroom(self, *args, **kwargs):
        pass

    def addfriend(self, *args, **kwargs):
        pass

    def deletefriend(self, *args, **kwargs):
        pass

    def searchuser(self, *args, **kwargs):
        pass

    def talkwith(self, *args, **kwargs):
        pass

    def _msganalysis(self, msg, **kwargs):
        logger = logging.getLogger(__name__)
        client_socket = kwargs["client_socket"]
        print(msg)
        print(len(msg))
        print(type(msg))
        if msg.startswith("--"):
            msg = msg.rstrip()
            command, *args = msg.split(' ')
            try:
                print("command:%s!" % command)
                if command in self.COMMAND_LIST.keys():
                    self.COMMAND_LIST[command](*args, **kwargs)
                    logger.info("Get command '%s' OK!" % command)
                else:
                    self.send(client_socket, "Unknown command '%s'!" % command)
                    # using for other command,default --talkwith
            except Exception as e:
                print("++++++++++++")
                logger.error(e)
        else:
            pass

    def _tcpservice(self, client_socket):
        while True:
            msg = self.receive(client_socket)
            if not msg:
                break
            self._msganalysis(msg, client_socket=client_socket)

    def run(self):
        while True:
            client_socket, client_address = self.socketFD.accept()
            t = threading.Thread(target=self._tcpservice, args=(client_socket,))
            t.start()

    def receive(self, client_socket):
        return client_socket.recv(RECEIVE_SIZE).decode('utf-8')

    def send(self, client_socket, msg):
        client_socket.send(str(msg).encode('utf-8'))


if __name__ == "__main__":
    server = Server()
    server.run()
