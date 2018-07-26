#! /usr/bin/python3
# -*- coding: utf-8 -*-

import random
import os
import logging
import socket
import threading

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s')
ADDRESS = "127.0.0.1"
PORT = 3335
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
            print("================")
            logger.error(e)

    def _isValidusername(self, **kwargs):
        logger = logging.getLogger(__name__)
        client_socket = kwargs["client_socket"]
        if "username" in kwargs.keys():
            username = kwargs["username"]
        else:
            username = self.receive(client_socket)
            # username = client_socket.recv(RECEIVE_SIZE).decode('utf-8')

        if ' ' in username or '-' in username or '!' in username:
            logger.warning("Invalid character in username %s!" % username)
            try:
                self.send(client_socket, "Invalid character in your username: %s!Please try again!" % username)
                # client_socket.send(
                #     ("Invalid character in your username: %s!Please try again!" % username).encode('utf-8'))
                self.send(client_socket, "Please enter your username:")
                # client_socket.send("Please enter your username:".encode('utf-8'))
            except Exception as e:
                logger.error(e)
            return False
        else:
            return username

    def _register(self, username, password):
        logger = logging.getLogger(__name__)
        try:
            result = os.popen("cat ./ServerFolder/UserProfile.txt | grep %s" % username).read()
            print(result)
            if result == '':
                os.system("echo %s:%s >> ./ServerFolder/UserProfile.txt" % (str(username), str(hash(password))))
                logger.info("Add new username to UserProfile.txt.")
            else:
                logger.warning("username: %s has been used! Please choose other name!")
        except Exception as e:
            logger.error(e)

    def register(self, *args, **kwargs):
        logger = logging.getLogger(__name__)
        repeat_times = 0
        client_socket = kwargs["client_socket"]
        if len(args) == 0:  # only --register
            self.send(client_socket, "Please enter your username:")
            # client_socket.send("Please enter your username:".encode('utf-8'))
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
                    # client_socket.send(("OH MY GOD,MAN!YOUR ARE SO GOOD ENOUGH THAT I CANNOT HELP GIVING YOUR
                    # A NAME CALLED %s!" % username).encode('utf-8'))
                    logger.info("Automatically assign username: %s" % username)
                    break
                username = self._isValidusername(**kwargs)
            self.send(client_socket, "Please enter your password:")
            # client_socket.send("Please enter your password:".encode('utf-8'))
            password = hash(self.receive(client_socket))
            # password = hash(client_socket.recv(RECEIVE_SIZE).decode('utf-8'))
            self._register(username=username, password=password)
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
                    # client_socket.send(("OH MY GOD,MAN!YOUR ARE SO GOOD ENOUGH THAT I CANNOT HELP GIVING YOUR
                    # A NAME CALLED %s!" % username).encode('utf-8'))
                    logger.info("Automatically assign username: %s" % username)
                    break
                username = self._isValidusername(**kwargs)
            self.send(client_socket, "Please enter your password:")
            # client_socket.send("Please enter your password:".encode('utf-8'))
            password = hash(self.receive(client_socket))
            # password = hash(client_socket.recv(RECEIVE_SIZE).decode('utf-8'))
            self._register(username=username, password=password)
        else:  # --register {username} {password}
            print(args)
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
                    # client_socket.send(("OH MY GOD,MAN!YOUR ARE SO GOOD ENOUGH THAT I CANNOT
                    # HELP GIVING YOUR A NAME CALLED %s!" % username).encode('utf-8'))
                    logger.info("Automatically assign username: %s" % username)
                    break
                username = self._isValidusername(**kwargs)
            self.send(client_socket, "Please enter your password:")
            # client_socket.send("Please enter your password:".encode('utf-8'))
            password = hash(self.receive(client_socket))
            # password = hash(client_socket.recv(RECEIVE_SIZE).decode('utf-8'))
            self._register(username=username, password=password)
        logger.info("User register OK!")

    def login(self, *args, **kwargs):
        pass

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
        print(msg)
        print(type(msg))
        if msg.startswith("--"):
            command, *args = msg.split(' ')
            try:
                print("command: ", command)
                print("command_type: ", type(command))
                self.COMMAND_LIST[command](*args, **kwargs)
                logger.info("Get command OK!")
            except Exception as e:
                print("++++++++++++")
                logger.error(e)
        else:
            pass

    def _tcpservice(self, client_socket):
        while True:
            msg = self.receive(client_socket)
            # msg = client_socket.recv(RECEIVE_SIZE).decode('utf-8')
            print('=============')
            print(msg)
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
