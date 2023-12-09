# fake FOXSI

import os
import numpy as np
import time

from FoGSE.visualization import DATA_FILE

def write_numbers(file, filesizeB, fancy=False, random=False, quiet=False, no_of_pixels=100):
    # no_of_pixels = 100 only for 2d images
    entries_per_cycle = 1_000  # 1000 entries is about 50 kB, 20 entries -> 1 kB (1024 bytes), 20*1024 is 1 MB
    bytes_to_add = 50*entries_per_cycle # numpy saves out the txt file at this by default, can change but for hat gain at the moment?
    
    # need for more complex data no_of_fields = 1
    added_entries = 0
    _c = 0

    if os.path.exists(file):
        print(f"File {file} exists and is being removed.")
        os.remove(file)
    
    while added_entries<filesizeB:
        _dt = time.time()

        if random:
            np.random.seed(added_entries) # reproducable but still changes every cycle

        # this will change for the actual data, ran = np.random.rand(no_of_fields, entries_per_sec) if random else 
        # if no_of_fields==1:
        ran = np.random.rand(entries_per_cycle) if random else np.arange(entries_per_cycle, dtype=float)

        t = np.arange(entries_per_cycle) + added_entries

        if fancy:
            ran = fancy_data(ran, random=random)

        x = np.random.randint(no_of_pixels, size=entries_per_cycle).astype(float)
        y = np.random.randint(no_of_pixels, size=entries_per_cycle).astype(float)

        
        event_value = cause_event(arr=1, event_thresh=0.99, random=random)
        if event_value>1:
            x[:10], y[:10] = x[1], y[1]

        cc = np.concatenate((t[None,:],ran[None,:], x[None,:], y[None,:]), axis=0).T

        if os.path.exists(file):
            with open(file, "a") as f:
                np.savetxt(f, cc)
        else:
            np.savetxt(file, cc)

        cc_bytes = bytes_to_add#cc.nbytes # getsizeof(cc) # cc.size*cc.itemsize
        added_entries += cc_bytes
        
        # print out speed but not every loop iteration so (_c%15==0)
        if (not quiet) and (_c%15==0):
            print(f"\rWriting at {int(cc_bytes/(time.time()-_dt))} Bps and file size is at {round(100*added_entries/filesizeB,2)}%.", end="")

        _c += 1


def fancy_data(ran, random=False):
    cs = np.cumsum(ran)
    y0 = np.cos(ran*0.01)
    y1 = np.cos(ran*0.02)
    y2 = 1.2*np.cos(ran*0.01-1)
    y3 = 1.5*np.sin(ran*0.03-1)
    y4 = 4*np.sin(ran*0.01-10)
    y5 = 0.5*np.sin(ran*0.1+0.5)
    _event = np.random.rand() if random else 0
    if _event>=0.5:
        cs *= 5
    else:
        cs /= 5
    ran = cs+y0+y1+y2+y3+y4+y5
    ran = cause_event(arr=ran, event_thresh=0.99)
    return ran

def cause_event(arr, event_thresh=0.99, random=False):
    _event = np.random.rand() if random else 0
    if _event>event_thresh:
        arr *= 1e2
    return arr

def test():
    from multiprocessing import Process

    fileSizeInBytes = 1024**3 # 1024**3 is gigabyte in bytes

    filename0 = DATA_FILE[:-4] + "_0" + DATA_FILE[-4:]

    filename1 = DATA_FILE[:-4] + "_1" + DATA_FILE[-4:]

    ####**** for testing checksum, set random to False
    random = True
    no_of_pixels = 100

    # run the function simultaneously with a couple different inputs
    p1 = Process(target = write_numbers, kwargs={"file":filename0, "filesizeB":fileSizeInBytes, "fancy":True, "random":random, "quiet":False})
    p1.start()
    p2 = Process(target = write_numbers, kwargs={"file":filename1, "filesizeB":fileSizeInBytes, "fancy":True, "random":random, "quiet":False, "no_of_pixels":no_of_pixels})
    p2.start()
    # p1.join()
    p2.join()

if __name__=="__main__":
    fileSizeInBytes = 1024**3 # 1024**3 is gigabyte in bytes

    filename0 = DATA_FILE

    ####**** for testing checksum, set random to False
    random = True
    no_of_pixels = 100
    write_numbers(file=filename0, filesizeB=fileSizeInBytes, fancy=True, random=random, quiet=False, no_of_pixels=no_of_pixels)
