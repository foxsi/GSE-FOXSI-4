import sys, os, time, socket
import scapy.all
import numpy as np
from pprint import pprint

class CaptureTransmitter:
    def __init__(self, capture: str, address: str, port: int):
        print("\topening capture...")
        # capture = pyshark.FileCapture(input_file=capture, include_raw=True, use_json=True)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((address, port))

        capture = scapy.all.rdpcap(capture)
        
        print("\tfound",len(capture),"saved packets")
        times = []
        raw_packets = []
        print("\tparsing capture...")
        packet_index = 0
        this_fragment_id = None
        this_fragment_offset = None
        this_frame = {}
        this_frame_time = []
        for packet in capture:
            if scapy.all.IP in packet and packet[scapy.all.IP].dst == "224.1.1.118":
                flags = int(packet[scapy.all.IP].flags)
                # print("counter:",packet_index,", flags:",flags)
                if flags == 0x02:
                    # this is a non-fragmented packet, just add it to the list as usual.
                    # print("\tfound packet")
                    payload = packet[scapy.all.UDP].payload
                    raw_packets.append(bytes(payload))
                    # print("\t\tfor flag 0x02, length:",len(bytes(payload)))
                    times.append(float(packet.time))
                    packet_index += 1
                
                if flags == 0x01:
                    # print("\tfound fragmented packet")
                    this_fragment_id = packet[scapy.all.IP].id
                    this_fragment_offset = packet[scapy.all.IP].frag
                    payload = packet[scapy.all.IP].payload
                    this_frame[this_fragment_offset] = bytes(payload)[8:]
                    # print("\t\tfor flag 0x01, length:",len(bytes(payload)))
                    this_frame_time.append(float(packet.time))

                if flags == 0x00:
                    # print("\tfound terminal fragmented packet")
                    # this is the last fragment for the fragment id.
                    if packet[scapy.all.IP].id == this_fragment_id:
                        this_fragment_offset = packet[scapy.all.IP].frag
                        payload = packet[scapy.all.IP].payload
                        this_frame[this_fragment_offset] = bytes(payload)
                        # print("\t\tfor flag 0x00, length:",len(bytes(payload)))
                        this_frame_time.append(float(packet.time))

                        # assemble the frame
                        this_frame = dict(sorted(this_frame.items()))
                        this_packet = bytearray()
                        for key in this_frame.keys():
                            this_packet.extend(this_frame[key])

                        # print("\tbuilt fragmented packet of length", len(this_packet))
                        this_time = max(this_frame_time)

                        # write the frame to raw_packets and time to times
                        times.append(this_time)
                        raw_packets.append(bytes(this_packet))

                        # clear the fragment-tracking data
                        this_fragment_id = None
                        this_fragment_offset = None
                        this_frame = {}
                        this_frame_time = []

                        # increment packet counter
                        packet_index += 1
                    else: 
                        print("failed to rebuild fragmented packet! Retained id", this_fragment_id,"but found",packet[scapy.all.IP].id)
                        pprint(packet)
        
        print("\tfound",len(raw_packets),"packets to send")
        # times = times[:packet_index]
        # raw_packets = raw_packets[:packet_index]
        duration = times[-1] - times[0]
        print("\tpacket transmission will last", duration, "seconds")
        key = input("> Press Q to quit, or another key to start sending: ")
        if key == 'q' or key == 'Q':
            print("\texiting.")
            sys.exit()

        print("\tstarting transmission.")
        last_time = 0
        negative_counter = 0
        total_start = time.time()
        for i, packet in enumerate(raw_packets):
            if i > 0:
                delay = times[i] - times[i - 1]
                elapsed = time.time() - last_time
                sleepy_time = max(delay - elapsed, 0.0)
                if delay > 5.0:
                    print("\tsleeping", delay - elapsed, "seconds")
                if sleepy_time == 0.0:
                    negative_counter += 1
                time.sleep(sleepy_time)

            # self.socket.sendto(packet, ("224.1.1.118", 9999))
            # print("sending",packet.hex()[:8])
            last_time = time.time()
        
        print("\ttotal transmission time:", time.time() - total_start, "seconds")
        print("\tfound", negative_counter, "timer overruns.")

        print("\ttransmission complete.")



if __name__ == '__main__':
    if len(sys.argv) > 3:
        print("opening capture file", sys.argv[1])
        CaptureTransmitter(sys.argv[1], sys.argv[2], int(sys.argv[3]))
    else:
        print("run like this:\n\t> python3 FoGSE/transmitFromCapture.py path/to/your.pcap local-ip local-port")