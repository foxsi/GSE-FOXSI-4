import json, socket, os, time, subprocess

import FoGSE.parameters as params
import FoGSE.singleton as singleton

from PyQt6.QtCore import QProcess



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
                int(sys["hex"], 16)
            ))
            named_systems[sys["name"]] = self.systems[-1]

        for sys in systems_json:
            this_name = sys["name"].lower()

            params.DEBUG_PRINT("\nsearching for commands for " + sys["name"])

            this_command_list: list[UplinkCommand] = []

            command_path = ""
            try:
                command_path = sys["commands"]
                params.DEBUG_PRINT("found command file " + command_path + " for " + sys["name"])
                this_command_list = self.add_commands_for_system(self.get_system_by_name(this_name), command_path)
            except:
                print("found no commands for system " + sys["name"])

            # add the commands to the deck
            # self.deck[named_systems[this_name].addr] = this_command_list
            self.deck[int(sys["hex"], 16)] = this_command_list
    
        self.validate()

    def validate(self, system=None, command=None):
        """
        Checks that
        """
        if system is None and command is None:
            return self.validate_deck()
        elif type(system) is not None and type(command) is not None:
            if self.get_command_for_system(system, command) is not None:
                return True
            else:
                return False
        else:
            print("cannot handle the arguments you've given me!")
            return False

    
    def validate_deck(self):
        # you got this! you can do it.
        """
        Checks that all uplink commands and systems are unique (unique `name` and `hex` or `addr`). Exceptions are raised if this is not the case.
        """

        params.DEBUG_PRINT("validating systems...")
        sys_names = [sys.name for sys in self.systems]
        sys_addrs = [sys.addr for sys in self.systems]

        if len(sys_names) != len(set(sys_names)):
            raise Exception("system names are not unique")
        if len(sys_addrs) != len(set(sys_addrs)):
            raise Exception("system ids are not unique")
        
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
                print(set([name for name in cmd_names if cmd_names.count(name) > 1]))
                raise Exception("command names are not unique.")
            if len(cmd_ids) != len(set(cmd_ids)):
                raise Exception("command ids are not unique.")
        
        params.DEBUG_PRINT("\tcommands are unique.")

    def add_commands_for_system(self, system: CommandSystem, command_file: str):
        command_list: list[UplinkCommand] = []

        with open(command_file) as file:
            cmd_file = file.read()
        cmd_json = json.loads(cmd_file)

        system_names = [sys.name.lower() for sys in self.systems]

        for cmd in cmd_json:
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
            this_sys = self.get_system_by_addr(sys)
            print("\t" + this_sys.name + ",\t" + hex(this_sys.addr))
            for cmd in self.deck[sys]:
                print("\t\t" + hex(cmd.hex) + ",\t" + cmd.name)
    
    def get_command_for_system(self, system=None, command=None):
        """
        `get_command_for_system` returns the `UplinkCommand` object with the provided `command` for the provided `system`.
        """
        system_addr = None
        uplink_command = None
        if type(system) is str:
            system_obj = self.get_system_by_name(name=system)
            system_addr = system_obj.addr
        elif type(system) is int:
            system_addr = system
        elif type(system) is CommandSystem:
            system_addr = system.addr
        
        if type(command) is str:
            uplink_command = next((cmd for cmd in self.deck[system_addr] if cmd.name == command), None)
        elif type(command) is int:
            uplink_command = next((cmd for cmd in self.deck[system_addr] if cmd.hex == command), None)
        
        return uplink_command
    
    def get_system_by_name(self, name: str):
        """
        `get_system_by_name` returns the `UplinkSystem` object with the provided `name`.
        """
        system = next((sys for sys in self.systems if sys.name == name), None)
        return system
    def get_system_by_addr(self, addr: int):
        """
        `get_system_by_addr` returns the `UplinkSystem` object with the provided `addr`.
        """
        system = next((sys for sys in self.systems if sys.addr == addr), None)
        return system

    def get_commands_for_system(self, system: str):
        """
        `get_commands_for_system` returns all the commands that can be sent to `system`.
        """
        return self.deck[self.get_system_by_name(system).addr]





class FormatterUDPInterface(metaclass=singleton.Singleton):
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

    # def __init__(self, addr=params.GSE_IP, port=params.GSE_PORT, logging=True, logfilename=None):
    def __init__(self, configfile="foxsi4-commands/systems.json", logging=True, logfilename=None, end_background_process_on_close=True):
        
        # configure sockets and endpoints
        try:
            with open(configfile) as json_file:
                data = json.load(json_file)
                local = get_field_with_name(data, "gse")
                remote = get_field_with_name(data, "formatter")
                self.unix_local_socket_path = local["logger_interface"]["unix_send_socket"]
                self.unix_remote_socket_path = local["logger_interface"]["unix_listen_socket"]
                print("using unix datagram socket: " + self.unix_local_socket_path)
                try:
                    os.unlink(self.unix_local_socket_path)
                except OSError:
                    if os.path.exists(self.unix_local_socket_path):
                        raise RuntimeError

                # try to build `UplinkCommandDeck`
                try:
                    self.deck = UplinkCommandDeck(configfile)
                    self.deck.print()
                except Exception as e:
                    print("couldn't create uplink command deck!")
                    print(e)
        except:
            self.unix_local_socket_path = "/tmp/foxsi_gse_unix_udp_socket"
        
        # set up socket to listen
        self.unix_local_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self.unix_local_socket.bind(self.unix_local_socket_path)

        # log sent packets to file
        self.do_logging = logging
        self.end_background_process_on_close = end_background_process_on_close
        if self.do_logging:
            print("\nstarting logger in subprocess...")
            self.background_listen_process = subprocess.Popen(["python3","FoGSE/listening.py", configfile])
            # using QProcess for this because it cleans up correctly on exit, unlike 
            # self.background_listen_process = QProcess()
            # self.background_listen_process.start("python3", ["FoGSE/listening.py", configfile])
            print("started listen for downlink\n")
            time.sleep(2)
            # sleep so the subprocess can start
            
        # connect local socket
        self.unix_local_socket.connect(self.unix_remote_socket_path)
        
        # Use for GUI to send requests to daemon listener thread:
        self._replace_local_socket = ()

        # expected reply length
        self.recv_len = 0

        # track progress through logfile
        self.command_count = 0

    def __del__(self):
        print("cleaning up FormatterUDPInterface")
        if (self.end_background_process_on_close):
            self.background_listen_process.kill()
            print("sent kill to listener process")
            time.sleep(0.5)
        self.unix_local_socket.close()

    def submit_uplink_command(self, system, command):
        message = [system, command]

        if self.deck.validate(message[0], message[1]):
            self.unix_local_socket.send(bytes(message))

            params.DEBUG_PRINT("submitted uplink command: " + str(message))
        else:
            params.DEBUG_PRINT("got bad uplink command! ignoring.")
            return



# free functions (utilities)---todo: move to parameters.py
def get_field_with_name(json_source, name:str):
    for item in json_source:
        if item["name"] == name:
            return item
def get_field_with_hex(json_source, hex:int):
    for item in json_source:
        if int(item["hex"], 16) == hex:
            return item
        
