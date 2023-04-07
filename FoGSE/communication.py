import socket, sys

import FoGSE.parameters

class FormatterInterface:
    def __init__(self):
        self.formatter_ip = FoGSE.parameters.FORMATTER_IP
        self.formatter_port = FoGSE.parameters.FORMATTER_PORT

        self.local_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # address (IP and port) of remote server
        self.remote_addr = (self.formatter_ip, self.formatter_port)
        
        # store received packets
        self.data = []

        # expected reply length
        self.recv_len = 0

        # log file for reading
        self.file = []

        # track progress through logfile
        self.last_line = 0
    
    # opens log file (written by ListenerLogger)
    def openLog(self, filename):
        self.file = open(filename, "r")

    # closes log file (written by ListenerLogger)
    def closeLog(self, filename):
        self.file.close()

    # send message to Formatter. todo: prepend detector address
    def send(self, message):
        FoGSE.parameters.DEBUG_PRINT("sending message to remote")
        self.local_socket.sendto(message, self.remote_addr)
    
    # prepend destination system address before sending. 
    def sendto(self, system_addr, message):
        FoGSE.parameters.DEBUG_PRINT("sending message to remote system")
        sendstring = system_addr + message
        self.local_socket.sendto(sendstring, self.remote_addr)
    
    # unimplemented: UDP recv handled by ListenerLogger application
    def recv(self):
        print("use ListenerLogger for receiving, and read from log file.")
        raise Exception("Use ListenerLogger for receive.")
    
    # todo: implement later
    def read(self):
        pass

    # read an array of lines from the log file
    def readlines(self, lines):
        return self.getlines(self.file, lines)

    # utility function used by readlines()
    def getlines(self, lines):
        return (x for i, x in enumerate(self.file) if i in lines)

        