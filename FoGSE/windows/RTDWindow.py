"""
A demo to walk through an existing CdTe raw file.
"""

import numpy as np

from PyQt6.QtWidgets import QApplication

from FoGSE.read_raw_to_refined.readRawToRefinedRTD import RTDReader
from FoGSE.windows.base_windows.BaseWindow import BaseWindow
from FoGSE.windows.base_windows.LightCurveWindow import MultiLightCurve


class RTDWindow(BaseWindow):
    """
    An individual window to display RTD data read from a file.

    Parameters
    ----------
    data_file : `str` 
        The file to be passed to `FoGSE.read_raw_to_refined.readRawToRefinedRTD.RTDReader()`.
        If given, takes priority over `reader` input.
        Default: None

    reader : instance of `FoGSE.read_raw_to_refined.readRawToRefinedBase.ReaderBase()`
        The reader already given a file.
        Default: None

    plotting_product : `str`
        String to determine whether an \"image\", \"spectrogram\", or \"lightcurve\" 
        should be shown. Only \"lightcurve\"  is supported here.
        Default: \"lightcurve\"
    
    name : `str`
        A useful string that can be used as a label.
        Default: \"RTD\"
    """
    def __init__(self, data_file=None, reader=None, plotting_product="lightcurve", name="RTD", parent=None):

        BaseWindow.__init__(self, data_file=data_file, 
                            reader=reader, 
                            plotting_product=plotting_product, 
                            image_angle=0, 
                            integrate="integrate", 
                            name=name, 
                            colour="", 
                            parent=parent)

    def base_essential_get_reader(self):
        """ Return default reader here. """
        return RTDReader
    
    def products(self):
        """ Define the products for the class. """
        return {"lightcurve":None}
    
    def base_essential_setup_product(self, product):
        """ 
        Given a plotting product, return a function to set up that product.
        """
        product_setup_map = self.products()

        product_setup_map["lightcurve"] = self.lightcurve_setup

        return product_setup_map.get(product, None)
    
    def update_product(self, product):
        """ 
        Given a plotting product, return a function to update that product.
        """
        product_update_map = self.products()

        product_update_map["lightcurve"] = self.lightcurve_update

        return product_update_map.get(product, None)

    def lightcurve_setup(self):
        """ Sets up the class for a time profile product. """

        self.chip1_ids     = ['ts0',  'ts1',        'ts2',  'ts3',  'ts4',    'ts5',     'ts6',      'ts7',  'ts8']
        self.chip1_names   = ['LN2',  'POS2',       'POS3', 'POS4', 'POS5',   '5.5 V',   'MICRO',    '???',  'TIMEPIX']
        self.chip1_colours = ['blue', 'lightgreen', 'red',  'cyan', 'gold',   'magenta', 'darkGrey', 'pink', 'k']

        self.chip2_ids     = ['ts9',         'ts10',       'ts11',   'ts12',    'ts13',    'ts14',    'ts15',     'ts16',     'ts17']
        self.chip2_names   = ['OPTIC PLATE', 'A FRONT',    'A BACK', 'B FRONT', 'C FRONT', 'C BACK',  'D FRONT',  'D MIDDLE', 'D BACK']
        self.chip2_colours = ['blue',        'lightgreen', 'red',    'cyan',    'gold',    'magenta', 'darkGrey', 'pink',     'k']

        self.chip1 = MultiLightCurve(ids=self.chip1_ids, colours=self.chip1_colours, names=self.chip1_names)
        self.chip2 = MultiLightCurve(ids=self.chip2_ids, colours=self.chip2_colours, names=self.chip2_names)

        self.layoutMain.addWidget(self.chip1)
        self.layoutMain.addWidget(self.chip2)

        self.chip1.set_labels(xlabel="", ylabel="T (C)", title="", xlabel_kwargs={"size":5}, ylabel_kwargs={"size":5}, title_kwargs={"size":0}, tick_kwargs={"labelsize":4}, offsetsize=1)
        self.chip2.set_labels(xlabel="Time (Unixtime)", ylabel="T (C)", title="", xlabel_kwargs={"size":5}, ylabel_kwargs={"size":5}, title_kwargs={"size":0}, tick_kwargs={"labelsize":4}, offsetsize=1)

        self.detw, self.deth = self.chip1.detw, self.chip1.deth+self.chip2.deth
        self.aspect_ratio = self.detw / self.deth

    def lightcurve_update(self):
        """ Define how the time profile product should updated. """
        chip1_values = self.reader.collection.chip1_data()
        chip2_values = self.reader.collection.chip2_data()
        
        # defined how to add/append onto the new data arrays
        self.chip1.add_plot_data(chip1_values[1:], new_data_xs=chip1_values[0], replace={"this":[np.nan], "with":[0]})
        self.chip2.add_plot_data(chip2_values[1:], new_data_xs=chip2_values[0], replace={"this":[0], "with":[np.nan]})

        # plot the newly updated x and ys
        self.chip1.manage_plotting_ranges()
        self.chip2.manage_plotting_ranges()

    def base_essential_update_plot(self):
        """Defines how the plot window is updated. """
        self.update_product(self.plotting_product)()

        self.update()


if __name__=="__main__":
    
    import os
    DATAFILE = os.path.dirname(os.path.realpath(__file__)) + "/../../../fake_temperatures.txt"
    DATAFILE = "/Users/kris/Downloads/housekeeping.log"
    # DATAFILE = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/GSE-FOXSI-4/logs/received/1-2-2024_9-16-23/housekeeping_rtd.log"
    DATAFILE = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/usingGSECodeForDetAnalysis/feb3/run19/gse/housekeeping.log"

    def initiate_gui():
        app = QApplication([])

        # R = RTDFileReader(DATAFILE)
        R = RTDReader(DATAFILE)

        f0 = RTDWindow(reader=R)

        f0.show()
        app.exec()

    # from multiprocessing import Process

    # fake temps
    # p1 = Process(target = initiate_fake_Timepixs)
    # p1.start()
    # live plot
    # p2 = Process(target = initiate_gui)
    # p2.start()
    # p2.join()

    initiate_gui()
