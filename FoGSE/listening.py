import socket, ipaddress, serial
import os
import sys
import json
import queue
import math
import time
import struct
from datetime import datetime

# todo: migrate this inside systems.json

DOWNLINK_TYPE_ENUM = {
    "pc":   0x00,
    "ql":   0x01,
    "tpx":  0x02,
    "hk":   0x10,
    "pow":  0x11,
    "rtd":  0x12,
    "intro":0x13,
    "stat": 0x14,
    "err":  0x15,
    "none": 0xff
}


class LogFileManager:
    """
    `LogFileManager` is an interface between a raw data stream and its log 
    file. 

    This object assumes an 8-byte header on all data in this format: 
        <sending system>
        <number of expected packets MSB>
        <number of expected packets LSB>
        <this packet's index MSB>
        <this packet's index LSB>
        <data type in this frame> (see `DOWNLINK_TYPE_ENUM` for options)
        <reserved>
        <reserved>

    Packets have their headers removed and are buffered into a full frame 
    before frames are written to disk.

    Because this is a raw binary file, each data frame is assumed to be fixed 
    width. 
    """

    def __init__(self, filepath: str, system: int, data: int, frame_len: int,
                 payload_len: int):
        """
        Construct a new instance of `LogFileManager`.

        Parameters
        ----------
        filepath : str
            Path to the log file to be used for storage. Provided file WILL BE 
            OVERWRITTEN.

        system : int
            The system ID code (one byte) this `LogFileManager` will expect in 
            the raw packet header.

        data : int
            The data ID code (one byte) this `LogFileManager` will expect in 
            the raw packet header. See `DOWNLINK_TYPE_ENUM` for a list of 
            detected raw data types.

        frame_len : int
            The number off received bytes per complete frame.

        payload_len : int
            The length of the payload portion of the packet, i.e. the total 
            packet length minus header length (8 bytes).

        Raises
        ------
        RuntimeError : if arguments are out-of-bounds, or if provided path to 
            log file cannot be opened.
        """
        self.filepath = filepath
        try:
            self.file = open(filepath, "wb")
        except:
            print("can't open log file at ", self.filepath)
            raise RuntimeError

        if system > 255:
            print("system ID must be 1 byte wide")
            raise RuntimeError
        if data > 255:
            print("data ID must be 1 byte wide")
            raise RuntimeError

        self.system = system
        self.data = data
        self.frame_len = frame_len
        self.payload_len = payload_len
        self.frame = bytearray(self.frame_len)
        self.queued = [0]*math.ceil(self.frame_len/self.payload_len)

        print("payload len:\t", self.payload_len)
        print("frame len:\t", self.frame_len)
        print("queued len:\t", len(self.queued))

    def enqueue(self, raw_data: bytearray):
        """
        Adds raw data to queue for file write.

        Removes headers and queues raw data from packets until a whole 
        frame has been completed. Once a frame is completed it is written 
        to the disk.

        Parameters
        ----------
        raw_data : bytearray
            Raw packet (e.g. received on socket) to add to queue. Should 
            include valid 8-byte header.

        Raises
        ------
        KeyError : if header cannot be parsed.
        """
        if raw_data[0] != self.system:
            print("Log queue got bad system code!")
            raise KeyError
        if raw_data[5] != self.data:
            print("Log queue got bad data code!")
            raise KeyError

        npackets = int.from_bytes(raw_data[1:3], byteorder='big')
        ipacket = int.from_bytes(raw_data[3:5], byteorder='big')

        if ipacket <= npackets:
            # add this packet to the queue, mark it as queued
            
            if self.queued[0]:
                # if the first element in the frame is there (so CdTe doesn't get bad frames)
                if self.queued[ipacket - 1]:
                    # if this element already exists in the packet
                    print("for",raw_data[0],"overwritten by",ipacket-1,"queued:",self.queued)
                    self.write()
                    self.add_to_frame(raw_data)
                    return True
            
            self.add_to_frame(raw_data)
                
            if all(entry == 1 for entry in self.queued):
                self.write()
                return True
            else:
                return False
        else:
            print("Logging got bad packet number: ", ipacket, " for max index ", npackets)
            raise KeyError

    def add_to_frame(self, packet:bytearray):
        npackets = int.from_bytes(packet[1:3], byteorder='big')
        ipacket = int.from_bytes(packet[3:5], byteorder='big')
        this_index = (ipacket - 1)*self.payload_len
        distance = min(len(packet[8:]), self.frame_len)
        self.frame[this_index:(this_index + distance)] = packet[8:]
        # if ipacket == npackets == 1:
        #     print("singleton frame:")
        #     print(packet[:8])
        #     print("packet length",len(packet))
        #     print(self.frame)
        #     print(ipacket, this_index, distance)
        self.queued[ipacket - 1] = 1
        # print(self.queued)
                
    def write(self):
        """
        Writes data in `self.queue` to `self.file`, then refreshes queue.
        """
        self.file.write(self.frame)
        self.file.flush()
        print("wrote " + str(len(self.frame)) + " bytes to " + self.filepath)
        self.frame = bytearray(self.frame_len)
        self.queued = [0]*len(self.queued)



class Listener():
    """
    `Listener` provides an interface between the local machine and a 
    remote (e.g. Formatter) computer.
     
    This object supports local logging of received raw data to file, 
    and can forward commands to the remote computer.

    .. mermaid::
        flowchart LR
            formatter["Formatter"]
            listener["Listener"]
            logs["Log files"]
            gse["GSE"]
            formatter--raw data-->listener
            listener--raw frames-->logs
            listener--commands-->formatter
            gse--commands-->listener
            logs--raw frames-->gse
            
    """
    def __init__(self, json_config_file="foxsi4-commands/systems.json",
                 local_system="gse", remote_system="formatter"):
        """
        Creates a `Listener` instance.

        Parameters
        ----------
        
         json_config_file : str
            Path to valid configuration JSON file. See 
            `foxsi4-commands/systems.json` for reference. Local socket,
            file naming, and log file indexing information will be 
            derived from this file. JSON content should be an array of
            fields, each field containing at least a `name` and `hex`
            attribute.
        
        local_system : str
            The `name` key to search for in `json_config_file` to define
            and set up sockets and path names in the local system.
        
        remote_system : str
            The `name` key to search for in `json_config_file` to define
            and set up the remote system.

        Raises
        ------
        RuntimeError : if required JSON fields cannot be found, or log files
        or folders cannot be created.
        """

        with open(json_config_file, "r") as json_config:
            json_dict = json.load(json_config)
            self.local_system_config = self.get_system_dict(local_system,
                                                            json_dict)
            self.remote_system_config = self.get_system_dict(remote_system,
                                                             json_dict)
            self.uplink_system_config = self.get_system_dict("uplink",
                                                             json_dict)

            if self.local_system_config is None or \
                    self.remote_system_config is None or \
                        self.uplink_system_config is None:  
                print("can't access system in provided JSON!")
                raise RuntimeError

            if self.local_system_config["ethernet_interface"]["protocol"] != "udp":
                print("can't handle non-UDP remote interface!")
                raise RuntimeError

            # constant header size for packets.
            self.header_size = 8
            self.max_receive_size = (self.local_system_config
                                     ["ethernet_interface"]
                                     ["max_payload_bytes"] - self.header_size)
            try:
                now = datetime.now()
                now_str = str(now.day) + "-" + str(now.month) + "-" + str(now.year) + \
                    "_" + str(now.hour) + "-" + str(now.minute) + \
                    "-" + str(now.second)
                self.start = now
                self.log_in_folder = os.path.join(
                    self.local_system_config["logger_interface"]["log_received_folder"], now_str)
                self.log_out_folder = os.path.join(
                    self.local_system_config["logger_interface"]["log_sent_folder"], now_str)
                if not os.path.exists(self.log_in_folder):
                    os.makedirs(self.log_in_folder)
                    print("created downlink log folder:\t", self.log_in_folder)
                if not os.path.exists(self.log_out_folder):
                    os.makedirs(self.log_out_folder)
                    print("created uplink log folder:\t", self.log_out_folder)

                self.log_out_file = os.path.join(
                    self.log_out_folder, "uplink.log")
                self.log_out = open(self.log_out_file, "wb")
                self.downlink_catch_file = os.path.join(
                    self.log_in_folder, "catch.log")
                self.downlink_catch = open(self.downlink_catch_file, "w")
                self.downlink_lookup = self.make_log_dict(json_dict)

            except KeyError:
                print("can't create log files!")
                raise RuntimeError

            self.unix_socket_path = self.local_system_config["logger_interface"]["unix_listen_socket"]
            try:
                os.unlink(self.unix_socket_path)
            except OSError:
                if os.path.exists(self.unix_socket_path):
                    raise RuntimeError
                
            try:
                self.uplink_port_path = self.local_system_config["logger_interface"]["uplink_device"]
                
                self.uplink_port = serial.Serial(
                    self.uplink_port_path,
                    baudrate=self.uplink_system_config["uart_interface"]["baud_rate"],
                    timeout=1
                )
                print("opened uplink serial port at",self.uplink_port_path)
            except:
                print("could not open uplink serial port at",self.uplink_port_path)

            try:
                self.mcast_group = self.local_system_config["ethernet_interface"]["mcast_group"]
                self.local_recv_address = self.local_system_config["ethernet_interface"]["address"]
            except KeyError:
                self.mcast_group = None
                self.local_recv_address = self.local_system_config["ethernet_interface"]["address"]
            
            self.local_recv_port = self.local_system_config["ethernet_interface"]["port"]
            self.local_recv_endpoint = (self.local_recv_address, self.local_recv_port)
            # todo: populate these correctly from JSON
            self.local_send_address = self.local_system_config["ethernet_interface"]["address"]
            self.local_send_port = self.local_system_config["ethernet_interface"]["port"]
            self.local_send_endpoint = (self.local_send_address, self.local_send_port)

            self.remote_address = self.remote_system_config["ethernet_interface"]["address"]
            self.remote_port = self.local_recv_port
            self.remote_endpoint = (self.remote_address, self.remote_port)

            self.unix_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
            self.unix_socket.bind(self.unix_socket_path)
            self.unix_socket.settimeout(0.001)

            print("listening for command (to forward) on Unix datagram socket at:\t",
                  self.unix_socket_path)
            
            self.local_send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.local_send_socket.bind(("192.168.1.118", 9999))
            self.local_send_socket.connect(self.remote_endpoint)

            # setup UDP interface
            if self.mcast_group is not None and ipaddress.IPv4Address(self.mcast_group).is_multicast:
                print("got multicast address")
                # open the socket for standard use
                self.local_recv_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
                self.local_recv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

                self.local_recv_socket.bind((self.mcast_group, self.local_recv_port))
                mreq = struct.pack('4s4s', socket.inet_aton(self.mcast_group), socket.inet_aton(self.local_recv_address))

                # struct.pack('4sl', osself.mcast_group, int.from_bytes(interface, byteorder='big'))
                self.local_recv_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

                print("listening for downlink (to log) on Ethernet datagram socket at:\t",
                    self.mcast_group + ":" + str(self.local_recv_port))
            
            else:
                # listen on a unicast socket
                self.local_recv_socket = socket.socket(
                    socket.AF_INET, socket.SOCK_DGRAM)
                self.local_recv_socket.bind((self.local_recv_address, self.local_port))
                self.local_recv_socket.connect(self.remote_endpoint)
                print("listening for downlink (to log) on Ethernet datagram socket at:\t",
                    self.local_recv_address + ":" + str(self.local_recv_port))
            
            self.local_recv_socket.settimeout(0.01)
            self.local_send_socket.settimeout(0.001)
            # print("listening for downlink (to log) on Ethernet datagram socket at:\t",
            #       self.local_recv_endpoint[0] + ":" + str(self.local_recv_endpoint[1]))

            print("sending uplink on serial port at:\t",
                  self.uplink_port_path)
            
            self._uplink_message_queue = queue.Queue()

            self.print()

            try:
                self._run_log()
            except KeyboardInterrupt:
                self.__del__()

    def __del__(self):
        # close sockets
        self.unix_socket.close()
        self.local_recv_socket.close()
        self.local_send_socket.close()
        # remove the unix socket file
        # os.remove(self.unix_socket_path)

        # close all log files
        self.log_out.close()
        self.downlink_catch.close()
        for system in self.downlink_lookup.keys():
            for data in self.downlink_lookup[system].keys():
                self.downlink_lookup[system][data].file.close()

    def read_unix_socket_to_queue(self):
        """
        Checks for available commands in local Unix socket.

        If data (of length 2) is available, it is added to the
        uplink queue for later transmission.
        """
        # do not validate, just check length
        try:
            data, sender = self.unix_socket.recvfrom(4096)
            print("queueing", len(data), "bytes")
            if len(data) == 2:
                self._uplink_message_queue.put([data[0], data[1]])
            else:
                print("ignored bad-length uplink command: ", data)
        except socket.timeout:
            return

    def read_local_socket_to_log(self):
        """
        Checks for data present in the local Ethernet socket.

        If data is available, try to log it by looking up a `LogFileManager`
        to use. If no appropriate log file can be found, it is time-tagged
        and added (fully in raw form, including header) to a catch-all log
        file.
        """
        try:
            data, sender = self.local_recv_socket.recvfrom(2048)
            # print("logging", len(data), "bytes")
            if len(data) < 8:
                return
            try:
                self.downlink_lookup[data[0x00]][data[0x05]].enqueue(data)
            except KeyError:
                print("got unloggable packet with header: ", data[:8].hex())
                self.write_to_catch(data)
                return
            except Exception as e:
                print("other error: ", e)
                # todo: dump this in a aggregate log
        except socket.timeout:
            # print("read timed out")
            return

    def _run_log(self):
        """
        Main loop that checks for data from both Unix and Ethernet sockets.

        Delegates logging of Ethernet raw data to `self.read_local_socket_to_log()`
        and queueing of Unix socket commands to `self.read_unix_socket_to_queue()`.
        """
        # with self.unix_socket:
        while True:
            self.read_unix_socket_to_queue()
            # handle any queued requests to uplink commands:
            while self._uplink_message_queue.qsize() > 0:
                # apparently queues are thread safe.

                # pop command from the front of the list (FIFO):
                message = []
                try:
                    message = self._uplink_message_queue.get(block=False)
                except queue.Empty:
                    print("uplink queue already empty!")

                # expect all `command` to be <system> <command> `int` pairs
                try:
                    if len(message) == 2:
                        print(message)
                        # print(self.local_send_socket.getsockname())
                        # print(self.local_send_socket.getpeername())
                        # self.local_send_socket.sendall(bytes(message))
                        self.uplink_port.write(bytes(message))
                        print("transmitted " +
                                str(message) + " to Formatter on", self.local_send_endpoint[0], ":", self.local_send_endpoint[1])
                    else:
                        print("found bad uplink command in queue! discarding.")
                except Exception as e:
                    print("couldn't send uplink command! ignoring.")
                    print("\tException:",e)
                    continue
            self.read_local_socket_to_log()
            # time.sleep(0.01)

    def get_system_dict(self, name: str, json_dict: dict):
        """
        Looks up the JSON `dict` in provided `json_dict`.

        Parameters
        ----------
        json_dict : dict
            A JSON dictionary (hopefully) containing fields with attribute `name`.

        Returns
        -------
        None or dict : The JSON field containing the `name` key, if one exists.
        """
        for element in json_dict:
            try:
                if element["name"] == name:
                    return element
            except:
                continue
        return None

    def make_log_dict(self, json_dict):
        """
        Creates `dict` of `dict` mapping `int`s to `LogFileManager`.

        First key is the unique hex code for a system; second key is
        the unique hex code for a raw data type generated by that system
        (see `DOWNLINK_TYPE_ENUM`).

        Parameters
        ----------
        json_dict : dict
            JSON à la foxsi4-commands/systems.json, containing fields
            which contain attributes `name` and `hex`.  
        """
        lookup = {}
        for element in json_dict:
            name = element["name"]
            addr = int(element["hex"], 16)
            rbif = self.get_ring_buffer_interface(element)
            if type(rbif) is dict:
                lookup[addr] = {}
                for key in rbif.keys():
                    try:
                        filename = name + "_" + key + ".log"
                        pathname = os.path.join(self.log_in_folder, filename)

                        log_info = LogFileManager(
                            pathname,
                            addr,
                            DOWNLINK_TYPE_ENUM[key],
                            int(rbif[key]["ring_frame_size_bytes"], 16),
                            self.max_receive_size
                        )
                        lookup[addr][DOWNLINK_TYPE_ENUM[key]] = log_info
                        print("opened downlink log: ", log_info.filepath)
                    except Exception as e:
                        print(e)
                        print("\tcouldn't create log dictionary for ", name, key)
        return lookup

    def get_ring_buffer_interface(self, json_dict):
        try:
            return json_dict["ring_buffer_interface"]
        except KeyError:
            for key in json_dict.keys():
                try:
                    if type(json_dict[key]) is dict:
                        return json_dict[key]["ring_buffer_interface"]
                except KeyError:
                    continue
            return None

    def write_to_catch(self, data: bytes):
        """
        Writes raw data to catch-all log file.

        To be used if a dedicated log file cannot be found.
        Raw data bytes will be time-tagged at the start of the line and encoded
        as UTF-8 for storage. Packets are newline-delimited.

        Parameters
        ----------
        data : bytes
            The raw data stream to write to the file.

        """
        delta = datetime.now() - self.start
        header = "[" + str(delta) + "]" + " "
        content = str(data.hex()) + "\n"
        self.downlink_catch.write(header + content)
        self.downlink_catch.flush()
        print("wrote " + str(len(data)) +
              " bytes to " + self.downlink_catch_file)

    def print(self):
        for system in self.downlink_lookup.keys():
            for data in self.downlink_lookup[system].keys():
                print(self.downlink_lookup[system][data].system,
                      self.downlink_lookup[system][data].data)


if __name__ == "__main__":
    print("starting listener...")
    pass_arg = ""
    if len(sys.argv) == 2:
        print(sys.argv[1])
        pass_arg = sys.argv[1]
        log = Listener(pass_arg)
    else:
        Listener()
