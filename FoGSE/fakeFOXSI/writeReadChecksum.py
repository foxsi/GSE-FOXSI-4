"""Write and read from a file simultaneously. Check no corruption happens."""

import sys
import os
import time
import hashlib
from multiprocessing import Process

from createDataFile import write_numbers
from FoGSE.readBackwards import BackwardsReader
from FoGSE.visualization import DATA_FILE

FILENAME_H0 = DATA_FILE[:-4] + "_CS0" + DATA_FILE[-4:] # just write this file
FILENAME_H1 = DATA_FILE[:-4] + "_CS1" + DATA_FILE[-4:] # write and read this file at the same time

# set up some inputs
QUIET = True # stop the file writing and reading functions printing info?
FILESIZE = 10 * 1024**3 # 1024**3 is gigabyte in bytes
READCALLS = 30_000 # read file this many times before stopping (3000 for about a 2.7 GB file to be created @ buffer=25_000_020)
READBLOCK = 100_000#25_000_020 # block size for backwards reader

def run_reading_func():
    """Function to read a file backwards"""
    
    calls = 0 # 3000 calls is made while a 2.7 GB is being made
    while calls<READCALLS:
        _dt = time.time()
        if os.path.exists(FILENAME_H1):
            with BackwardsReader(file=FILENAME_H1, blksize=READBLOCK, forward=True) as f:
                block = f.read_block()
                if not QUIET:
                    print(f"Reading ({len(block.decode('utf-8'))/(time.time()-_dt)} Bps).")
                    
            calls += 1

def run_writing_func():
    """Function to write a file"""

    write_numbers(file=FILENAME_H1, filesizeB=FILESIZE, fancy=True, random=False, quiet=QUIET)


if __name__=="__main__":

    for i in range(1, 51):

        # remove files for the checksum check if they are already there
        if os.path.exists(FILENAME_H0):
            os.remove(FILENAME_H0)
        if os.path.exists(FILENAME_H1):
            os.remove(FILENAME_H1)
        
        # write the file normally
        write_numbers(file=FILENAME_H0, filesizeB=FILESIZE, fancy=True, random=False, quiet=QUIET)

        # run the functions simultaneously
        p1 = Process(target = run_reading_func)
        p1.start()
        p2 = Process(target = run_writing_func)
        p2.start()
        p1.join()
        p2.join()

        # compare the checksums of the files, first one was just written while the second was read as it was written
        checksum = hashlib.md5(open(FILENAME_H0,'rb').read()).hexdigest()==hashlib.md5(open(FILENAME_H1,'rb').read()).hexdigest()
        if checksum:
            print(f"Checksum checks out! (For files {FILENAME_H0} and {FILENAME_H1}.) Run: {i}.")
        else:
            print(f"Boooo!! Checksum does not check out! (For files {FILENAME_H0} and {FILENAME_H1}.) Run: {i}.")

        # remove the files
        os.remove(FILENAME_H0)
        os.remove(FILENAME_H1)

    # exit everything
    sys.exit()

    