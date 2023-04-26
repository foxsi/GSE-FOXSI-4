import sys
import time
from PyQt6.QtWidgets import QApplication
# from FOGSE import application
from FoGSE.application import GSEMain, GSEFocus, GSECommand
from FoGSE.fakeFOXSI.createDataFile import write_numbers
from FoGSE.visualization import DATA_FILE

from multiprocessing import Process

def run_layout():
    """Run GSEMain"""
    app = QApplication([])
    window = GSEMain()
    window.show()
    sys.exit(app.exec())

def fake_foxsi(**kwargs):
    """Produce fake data after a small delay"""
    time.sleep(5)
    write_numbers(**kwargs)
    
if __name__=="__main__":
    
    # layout
    p1 = Process(target = run_layout)
    p1.start()
    # fake FOXSI
    p2 = Process(target = fake_foxsi, kwargs={"file":DATA_FILE, "filesizeB":1024**3, "fancy":True, "random":True, "quiet":False, "no_of_pixels":100})
    p2.start()
    p2.join()

    