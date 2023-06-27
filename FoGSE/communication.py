import json, socket, sys, math

import FoGSE.parameters as params



class CommandSystem:
    """
    `CommandSystem` is a container for an onboard system name and hex ID. This class is used for addressing `UplinkCommand`s.
    
    :param name: A human-readable and informative name for the system.
    :type name: str
    :param addr: A unique system identifier.
    :type addr: int
    """

    def __init__(self, name: str, addr: int):
        self.name = name
        self.addr = addr



class UplinkCommand:
    """
    `UplinkCommand` structures command data to provide a safe interface for sending commands during testing and flight. These commands are sent over UDP to the FOXSI Formatter, and must be prefixed with a target address before being wrapped in the UDP/Ethernet packets. This class only defines the command hex code and requirements for the target.

    :param name: A human-readable and informative name for the command.
    :type name: str
    :param hex: The unique encoding of the command which will be transmitted to FOXSI.
    :type hex: list[int]
    :param arg_len: The length (in bytes) of the argument to the command. If `arg_len <= 0`, assume no arguments required.
    :type arg_len: int
    :param reply_len: The length (in bytes) of the expected reply to the command. If `reply_len <= 0`, assume no reply.
    :type reply_len: int
    :param targets: The onboard systems this command may be sent to. `targets` must be a subset of `FoGSE.parameters.SUBSYSTEMS`.
    :type targets: set
    :param flight: Set `True` to enable this command during flight. If `False`, mark the command for use only during ground test.
    :type flight: bool
    :param valid_systems: A set of allowable systems for all commands.
    :type valid_systems: set
    """

    def __init__(self, name: str, hex: list[int], arg_len: int, reply_len: int, targets: set or list, flight: bool, valid_systems: set or list):
        # assign name and hex code
        self.name = name
        self.hex = hex

        # assign reply_len, then change read/write properties based on it
        self.reply_len = reply_len
        if reply_len < 0:
            self.reply_len = 0
            raise Warning("reply length is negative, assuming no reply")
        elif reply_len == 0:
            self.write = True
            self.read = False
        else:
            self.read = True
            self.write = False

        # assign valid command targets, confirm they are allowable
        if set(targets) <= set(valid_systems):
            self.targets = targets
        else:
            print(targets)
            print(valid_systems)
            raise Exception("targets must be a subset of valid_systems set")
        
        # assign flight usability
        self.flight = flight

        # assign argument length
        if arg_len < 0:
            self.arg_len = 0
            raise Warning("argument length is negative, assuming zero")
        else:
            self.arg_len = arg_len



class UplinkCommandDeck:
    """
    `UplinkCommandDeck` is used to safely ingest desired system and command list, and provide a reliable interface to the commands that does not allow commands to be misapplied to systems.

    :param commands: List of `UplinkCommand`s.
    :type commands: list[UplinkCommand]
    :param systems: List of `CommandSystem`s to which the `commands` can be sent.
    :type systems: list[CommandSystem]
    """

    def __init__(self, system_file: str):
        # self.commands: list[UplinkCommand] = []
        self.deck: dict[int, list(UplinkCommand)] = {}
        self.systems: list[CommandSystem] = []
        named_systems = {}

        with open(system_file) as sysf:
            systems_in = sysf.read()

        systems_json = json.loads(systems_in)
        params.DEBUG_PRINT("loaded experiment systems definition")

        for sys in systems_json:
            # add the system to the system list
            self.systems.append(CommandSystem(
                sys["name"].lower(),
                int(sys["hex"], 0)
            ))
            named_systems[sys["name"]] = self.systems[-1]

        for sys in systems_json:
            this_name = sys["name"].lower()

            params.DEBUG_PRINT("\nsearching for commands for " + sys["name"])

            this_command_list: list[UplinkCommand] = []

            command_path = ""
            try:
                command_path = sys["ethernet_interface"]["command_path"]
                params.DEBUG_PRINT("found command file " + command_path + " for " + sys["name"])
                this_command_list = self.add_commands_for_system(self.get_system_by_name(this_name), command_path)
            except:
                print("found no ethernet commands for system " + sys["name"])
            try:
                command_path = sys["ethernet_interface"]["spacewire_interface"]["command_path"]
                params.DEBUG_PRINT("found command file " + command_path + " for " + sys["name"])
                this_command_list = self.add_commands_for_system(self.get_system_by_name(this_name), command_path)
            except:
                print("found no spacewire commands for system " + sys["name"])
            try:
                command_path = sys["uart_interface"]["command_path"]
                params.DEBUG_PRINT("found command file " + command_path + " for " + sys["name"])
                this_command_list = self.add_commands_for_system(self.get_system_by_name(this_name), command_path)
            except:
                print("found no uart commands for system " + sys["name"])

            # if sys["ethernet_interface"]["command_path"] is not None:
            #     params.DEBUG_PRINT("found command file " + sys["ethernet_interface"]["command_path"] + " for " + sys["name"])
            #     this_command_list = self.add_commands_for_system(self.get_system_by_name[this_name], sys["ethernet_interface"]["command_path"])
            # elif sys["ethernet_interface"]["spacewire_interface"]["command_path"] is not None:
            #     params.DEBUG_PRINT("found command file " + sys["ethernet_interface"]["spacewire_interface"]["command_path"] + " for " + sys["name"])
            #     this_command_list = self.add_commands_for_system(self.get_system_by_name[this_name], sys["ethernet_interface"]["spacewire_interface"]["command_path"])
            # elif sys["uart_interface"]["command_path"] is not None:
            #     params.DEBUG_PRINT("found command file " + sys["uart_interface"]["command_path"] + " for " + sys["name"])
            #     this_command_list = self.add_commands_for_system(self.get_system_by_name[this_name], sys["uart_interface"]["command_path"])
            # else:
            #     params.DEBUG_PRINT("Could not find commands for system " + sys["name"] +". Removing from deck.")
            #     continue

            # add the commands to the deck
            self.deck[named_systems[this_name].addr] = this_command_list
            
            # todo: remove this
            # for command in sys["???"]:
            #     thistargets = []
            #     for field in command.keys():
            #         if field.upper() in named_systems and int(command[field]):
            #             thistargets.append(named_systems[field.upper()])
            #     # for tg in command["targets"]:
            #     #     if tg in named_systems:
            #     #         thistargets.append(named_systems[tg])

            #     arglen = 0
            #     replen = 0
            #     if command["reply.length [B]"]:
            #         if command["reply.length [B]"].isnumeric():
            #             replen = int(command["reply.length [B]"])

            #     if command["arg1.length [B]"]:
            #         if command["arg1.length [B]"].isnumeric():
            #             arglen = 0

            #     self.commands.append(UplinkCommand(
            #         command["name"].upper(),
            #         int(command["hex"], 0),
            #         arglen,
            #         replen,
            #         set(thistargets),
            #         1,
            #         # command["flight"],
            #         self.systems
            #     ))
    
        self.validate()
        self.print()

    def validate(self):
        # you got this! you can do it.
        """
        `validate` checks that all uplink commands and systems are unique (unique `name` and `hex` or `addr`). Exceptions are raised if this is not the case.
        """

        params.DEBUG_PRINT("validating systems...")
        sys_names = [sys.name for sys in self.systems]
        sys_addrs = [sys.addr for sys in self.systems]

        if len(sys_names) != len(set(sys_names)):
            raise Exception("system names are not unique")
        if len(sys_addrs) != len(set(sys_addrs)):
            raise Exception("system names are not unique")
        
        params.DEBUG_PRINT("\tsystems are unique.")

        params.DEBUG_PRINT("validating command deck...")
        # todo: loop for all systems, check uniqueness of commands per-system

        for key in self.deck.keys():
            these_commands = self.deck[key]
            if len(these_commands) != len(set(these_commands)):
                raise Exception("command objects are not unique.")
            
            cmd_names = [cmd.name for cmd in these_commands]
            cmd_ids = [cmd.hex for cmd in these_commands]

            if len(cmd_names) != len(set(cmd_names)):
                raise Exception("command names are not unique.")
            if len(cmd_ids) != len(set(cmd_ids)):
                raise Exception("command ids are not unique.")
        
        params.DEBUG_PRINT("\tcommands are unique.")
    
    def add_commands_for_system(self, system: CommandSystem, command_file: str):
        command_list: list[UplinkCommand] = []

        with open(command_file) as file:
            cmd_file = file.read()
        cmd_json = json.loads(cmd_file)
        params.DEBUG_PRINT("\tloaded command definitions for " + system.name)

        system_names = [sys.name.lower() for sys in self.systems]

        for cmd in cmd_json:
            params.DEBUG_PRINT("\tadding command " + cmd["hex"])
            thistargets = []
            for field in cmd.keys():
                if field.lower() in system_names:
                    thistargets.append(self.get_system_by_name(field.lower()))
       
            arglen = 0
            replen = 0
            if cmd["reply.length [B]"]:
                if cmd["reply.length [B]"].isnumeric():
                    replen = int(cmd["reply.length [B]"])

            if cmd["arg1.length [B]"]:
                if cmd["arg1.length [B]"].isnumeric():
                    arglen = 0

            this_cmd = UplinkCommand(
                cmd["name"],
                int(cmd["hex"], 0),
                arglen,
                replen,
                thistargets,
                True,
                self.systems
            )
            command_list.append(this_cmd)

        return command_list
        
    def print(self):
        """
        `print` displays the command deck tree, indexed by system hex code.
        """
        print("printing command deck:")
        for sys in self.deck.keys():
            print("\t" + hex(sys))
            for cmd in self.deck[sys]:
                print("\t\t" + cmd.name + ", " + hex(cmd.hex))
    
    def get_command_by_system_by_name(self, system: CommandSystem, name: str):
        """
        `get_command_by_system_by_name` returns the `UplinkCommand` object with the provided `name` for the provided `system`.
        """
        command = next((cmd for cmd in self.deck[system.addr] if cmd.name == name), None)
        return command
    
    def get_command_by_system_by_name(self, system: int, name: str):
        """
        `get_command_by_system_by_name` returns the `UplinkCommand` object with the provided `name` for the provided `system`.
        """
        command = next((cmd for cmd in self.deck[system] if cmd.name == name), None)
        return command
    def get_command_by_system_by_name(self, system: str, name: str):
        """
        `get_command_by_system_by_name` returns the `UplinkCommand` object with the provided `name` for the provided `system`.
        """
        command = next((cmd for cmd in self.deck[self.get_system_by_name(system).addr] if cmd.name == name), None)
        return command

    def get_system_by_name(self, name: str):
        """
        `get_system_by_name` returns the `UplinkSystem` object with the provided `name`.
        """
        system = next((sys for sys in self.systems if sys.name == name), None)
        return system

    def get_commands_for_system(self, system: CommandSystem):
        """
        `get_commands_for_system` returns all the commands that can be sent to `system`.
        """
        return self.deck[system.addr]

    def get_commands_for_system(self, system: str):
        """
        `get_commands_for_system` returns all the commands that can be sent to `system`.
        """
        return self.deck[self.get_system_by_name(system).addr]



class FormatterUDPInterface:
    """
    `FormatterUDPInterface` defines a UDP/Ethernet link to the Formatter in the FOXSI experiment. This interface can only be used to send commands to the Formatter. Downlinked data should be received by the separate ListenerLogger application. 

    :param formatter_ip: The IP address to send data to. Defaults to 192.168.1.8.
    :type formatter_ip: str
    :param formatter_port: The Formatter's port number for communication with this ground software. Defaults to 9999. Must be greater than 1024.
    :type formatter_port: int
    :param do_logging: Toggles logging of transmitted commands to file.
    :type do_logging: bool
    :param local_socket: UDP socket object.
    :type local_socket: socket.socket
    :param remote_addr: Formatter IP/port pair.
    :type remote_addr: tuple
    :param logfile: File to log outbound commands to.
    :type logfile: TextIOWrapper
    """

    def __init__(self, addr=params.FORMATTER_IP, port=params.FORMATTER_PORT, logging=True, logfilename=None):
        self.formatter_ip = addr
        self.formatter_port = port

        # log sent packets to file
        self.do_logging = logging

        if self.do_logging:
            if logfilename is None:
                # make some default new log file
                logfilename = "uplink_commands.log"
            # open log file
            self.logfile = open(logfilename, 'wb+')

        self.local_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # address (IP and port) of remote server
        self.remote_addr = (self.formatter_ip, self.formatter_port)
        params.DEBUG_PRINT("remote address: " + self.formatter_ip + ":" + str(self.formatter_port))

        # expected reply length
        self.recv_len = 0

        # track progress through logfile
        self.command_count = 0

    def __del__(self):
        self.local_socket.close()
        # if self.do_logging:
        #     self.logfile.close()

    def change_endpoint(self, addr, port):
        params.DEBUG_PRINT("modifying UDP endpoint")
        self.formatter_ip = addr
        self.formatter_port = port
        self.remote_addr = (self.formatter_ip, self.formatter_port)

    # send message to Formatter.
    def send(self, message):
        params.DEBUG_PRINT("sending message to remote")
        self.local_socket.sendto(message, self.remote_addr)

    def send(self, addr: int, data: int, arg: int=None):
        params.DEBUG_PRINT("\tsending message to remote")
        
        message = bytearray([addr, data])
        if arg:
            message.extend(arg.to_bytes(math.ceil(arg.bit_length()/8.0), "big"))

        params.DEBUG_PRINT("\tmessage: 0x%s" % message.hex())
        self.local_socket.sendto(message, self.remote_addr)
        params.DEBUG_PRINT("\tmessage sent")

        if self.do_logging:
            self.logfile.write(self.command_count.to_bytes(8,"big"))
            self.logfile.write("\t".encode("ascii"))
            self.logfile.write(message)
            self.logfile.write("\n".encode("ascii"))

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
