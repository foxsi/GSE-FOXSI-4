"""
A demo to walk through a Timepix raw file.
"""

import numpy as np

from PyQt6.QtWidgets import QApplication

from FoGSE.readers.TimepixPCAPReader import TimepixPCAPReader
from FoGSE.windows.base_windows.BaseWindow import BaseWindow
from FoGSE.windows.base_windows.LightCurveWindow import LightCurve, MultiLightCurve


class TimepixPCAPWindow(BaseWindow):
    """
    An individual window to display Timepix data read from a file.

    Parameters
    ----------
    data_file : `str` 
        The file to be passed to `FoGSE.readers.TimepixPCReader.TimepixPCReader()`.
        If given, takes priority over `reader` input.
        Default: None

    reader : instance of `FoGSE.readers.BaseReader.BaseReader()`
        The reader already given a file.
        Default: None

    plotting_product : `str`
        String to determine whether an \"image\", \"spectrogram\", or \"lightcurve\" 
        should be shown. Only \"lightcurve\"  is supported here.
        Default: \"lightcurve\"
    
    name : `str`
        A useful string that can be used as a label.
        Default: \"TimepixPCAP\"
    """
    def __init__(self, data_file=None, reader=None, plotting_product="lightcurve", name="TimepixPCAP", parent=None):

        BaseWindow.__init__(self, data_file=data_file, 
                            reader=reader, 
                            plotting_product=plotting_product, 
                            name=name, 
                            colour="", 
                            parent=parent)

    def base_essential_get_reader(self):
        """ Return default reader here. """
        return TimepixPCAPReader
    
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

        self.pcap1_plot = LightCurve()
        self.pcapn_plot = MultiLightCurve(ids=["pcap2", "pcap3", "pcap4"], colours=["g", "b", "k"])
        
        self.layoutMain.addWidget(self.pcap1_plot)
        self.layoutMain.addWidget(self.pcapn_plot)

        self.pcap1_plot.set_labels(xlabel="", ylabel="PCAP1", title=" ", xlabel_kwargs={"size":5}, ylabel_kwargs={"size":5}, title_kwargs={"size":0}, tick_kwargs={"labelsize":4}, offsetsize=1)
        self.pcapn_plot.set_labels(xlabel="Time (frame #)", ylabel="PCAP2,3,4", title="", xlabel_kwargs={"size":5}, ylabel_kwargs={"size":5}, title_kwargs={"size":0}, tick_kwargs={"labelsize":4}, offsetsize=1)
        
        self.detw, self.deth = self.pcap1_plot.detw, self.pcap1_plot.deth+self.pcapn_plot.deth
        self.aspect_ratio = self.detw / self.deth

    def lightcurve_update(self):
        """ Define how the time profile product should updated. """
        new_pcap1 = self.reader.collection.get_pcap1()
        new_pcapn = [self.reader.collection.get_pcap2(),
                     self.reader.collection.get_pcap3(),
                     self.reader.collection.get_pcap4()]
        
        # defined how to add/append onto the new data arrays
        self.pcap1_plot.add_plot_data(new_pcap1)
        self.pcapn_plot.add_plot_data(new_pcapn)

        # plot the newly updated x and ys
        self.pcap1_plot.manage_plotting_ranges()
        self.pcapn_plot.manage_plotting_ranges()

    def base_essential_update_plot(self):
        """Defines how the plot window is updated. """
        self.update_product(self.plotting_product)()

        self.update()


if __name__=="__main__":
    
    DATAFILE = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/timepix/for_Kris/fake_data_for_parser/example_timepix_frame.bin"
    DATAFILE = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/timepix/for_Kris/fake_data_for_parser/example_timepix_frame_writing.bin"

    def initiate_gui():
        app = QApplication([])

        R = TimepixPCAPReader(DATAFILE)

        f0 = TimepixPCAPWindow(reader=R)

        f0.show()
        app.exec()

    initiate_gui()
