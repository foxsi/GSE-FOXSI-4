import socket, sys

import FoGSE.parameters as params

class UplinkCommand:
    """
    `UplinkCommand` structures command data to provide a safe interface for sending commands during testing and flight. These commands are sent over UDP to the FOXSI Formatter, and must be prefixed with a target address before being wrapped in the UDP/Ethernet packets. This class only defines the command bitstring and requirements for the target.

    :param name: A readable and informative name for the command.
    :type name: str
    :param bytestring: The encoding of the command which will be transmitted to FOXSI.
    :type bytestring: list[int]
    :param arg_len: The length (in bytes) of the argument to the command. If `arg_len <= 0`, assume no arguments required.
    :type arg_len: int
    :param reply_len: The length (in bytes) of the expected reply to the command. If `reply_len <= 0`, assume no reply.
    :type reply_len: int
    :param targets: The onboard systems this command may be sent to. `targets` must be a subset of `FoGSE.parameters.SUBSYSTEMS`.
    :type targets: set
    :param flight: Set `True` to enable this command during flight. If `False`, mark the command for use only during ground test.
    :type flight: bool
    """

    def __init__(self, name: str, bytestring: list[int], arg_len: int, reply_len: int, targets: set, flight: bool):
        self.command_name = name
        self.bytestring = bytestring
        self.reply_len = reply_len
        if reply_len < 0:
            raise Warning("reply length is negative, assuming no reply")
        elif reply_len == 0:
            self.write = True
            self.read = False
        else:
            self.read = True
            self.write = False

        if targets <= params.SUBSYSTEMS:
            self.targets = targets
        else:
            raise Exception("targets must be a subset of parameters.SUBSYSTEMS set")
        
        self.flight = flight

        if arg_len < 0:
            raise Warning("argument length is negative, assuming zero")
            self.arg_len = 0
        else:
            self.arg_len = arg_len

class FormatterUDPInterface:
    def __init__(self):
        self.formatter_ip = params.FORMATTER_IP
        self.formatter_port = params.FORMATTER_PORT

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
    def open_log(self, filename):
        self.file = open(filename, "r")

    # closes log file (written by ListenerLogger)
    def close_log(self, filename):
        self.file.close()

    # send message to Formatter. todo: prepend detector address
    def send(self, command):
        params.DEBUG_PRINT("sending message to remote")
        self.local_socket.send_to(command, self.remote_addr)
    
    # prepend destination system address before sending. 
    def send_to(self, system_addr, command, arg):
        params.DEBUG_PRINT("sending message to remote system")
        send_packet = self.make_packet(system_addr, command, arg)
        self.local_socket.sendto(send_packet, self.remote_addr)

    # build packet to uplink. todo: make this way more robust and safe.
    def make_packet(self, system_addr, message, arg):
        params.DEBUG_PRINT("building uplink packet to send")
        # maybe do system_addr.decode("ASCII") here or something?
        return system_addr + params.UPLINK_PACKET_SUBSYSTEM_DELIM + message + params.UPLINK_PACKET_COMMAND_DELIM + arg
        

    # unimplemented: UDP recv handled by ListenerLogger application
    def recv(self):
        print("use ListenerLogger for receiving, and read from output log file.")
        raise Exception("Use ListenerLogger for receiving messages from Formatter.")
    
    # todo: implement later. Or maybe implement elsewhere.
    def read(self):
        pass

    # read an array of lines from the log file
    def read_lines(self, lines):
        return self.get_lines(self.file, lines)

    # utility function used by readlines()
    def get_lines(self, lines):
        return (x for i, x in enumerate(self.file) if i in lines)

        