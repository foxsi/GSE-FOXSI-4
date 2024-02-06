### Functions for CMOS Parser ###
### By Riko Shimizu (SOKENDAI)
### Oct. 25th, 2023
### Updated Nov. 1st, 2023
### Updated Feb. 2nd, 2024
### Updated Feb. 2nd, 2024


# CC = Conmmand Confirmation : 160  B
# HK = House Keeping         : 176  B  ### Size changed (Feb. 2, 2024)
# QL = Quick Look data       : 481 kB
# PC = Photon counting data  : 577 kB

# CC and HK data are downlinked together at 336 B


import numpy as np
from PIL import Image, ImageOps

# Each data has 4B
bytesize = 4

# indices for Commands Confirmation data
CC_indices = {
    'gain_mode': 0,
    'exposureQL': 4,
    'exposurePC': 8,
    'repeat_N': 12,
    'repeat_n':16,
    'gain_even': 20,
    'gain_odd': 24,
    'ncapture': 28,

    'cmos_init': 64,
    'cmos_training': 68,
    'cmos_setting': 72,
    'cmos_start': 80,
    'cmos_stop': 84,

    'ping': 96,

    'enable_double_command': 128,
    'remove_all_data': 132,
    'reboot':136,
    'shutdown': 140
}

# indices for House Keeping data (after commands confirmation data which has 160B)
HK_indices = {
    'line_time': 0 + 160,
    'line_time_at_pps': 4 + 160,

    'cpu_load_average':16 + 160,

    'remaining_disk_size': 20 + 160,

    'software_status': 32 + 160,
    'error_time': 36 + 160,
    'error_flag': 40 + 160,
    'error_training': 44 + 160,
    'data_validity': 48 + 160,

    'sensor_temp': 80 + 160,
    'fpga_temp': 84 + 160,

    'gain_mode': 96 + 160,
    'exposureQL':100 + 160,
    'exposurePC': 104 + 160,
    'repeat_N': 108 + 160,
    'repeat_n':112 + 160,
    'gain_even': 116 + 160,
    'gain_odd': 120 + 160,
    'ncapture': 124 + 160,

    'write_pointer_position_store_data' :128 + 160,
    'read_pointer_position_QL': 160 + 160,
    'data_size_QL': 164 + 160,
    'read_pointer_position_PC': 168 + 160,
    'data_size_PC': 172 + 160
}

# indiced for QL and PC data
QLPC_indices = {
    'line_time': 4,
    'gain': 8,
    'exposure':12
}


# get int values from input data. 
# data has 336B(CC+HK), 481kB(QL), or 577kB(PC)
def toInt(data, index):
    return int.from_bytes(data[index:index+bytesize], byteorder='little')



##### Commnads Confermation 160 B #####

def exposureParameters(data336B):
    gain_mode = toInt(data336B, CC_indices['gain_mode'])
    exposureQL = toInt(data336B, CC_indices['exposureQL'])
    exposurePC = toInt(data336B, CC_indices['exposurePC'])
    repeat_N = toInt(data336B, CC_indices['repeat_N'])
    repeat_n = toInt(data336B, CC_indices['repeat_n'])
    gain_even = toInt(data336B, CC_indices['gain_even'])
    gain_odd = toInt(data336B, CC_indices['gain_odd'])
    ncapture = toInt(data336B, CC_indices['ncapture'])
    return gain_mode, exposureQL, exposurePC, repeat_N, repeat_n, gain_even, gain_odd, ncapture

def operateCMOS(data336B):
    cmos_init = toInt(data336B, CC_indices['cmos_init'])
    cmos_training = toInt(data336B, CC_indices['cmos_training'])
    cmos_setting = toInt(data336B, CC_indices['cmos_setting'])
    cmos_start =  toInt(data336B, CC_indices['cmos_start'])
    cmos_stop = toInt(data336B, CC_indices['cmos_stop'])
    return cmos_init, cmos_training, cmos_setting, cmos_start, cmos_stop

def ping(data336B):
    ping = toInt(data336B, CC_indices['ping'])
    return ping

def discreteCommands(data336B):
    enable_double_command = toInt(data336B, CC_indices['enable_double_command'])
    remove_all_data =  toInt(data336B, CC_indices['remove_all_data'])
    reboot =  toInt(data336B, CC_indices['reboot'])
    shutdown =  toInt(data336B, CC_indices['shutdown'])
    return enable_double_command, remove_all_data, reboot, shutdown


##### House keeping data 352B #####

def time(data336B):
    line_time = toInt(data336B, HK_indices['line_time'])
    line_time_at_pps = toInt(data336B, HK_indices['line_time_at_pps'])
    return line_time, line_time_at_pps

def cpu(data336B):
    cpu_load_average = toInt(data336B, HK_indices['cpu_load_average'])
    return cpu_load_average                             

def disk(data336B):
    remaining_disk_size = toInt(data336B, HK_indices['remaining_disk_size'])
    return remaining_disk_size

def softFpgaStatus(data336B):
    software_status = toInt(data336B, HK_indices['software_status'])
    error_time = toInt(data336B, HK_indices['error_time'])
    error_flag = toInt(data336B, HK_indices['error_flag'])
    error_training = toInt(data336B, HK_indices['error_training'])
    data_validity = toInt(data336B, HK_indices['data_validity'])
    return software_status, error_time, error_flag, error_training, data_validity


# get decimal number from two's complement
def twosComplementToDecimal(bits):
    if bits[0] == '1':  # Negative number
        inverted_bits = ''.join('1' if bit == '0' else '0' for bit in bits)
        decimal_value = int(inverted_bits, 2) + 1
        return -decimal_value
    else:  # Positive number
        return int(bits, 2)

# sensor temp data has 2 byte. 8 bit is integer portion and 8 bit is fractional portion.
def sensorTemp(data4B):
    value = int.from_bytes(data4B, 'little') 
    value = value & 0xFFFF
    sensor_temp = twosComplementToDecimal(bin(value))/(2**8)
    return sensor_temp

# fpga temp data has 12 bit. 8 bit is integer portion and 4 bit is fractional portion.
def fpgaTemp(data4B):
    value = int.from_bytes(data4B, 'little')
    value = value & 0xFFF
    fpga_temp = twosComplementToDecimal(bin(value))/(2**4)
    return fpga_temp

def temperature(data336B):
    sensor_temp = sensorTemp(data336B[HK_indices['sensor_temp']:HK_indices['sensor_temp']+bytesize])
    fpga_temp = fpgaTemp(data336B[HK_indices['fpga_temp']:HK_indices['fpga_temp']+bytesize])
    return sensor_temp, fpga_temp


def currentExposureParameters(data336B):
    gain_mode = toInt(data336B, HK_indices['gain_mode'])
    exposureQL = toInt(data336B, HK_indices['exposureQL'])
    exposurePC = toInt(data336B, HK_indices['exposurePC'])
    repeat_N = toInt(data336B, HK_indices['repeat_N'])
    repeat_n = toInt(data336B, HK_indices['repeat_n'])
    gain_even = toInt(data336B, HK_indices['gain_even'])
    gain_odd = toInt(data336B, HK_indices['gain_odd'])
    ncapture = toInt(data336B, HK_indices['ncapture'])
    return gain_mode, exposureQL, exposurePC, repeat_N, repeat_n, gain_even, gain_odd, ncapture

def downlinkData(data336B):
    write_pointer_position_store_data = toInt(data336B, HK_indices['write_pointer_position_store_data'])
    read_pointer_position_QL = toInt(data336B, HK_indices['read_pointer_position_QL'])
    data_size_QL = toInt(data336B, HK_indices['data_size_QL'])
    read_pointer_position_PC = toInt(data336B, HK_indices['read_pointer_position_PC'])
    data_size_PC = toInt(data336B, HK_indices['data_size_PC'])
    return write_pointer_position_store_data, read_pointer_position_QL, data_size_QL, read_pointer_position_PC, data_size_PC


# # for check -----------
# with open('data336B_test.bin', 'rb') as file:
#     data = file.read()
# gain_mode, exposureQL, exposurePC, repeat_N, repeat_n, gain_even, gain_odd, ncapture = exposureParameters(data)
# print(hex(gain_mode), exposureQL, exposurePC, hex(ncapture))
# # ---------------------


##### QL data 481kB #####

# each pixels have 2 byte (value is 12 bit).
# read each 2 byte and get each pixels' value
def makeDecimalList(data):
    decimal_list = []
    for i in range(0, len(data), 2):
        byte1 = data[i + 1]
        byte2 = data[i]
        decimal_number = byte1 * 256 + byte2
        decimal_list.append(decimal_number)
    return decimal_list

# get QL header(linetime, gain, exposure) and make image.
def QLimageData(data481kB):
    linetime = toInt(data481kB, QLPC_indices['line_time'])
    gain = toInt(data481kB, QLPC_indices['gain'])
    exposureQL = toInt(data481kB, QLPC_indices['exposure'])

    decimal_list = makeDecimalList(data481kB[16:16+491520])
    # Make QL image
    width, height = 512, 480
    pixels = np.array([float(value) for value in decimal_list])

    return linetime, gain, exposureQL, np.reshape(pixels, (height,width))

##### End of QL #####


##### PC data 577kB #####

# get PC header(linetime, gain, exposure) and make image.
def PCimageData(data577kB):
    linetime = toInt(data577kB, QLPC_indices['line_time'])
    gain = toInt(data577kB, QLPC_indices['gain'])
    exposurePC = toInt(data577kB, QLPC_indices['exposure'])

    decimal_list = makeDecimalList(data577kB[16:16+589824])
    # Make PC image
    width, height = 768, 384
    # Set pixel values
    pixels = np.array([float(value) for value in decimal_list])

    return linetime, gain, exposurePC, np.reshape(pixels, (height,width))

##### End of PC #####
