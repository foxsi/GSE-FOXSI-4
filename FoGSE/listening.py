import socket, ipaddress, serial
import os
import sys
import json
import queue
import math
import time
import struct
from datetime import datetime

from FoGSE.utils import get_system_dict, get_ring_buffer_interface

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
    "reply":0x30,
    "none": 0xff
}

class LogFileManager:
    """
    `LogFileManager` is an interface between a raw data stream and its
    log file. 

    This object assumes an 8-byte header on all data in this format: 
        0. <sending system> 
        1. <number of expected packets MSB> 
        2. <number of expected packets LSB> 
        3. <this packet's index MSB> 
        4. <this packet's index LSB> 
        5. <data type in this frame> (see `DOWNLINK_TYPE_ENUM` for
           options) 
        6. <frame counter MSB> 
        7. <frame counter LSB> 

    Packets have their headers removed and are buffered into a full
    frame before frames are written to disk.

    Because this is a raw binary file, each data frame is assumed to be
    fixed width. 
    """

    def __init__(self, filepath: str, system: int, data: int, frame_len: int,
                 payload_len: int):
        """
        Construct a new instance of `LogFileManager`.

        Parameters
        ----------
        filepath : str
            Path to the log file to be used for storage. Provided file
            WILL BE OVERWRITTEN.

        system : int
            The system ID code (one byte) this `LogFileManager` will
            expect in the raw packet header.

        data : int
            The data ID code (one byte) this `LogFileManager` will
            expect in the raw packet header. See `DOWNLINK_TYPE_ENUM`
            for a list of detected raw data types.

        frame_len : int
            The number off received bytes per complete frame.

        payload_len : int
            The length of the payload portion of the packet, i.e. the
            total packet length minus header length (8 bytes).

        Raises
        ------
        RuntimeError : if arguments are out-of-bounds, or if provided
        path to 
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
        self.packets_per_frame = math.ceil(self.frame_len/self.payload_len)
        self.frames = []

        print("payload len:\t", self.payload_len)
        print("frame len:\t", self.frame_len)

    def add_frame(self, frame_counter:int):
        """
        Add a `CurrentFrame` to the `self.frames` list with the provided
        `frame_counter` value.

        This method will add a new, blank `CurrentFrame` object to
        `self.frames`, keyed to the provided `frame_counter` (and return
        `True`), unless a `CurrentFrame` already exists with the same
        `frame_counter` value (in which case `False` is returned). 

        Parameters
        ----------
        
        frame_counter: int
            A 2-byte counter or identifier for this frame.
        """
        for frame in self.frames: # check that there is no frame with this frame_counter already in the list of frames
            if frame.get_frame_counter() == frame_counter:
                return False
        self.frames.append(CurrentFrame(
            self.frame_len, 
            self.packets_per_frame,
            self.payload_len,
            frame_counter
        ))

        return True
    
    def delete_frame(self, frame_counter:int):
        """
        Delete the `CurrentFrame` with matching `frame_counter` from the
        `self.frames` list.

        If there are no items in `self.frames` for which
        `CurrentFrame.frame_counter` matches the provided argument,
        nothing will happen.

        Parameters
        ----------
        
        frame_counter: int
            A 2-byte counter or identifier for this frame.
        """
        index = None
        for i, frame in enumerate(self.frames):
            if frame.get_frame_counter() == frame_counter:
                index = i
        if index is not None:
            del self.frames[index]

    def pop_frame(self, frame_counter:int):
        """
        Pop the `CurrentFrame` with matching `frame_counter` from the
        `self.frames` list.

        "Pop" means return a copy of the `CurrentFrame` object and
        delete it from the list. If there are no items in `self.frames`
        for which `CurrentFrame.frame_counter` matches the provided
        argument, nothing will happen (and `None` will be returned).

        Parameters
        ----------
        
        frame_counter: int
            A 2-byte counter or identifier for this frame.
        """
        index = None
        for i, frame in enumerate(self.frames):
            if frame.get_frame_counter() == frame_counter:
                index = i
                break;
        if index is not None:
            out = self.frames.pop(index)
            return out
        
    def enqueue(self, raw_data: bytearray):
        """
        Adds raw data to queue for file write.

        Removes headers and queues raw data from packets until a whole
        frame has been completed. Once a frame is completed it is
        written to the disk.

        This method will attempt lookup for an existing, partially saved
        frame in `self.frames` (using the frame index byte in the
        received header). If a corresponding frame is found, attempt to
        insert the packet in it. If not, create a new `CurrentFrame`
        object for this frame counter and populate it. If this packet
        completes a frame, the frame is written to disk. If a
        `CurrentFrame` exists already for this packet counter and it has
        a packet in this packet's position, that frame will be dumped to
        disk and a new frame will be started with this packet in it.

        Parameters
        ----------
        raw_data : bytearray
            Raw packet (e.g. received on socket) to add to queue. Should
            include a valid 8-byte header.

        Raises
        ------
        KeyError : 
            if header cannot be parsed, or if the system/data type
            identifiers in the header do not match those in this class.
        """

        # unpack the header:
        system = raw_data[0]
        datatype = raw_data[5]
        npackets = int.from_bytes(raw_data[1:3], byteorder='big')
        ipacket = int.from_bytes(raw_data[3:5], byteorder='big')
        iframe = raw_data[7]

        if system != self.system:
            print("Log queue got bad system code!")
            raise KeyError
        if datatype != self.data:
            print("Log queue got bad data code!")
            raise KeyError
        
        frame = None
        for f in self.frames:
            if f.get_frame_counter() == iframe:
                frame = f
                break;
        
        if frame is not None: # the received frame counter exists in our list already. Try to insert packet.
            p_success = frame.insert(ipacket, raw_data[8:])
            if not p_success:
                print("failed to add packet to frame!")
                print("\tfor",system,"overwritten by",ipacket,"queued:",frame.queued)

                self.write(iframe) # dump current frame (which presumably contains some errors)
                f_success = self.add_frame(iframe)
                if not f_success:   # shouldn't happen, we just removed this frame and created a new one
                    print("failed to add new frame!")
                    # raise BufferError

                p_success = frame.insert(ipacket, raw_data[8:])
                if not p_success:   # shouldn't happen, this is a brand new frame; shouldn't be any conflicts.
                    print("failed to add packet to new frame!")
                    # raise BufferError

        else: # the received frame counter doesn't exist in our list. Create it and try to insert packet.
            f_success = self.add_frame(iframe)
            if not f_success:   # shouldn't happen, we already checked if the frame exists.
                print("failed to add new frame!")
                # raise BufferError
            frame = self.frames[-1]
            p_success = frame.insert(ipacket, raw_data[8:])
            if not p_success:   # shouldn't happen, this is a brand new frame; shouldn't be any conflicts.
                print("failed to add packet to new frame!")
                # raise BufferError
            
        if frame.done:
            self.write(iframe)
            return True
        else:
            return False
                
    def write(self, frame_counter:int):
        """
        Writes data in `self.queue` to `self.file`, then refreshes
        queue.
        """
        outframe = self.pop_frame(frame_counter)
        self.file.write(outframe.data)
        self.file.flush()
        print("wrote frame count " + str(frame_counter) + " to " + self.filepath)
    
    
class CurrentFrame():
    """
    `CurrentFrame` is an object to track a frame of data being
    reassembled from individual packets.

    In the downlink data stream, large data frames (such as CdTe or CMOS
    images or event lists) are fragmented into smaller packets to
    facilitate transmission. These packets contain an 8-byte header,
    which may contain a source frame identifier (a number describing the
    frame that was originally broken up into packets) in the last two
    header bytes.

    Attributes
    ----------
    
    done: Bool
        Flag `True` if the frame has been completed, i.e. all packets
        accounted for.

    frame_len: int
        Length, in bytes, of the full frame of data. 
    
    packet_count: int
        The number of packets expected to complete the frame. Maximum
        value is 0xffff.

    payload_len: int
        Length, in bytes, of each packet's payload (a payload is the
        packet without the 8-byte header).
    
    frame_counter: int
        A 2-byte wide identifier for this frame. Nominally this is a
        frame counter on the Formatter-side, but could be replaced with
        a CRC16 or other "random" identifier value. The idea is for all
        the packets that reconstitute this frame to share the same
        `frame_counter` value in their header. Maximum value is Maximum
        value is 0xffff.
    """
    def __init__(self, frame_len:int, packet_count:int, payload_len:int, frame_counter:int):
        self.done = False   # flag indicating frame is complete

        if packet_count > 0xffff:
            print("CurrentFrame constructed with too large packet_count!")
            raise ValueError
        if frame_counter > 0xffff:
            print("CurrentFrame constructed with too large frame_counter!")
            raise ValueError
        
        self.frame_len = frame_len
        self._frame_counter = frame_counter
        self.packet_count = packet_count
        self.payload_len = payload_len

        self.data = bytearray(frame_len)
        self.queued = [False]*packet_count

    def insert(self, ipacket:int, payload:bytearray):
        """
        Put the payload of a packet (header has been removed) into the
        `CurrentFrame`. 

        This method will search `self.queued` for the provided
        `ipacket`. If no packet in that index has been queued yet, this
        one will be added to the frame and its `self.queued` flag will
        be set. If this is the packet that completes the `CurrentFrame`
        (such that `all(self.queued) == True`), the `self.done` flag
        will be set.

        Returns
        -------
        Bool
            The return value is `True` if there is no packet yet in this
            position in `self.queued`, and `False` otherwise; i.e. if
            this packet *would* overwrite an existing packet in the
            frame.

        Parameters
        ----------
        ipacket: int
            A ONE-INDEXED (not zero-index) packet number, locating this
            packet in the frame it belongs to.

        payload: bytearray
            The beheaded packet contents that were sent by the formatter
            to the ground. The universal 8-byte header should have been
            removed.
        """
        
        if self.queued[ipacket - 1] == True: # indicate to caller that this packet has already been received for this frame
            return False
        
        # find byte position in overall frame
        frame_byte_index = (ipacket - 1)*self.payload_len
        # length to write in overall frame. If the payload is bigger
        # than the frame, truncate it.
        distance = min(len(payload), self.frame_len)
        self.data[frame_byte_index:(frame_byte_index + distance)] = payload

        self.queued[ipacket - 1] = True
        if all(self.queued):
            self.done = True
        
        return True

    def get_frame_counter(self):
        return self._frame_counter

class Listener():
    """
    `Listener` provides a logging interface between the local machine
    and a remote (e.g. Formatter) computer.
     
    This object supports local logging of received raw data to file, and
    can forward commands to the remote computer. Based on an 8-byte
    header the Formatter prepends to all downlink messages, the can
    identify and sort received packets into specific log files and
    formats.

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
    def __init__(self, json_config_file=os.path.join(__file__, "..", "..", "foxsi4-commands", "systems.json"),
                 command_interface="uplink", local_system="gse", 
                 remote_system="formatter"):
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
        RuntimeError : if required JSON fields cannot be found, or log
        files or folders cannot be created.
        """

        json_config_file = os.path.realpath(json_config_file)
        with open(json_config_file, "r") as json_config:
            json_dict = json.load(json_config)
            self.local_system_config = get_system_dict(local_system,
                                                       json_dict)
            self.remote_system_config = get_system_dict(remote_system,
                                                        json_dict)
            self.uplink_system_config = get_system_dict("uplink",
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
                self.log_out = open(self.log_out_file, "w")
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
            
            # initialize these, in case they are populated by
            # `.set_command_interface()`
            self.uplink_port_path = None
            self.uplink_port = None
            self.local_recv_socket = None
            
            try:
                self.mcast_group = self.local_system_config["ethernet_interface"]["mcast_group"]
            except KeyError:
                self.mcast_group = None
            self.local_recv_address = self.local_system_config["ethernet_interface"]["address"]
            
            self.local_recv_port = self.local_system_config["ethernet_interface"]["port"]
            self.local_recv_endpoint = (self.local_recv_address, self.local_recv_port)
            # todo: populate these correctly from JSON

            self.remote_address = self.remote_system_config["ethernet_interface"]["address"]
            self.remote_port = self.local_recv_port
            self.remote_endpoint = (self.remote_address, self.remote_port)
            
            self.unix_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
            self.unix_socket.bind(self.unix_socket_path)
            self.unix_socket.settimeout(0.001)

            self.set_command_interface(command_interface)

            print("listening for command (to forward) on Unix datagram socket at:\t",
                  self.unix_socket_path)
            
            self._uplink_message_queue = queue.Queue()
            # self.print()

            try:
                self._run_log()
            except KeyboardInterrupt:
                self.__del__()

    def __del__(self):
        # close sockets
        self.unix_socket.close()
        self.local_recv_socket.close()
        # remove the unix socket file os.remove(self.unix_socket_path)

        # close all log files
        self.log_out.close()
        self.downlink_catch.close()
        for system in self.downlink_lookup.keys():
            for data in self.downlink_lookup[system].keys():
                self.downlink_lookup[system][data].file.close()

    def set_command_interface(self, interface:str):
        success = False
        if interface == "uplink" or interface == "umbi":
            self.command_interface = interface
            success = self.start_interface()
        
        return success

    def start_interface(self):
        print("self.command_interface", self.command_interface)
        if self.command_interface == "uplink":
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
        else:
            print("ERROR: can only use uplink interface for commanding")
            raise RuntimeError

        # setup UDP interface
        if self.mcast_group is not None and ipaddress.IPv4Address(self.mcast_group).is_multicast:
            print("got multicast address")
            # open the socket for standard use
            self.local_recv_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            self.local_recv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

            self.local_recv_socket.bind((self.mcast_group, self.local_recv_port))
            mreq = struct.pack('4s4s', socket.inet_aton(self.mcast_group), socket.inet_aton(self.local_recv_address))

            # struct.pack('4sl', osself.mcast_group,
            # int.from_bytes(interface, byteorder='big'))
            self.local_recv_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

            print("listening for downlink (to log) on Ethernet datagram socket at:\t",
                self.mcast_group + ":" + str(self.local_recv_port))
        
        else:
            # listen on a unicast socket    
            self.local_recv_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.local_recv_socket.bind((self.local_recv_address, self.local_recv_port))
            self.local_recv_socket.connect(self.remote_endpoint)
            print("listening for downlink (to log) on Ethernet datagram socket at:\t",
                self.local_recv_address + ":" + str(self.local_recv_port))
            
        self.local_recv_socket.settimeout(0.01)
        return True
    
    def send_command(self, command:bytes):
        try:
            if self.command_interface == "uplink":
                self.uplink_port.write(command)
                print("transmitted","0x" + command.hex(),"to Formatter via",self.command_interface,self.uplink_port_path)
            
            if self.command_interface == "umbi":
                raise "Ethernet-based commanding has been removed!"
            
            self.write_to_uplink_log(command)
        except Exception as e:
            print("Got Exception while sending uplink command: ", e)
    
    def read_unix_socket_to_queue(self):
        """
        Checks for available commands in local Unix socket.

        If data (of length 2) is available, it is added to the uplink
        queue for later transmission.
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

        If data is available, try to log it by looking up a
        `LogFileManager` to use. If no appropriate log file can be
        found, it is time-tagged and added (fully in raw form, including
        header) to a catch-all log file.
        """
        try:
            data, sender = self.local_recv_socket.recvfrom(2048)
            # print("logging", len(data), "bytes")
            if len(data) < 8:
                return
          
            self.downlink_lookup[data[0x00]][data[0x05]].enqueue(data)
          

            # try:
            #     self.downlink_lookup[data[0x00]][data[0x05]].enqueue(data)
            # except KeyError: print("got unloggable packet with header:
            #     ", data[:8].hex()) self.write_to_catch(data) return
            #     except Exception as e: print("other error: ", e) #
            #     todo: dump this in a aggregate log
        except socket.timeout:
            # print("read timed out")
            return
        except KeyError:
            self.write_to_catch(data)

    def _run_log(self):
        """
        Main loop that checks for data from both Unix and Ethernet
        sockets.

        Delegates logging of Ethernet raw data to
        `self.read_local_socket_to_log()` and queueing of Unix socket
        commands to `self.read_unix_socket_to_queue()`.
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

                # expect all `command` to be <system> <command> `int`
                # pairs
                try:
                    if len(message) == 2:
                        self.send_command(bytes(message))
                    else:
                        print("found bad uplink command in queue! discarding.")
                except Exception as e:
                    print("couldn't send uplink command! ignoring.")
                    print("\tException:",e)
                    continue
            self.read_local_socket_to_log()
            # time.sleep(0.01)

    def make_log_dict(self, json_dict):
        """
        Creates `dict` of `dict` mapping `int`s to `LogFileManager`.

        First key is the unique hex code for a system; second key is the
        unique hex code for a raw data type generated by that system
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
            rbif = get_ring_buffer_interface(element)
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

    def write_to_uplink_log(self, data: bytes):
        """
        Writes uplink commands data to log file.

        Parameters
        ----------
        data : bytes
            The raw command (2 bytes) to write to the file.

        """

        delta = datetime.now() - self.start
        header = "[" + str(delta) + "]" + " "
        content = "0x" + str(data.hex()) + "\n"
        self.log_out.write(header + content)
        self.log_out.flush()
        print("\twrote " + str(len(data)) +
              " bytes to " + self.log_out_file)
        
    def write_to_catch(self, data: bytes):
        """
        Writes raw data to catch-all log file.

        To be used if a dedicated log file cannot be found. Raw data
        bytes will be time-tagged at the start of the line and encoded
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
    config_arg = ""
    interface_arg = ""
    if len(sys.argv) == 3:
        config_arg = sys.argv[1]
        interface_arg = sys.argv[2]
        log = Listener(config_arg, interface_arg)
    if len(sys.argv) == 2:
        config_arg = sys.argv[1]
        log = Listener(config_arg)
    else:
        Listener()
