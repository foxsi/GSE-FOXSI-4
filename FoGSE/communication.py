import json, socket, sys

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
    `UplinkCommand` structures command data to provide a safe interface for sending commands during testing and flight. These commands are sent over UDP to the FOXSI Formatter, and must be prefixed with a target address before being wrapped in the UDP/Ethernet packets. This class only defines the command bitstring and requirements for the target.

    :param name: A human-readable and informative name for the command.
    :type name: str
    :param bytestring: The unique encoding of the command which will be transmitted to FOXSI.
    :type bytestring: list[int]
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

    def __init__(self, name: str, bytestring: list[int], arg_len: int, reply_len: int, targets: set or list, flight: bool, valid_systems: set or list):
        # assign name and bytestring
        self.name = name
        self.bytestring = bytestring

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
    `UplinkCommandDeck` is used to safely ingest desired system and command list, and provide a reliable interface to the commands that does not allow commands to be misaplied to systems.

    :param commands: List of `UplinkCommand`s.
    :type commands: list[UplinkCommand]
    :param systems: List of `CommandSystem`s to which the `commands` can be sent.
    :type systems: list[CommandSystem]
    """

    def __init__(self, system_file: str, command_file: str):
        self.commands: list[UplinkCommand] = []
        self.systems: list[CommandSystem] = []
        named_systems = {}

        with open(system_file) as sysf:
            systems_in = sysf.read()

        systems_json = json.loads(systems_in)
        params.DEBUG_PRINT("loaded experiment systems definition")

        with open(command_file) as cmdf:
            cmds_in = cmdf.read()

        commands_json = json.loads(cmds_in)
        params.DEBUG_PRINT("loaded experiment commands definition")

        for sys in systems_json:
            self.systems.append(CommandSystem(
                sys["name"],
                int(sys["id"], 0)
            ))
            named_systems[sys["name"]] = self.systems[-1]

        for command in commands_json:
            thistargets = []
            for tg in command["targets"]:
                if tg in named_systems:
                    thistargets.append(named_systems[tg])

            self.commands.append(UplinkCommand(
                command["name"],
                int(command["bytestring"], 0),
                command["arg_len"],
                command["reply_len"],
                set(thistargets),
                command["flight"],
                self.systems
            ))
    
        self.validate()

    def validate(self):
        """
        `validate` checks that all uplink commands and systems are unique (unique `name` and `bytestring` or `addr`). Exceptions are raised if this is not the case.
        """
        # you got this! you can do it.
        
        params.DEBUG_PRINT("validating command and system list...")
        if len(self.commands) != len(set(self.commands)):
            raise Exception("command objects are not unique.")
        
        cmd_names = [cmd.name for cmd in self.commands]
        cmd_ids = [cmd.bytestring for cmd in self.commands]

        if len(cmd_names) != len(set(cmd_names)):
            raise Exception("command names are not unique.")
        if len(cmd_ids) != len(set(cmd_ids)):
            raise Exception("command ids are not unique.")
        
        params.DEBUG_PRINT("\tcommands are unique.")

        sys_names = [sys.name for sys in self.systems]
        sys_addrs = [sys.addr for sys in self.systems]

        if len(sys_names) != len(set(sys_names)):
            raise Exception("system names are not unique")
        if len(sys_addrs) != len(set(sys_addrs)):
            raise Exception("system names are not unique")
        
        params.DEBUG_PRINT("\tsystems are unique.")

    def get_command_by_name(self, name: str):
        """
        `get_command_by_name` returns the `UplinkCommand` object with the provided `name`.
        """
        command = next((cmd for cmd in self.commands if cmd.name == name), None)
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
        commands = []
        for cmd in self.commands:
            if system in cmd.targets:
                commands.append(cmd)
        return commands

    def get_commands_for_system(self, system: str):
        """
        `get_commands_for_system` returns all the commands that can be sent to `system`.
        """
        commands = []
        for cmd in self.commands:
            if self.get_system_by_name(system) in cmd.targets:
                commands.append(cmd)
        return commands

    def get_systems_for_command(self, command: UplinkCommand):
        """
        `get_systems_for_command` returns all the systems that can `command` can be sent to.
        """
        return command.targets

    def get_systems_for_command(self, command: str):
        """
        `get_systems_for_command` returns all the systems that can `command` can be sent to.
        """
        return self.get_command_by_name(command).targets



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
        
    # make packet from Uplink command. todo: impleme
    def make_packet(self, command_num: int, command: UplinkCommand):
        pass

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
