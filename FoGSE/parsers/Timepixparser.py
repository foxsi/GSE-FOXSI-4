# #timepix_parser.py
# #V1.1 - No flag readers 
# #V1.2 - Untested 12/20
# #V1.3 - Updated to load a text-log file of telemetry - logs generated from " parser_generate_frames.py"


dirt = './fake_data_for_parser/'
													# change to your local directory where the binary files are held.

def get_raised_flags(binary_flags):
    binary_flags = binary_flags[2:]  # Remove the '0b' prefix
    raised_flags = [i + 1 for i, bit in enumerate(reversed(binary_flags)) if bit == '1']
    return raised_flags

#################################################################################
# filename = 'example_timepix_frame.bin' 				# reading from a single file 

# with open(dirt+filename, 'rb') as file:
#     combined_binary_data = file.read()

def timepix_parser(bin_data):
    read_rates_packet = bin_data[:4]
    flag_byte_packet = bin_data[4]
    mean_tot = read_rates_packet[0] | (read_rates_packet[1] << 8)
    flx_rate = read_rates_packet[2] | (read_rates_packet[3] << 8)
    flags = flag_byte_packet
    print("Mean ToT = {}".format(mean_tot))
    print("flux rate = {}".format(flx_rate))
    print(f"Flags = {get_raised_flags(bin(flags))}")
    return mean_tot, flx_rate, get_raised_flags(bin(flags))

# #################################################################################
# filename = 'example_timepix_multiframe.bin'  	 # reading from multi-frame file 

# with open(dirt+filename, 'rb') as file:
#     combined_binary_data = file.read()

# packet_size = 5  								 # for the 4 bytes of read rates and 1 bytes for the flag  
# for i in range(0, len(combined_binary_data), packet_size):
#     current_packet = combined_binary_data[i:i + packet_size]
#     read_rates_packet = current_packet[:4]
#     flag_byte_packet = current_packet[4]
#     mean_tot = read_rates_packet[0] | (read_rates_packet[1] << 8)
#     flx_rate = read_rates_packet[2] | (read_rates_packet[3] << 8)
#     flags = flag_byte_packet

#     # Print the extracted information
#     print("Mean ToT = {}".format(mean_tot))
#     print("Flux rate = {}".format(flx_rate))
#     print("Flags = {}".format(bin(flags)))
#     print("------")  


















# # for readrates packet 
# class ReadRatesPacket:  
#     def __init__(self, mean_tot: int = 0, flx_rate: int = 0):
#         self.mean_tot = mean_tot  					# 2-byte integer (0-1022)
#         self.flx_rate = flx_rate  					# 2-byte integer (four digits)

# # for read all housekeeping packet 
# class ReadALLHKPacket:
#     def __init__(self, board_t1: int = 0, board_t2: int = 0, asic_voltages: list = [0, 0, 0, 0],
#                  asic_currents: list = [0, 0, 0, 0], fpga_values: list = [0, 0, 0], rpi_storage_fill: int = 0):
#         self.board_t1 = board_t1            		# 3-digit integer
#         self.board_t2 = board_t2            		# 3-digit integer
#         self.asic_voltages = asic_voltages  		# List of 4 integers (each with a max of 5 digits)
#         self.asic_currents = asic_currents  		# List of 4 integers (each with a max of 4 digits)
#         self.fpga_values = fpga_values  			# List of 3 integers (each with a max of 4 digits)
#         self.rpi_storage_fill = rpi_storage_fill    # 3-digit integer

# # for read temp packets 
# class ReadTempPacket:
#     def __init__(self, fpgat: int = 0, board_t1: int = 0, board_t2: int = 0):
#         self.fpgat = fpgat  						# 3 digits
#         self.board_t1 = board_t1  					# maximum 3 digits
#         self.board_t2 = board_t2  					# maximum 3 digits


# def unpack_read_rates_packet(packet):  #readrates 4 bytes
#     data = ReadRatesPacket()
#     data.mean_tot = packet[0] | (packet[1] << 8)
#     data.flx_rate = packet[2] | (packet[3] << 8)
#     return data


# def unpack_read_all_hk_packet(packet): #hk 27 bytes 
#     data = ReadALLHKPacket() #DEFINED IN EXAMPLE BELOW 
#     data.board_t1 = packet[0] + (packet[1] << 8)
#     data.board_t2 = packet[2] + (packet[3] << 8)
#     for i in range(4):									    	# Unpacking ASIC voltages (5 digits each)
#         data.asic_voltages[i] = packet[4 + i * 5] + (packet[5 + i * 5] << 8) + (packet[6 + i * 5] << 16)
#     for i in range(4):											# Unpacking ASIC currents (4 digits each)
#         data.asic_currents[i] = packet[7 + i * 4] + (packet[8 + i * 4] << 8)	
#     for i in range(3):   										# Unpacking FPGA voltages (4 digits each)
#         data.fpga_values[i] = packet[9 + i * 4] + (packet[10 + i * 4] << 8)
#     data.rpi_storage_fill = packet[11] + (packet[12] << 8)      # Unpacking RPI storage fill (3 digits)   
#     return data

# def unpack_read_temp_packet(packet): #temp 9 bytes 
#     data = ReadTempPacket()
#     data.fpgat = packet[0] + (packet[1] << 8)     	# Unpacking FPGA T (3 digits)
#     data.board_t1 = packet[2] + (packet[3] << 8)    # Unpacking Board T1 (3 digits)  
#     data.board_t2 = packet[4] + (packet[5] << 8)    # Unpacking Board T2 (3 digits)
#     return data


# max_packet_size = 27
# received_data = b''

# while True:
#     received_data += ser.read(max_packet_size - len(received_data)) # Read data from the serial port
#     sleep(0.03)
#     while len(received_data) > 0: 									# Determine the type of packet based on its size
#         if len(received_data) >= 27: 								# hk packet             
#             received_data = received_data[0:27]
#             unpacked_data = unpack_read_all_hk_packet(list(received_data)) 
#             print("Received BoardT1:", received_data.board_t1)
# 			print("Received BoardT2:", received_data.board_t2)
# 			print("Received ASIC Voltages:", received_data.asic_voltages)
# 			print("Received ASIC Currents:", received_data.asic_currents)
# 			print("Received FPGA Voltages:", received_data.fpga_values)
# 			print("Received RPI Storage Fill:", received_data.rpi_storage_fill)

#         elif len(received_data) >= 4: 								# readrates packet
#             # process_received_packet(received_data[:4])
#             # received_data = received_data[4:]
#             unpacked_data = unpack_read_rates_packet(list(received_data))
#             print("Received MeanToT:", received_data.mean_tot)
# 			print("Received FlxRate:", received_data.flx_rate)
#         elif len(received_data) >= 9: #temp packet
#             # process_received_packet(received_data[:9])
#             # received_data = received_data[9:]
#             unpacked_data = unpack_read_temp_packet(list(received_data))
#             print(f"Unpacked Data: FPGA T={unpacked_data.fpgat}, BoardT 1={unpacked_data.board_t1}, BoardT2={unpacked_data.board_t2}")

#         else:
#         	print("data length unmatching")
#         	print(len(received_data))
#             break

