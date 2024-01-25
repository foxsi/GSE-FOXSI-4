"""
A demo to walk through an existing CdTe raw file.
"""

import numpy as np

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QApplication, QWidget, QGridLayout
import pyqtgraph as pg

from FoGSE.read_raw_to_refined.readRawToRefinedCdTe import CdTeReader
from FoGSE.demos.readRawToRefined_single_cdte import CdTeFileReader
from FoGSE.windows.images import rotatation


class CdTeWindow(QWidget):
    """
    An individual window to display CdTe data read from a file.

    Parameters
    ----------
    data_file : `str` 
        The file to be passed to `FoGSE.read_raw_to_refined.readRawToRefinedCdTe.CdTeReader()`.
        If given, takes priority over `reader` input.
        Default: None

    reader : instance of `FoGSE.read_raw_to_refined.readRawToRefinedCdTe.ReaderBase()`
        The reader already given a file.
        Default: None

    plotting_product : `str`
        String to determine whether an "image" and or "spectrogram" should be shown.
        Default: "image"
    """
    def __init__(self, data_file=None, reader=None, plotting_product="image", image_angle=0, name="CdTe", parent=None):

        pg.setConfigOption('background', (255,255,255, 0)) # needs to be first

        QWidget.__init__(self, parent)
        self.graphPane = pg.PlotWidget()
        # self.graphPane.setMinimumSize(QtCore.QSize(200,100)) # was 250,250
        # self.graphPane.setSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.MinimumExpanding)

        self.layoutMain = QGridLayout()
        self.layoutMain.addWidget(self.graphPane)
        self.setLayout(self.layoutMain)

        self.name = name

        # decide how to read the data
        if data_file is not None:
            # probably the main way to use it
            self.reader = CdTeReader(data_file)
        elif reader is not None:
            # useful for testing and if multiple windows need to share the same file
            self.reader = reader
        else:
            print("How do I read the CdTe data?")

        # make this available everywhere, incase a rotation is specified for the image
        self.image_angle = image_angle
            
        self.image_product = plotting_product
        if self.image_product in ["image", "spectrogram"]:
            self.setup_2d()
        else:
            print("Nothing else is set-up yet.")

        self.reader.value_changed_collection.connect(self.update_plot)

        # Disable interactivity
        # self.graphPane.setMouseEnabled(x=False, y=False)  # Disable mouse panning & zooming

        self.update_background(colour=(10,40,80,100))#colour="white"
        
    def setup_2d(self):
        # set all rgba info (e.g., mode rgb or rgba, indices for red green blue, etc.)
        self.colour_mode = "rgba"
        self.channel = {"red":0, "green":1, "blue":2}
        # alpha index
        self.alpha = 3
        # colours range from 0->255 in RGBA
        self.min_val, self.max_val = 0, 255

        # define how many frames to fade a count out over
        self.set_fade_out(no_of_frames=25)

        # create QImage from numpy array 
        if self.image_product=="image":
            # could do some maths to figure out but this WILL give the result need even if something is changed elsewhere
            _rm = rotatation.rotate_matrix(matrix=np.zeros((128, 128)), angle=self.image_angle)
            self.detw, self.deth = np.shape(_rm)
            self.update_aspect(aspect_ratio=self.detw/self.deth)
            # set title and labels
            self.set_labels(self.graphPane, xlabel="X", ylabel="Y", title=f"{self.name}: Image")
        elif self.image_product=="spectrogram":
            self.detw, self.deth = 256, 1024
            self.update_aspect(aspect_ratio=2)
            # set title and labels
            self.set_labels(self.graphPane, xlabel="Strips [Pt:0-127, Al:127-255]", ylabel="ADC/Energy", title=f"{self.name}: Spectrogram")
 
        self.graphPane.plotItem.vb.setLimits(xMin=0, xMax=self.detw, yMin=0, yMax=self.deth)

        self.numpy_format = np.uint8
        self.set_image_ndarray()
        q_image = pg.QtGui.QImage(self.my_array, self.detw, self.deth, self.cformat)

        if hasattr(self,"img"):
            self.graphPane.removeItem(self.img)
        # send image to frame and add to plot
        self.img = QtWidgets.QGraphicsPixmapItem(pg.QtGui.QPixmap(q_image))
        self.graphPane.addItem(self.img)

        self.set_image_colour("green")

    def update_rotation(self, image_angle):
        """ Allow the image rotation to be updated whenever. """
        self.image_angle = image_angle
        self.setup_2d()

    def update_background(self, colour):
        """ 
        Update the background image colour. 
        
        E.g., colour=(10,40,80,100))
              colour=\"white\"
              etc.
        """
        self.graphPane.getViewBox().setBackgroundColor(colour)
    
    def update_aspect(self, aspect_ratio):
        """ Update the image aspect ratio (width/height). """
        self.aspect_ratio = aspect_ratio

    def set_fade_out(self, no_of_frames):
        """ Define how many frames to fade a count out over. """
        self.fade_out = no_of_frames
        # the minimum fade for a pixel, should be redunant but this can end up being 
        # an incredibly small value (e.g, 1e-14) instead of exactly 0
        self._min_fade_alpha = self.max_val - (self.max_val/self.fade_out)*self.fade_out

    def set_image_colour(self, colour):
        """ Define image colour to use. """

        if colour not in list(self.channel):
            print("Need colour of:", list(self.channel))
            return

        if hasattr(self, "image_colour") and hasattr(self, "my_array"):
            self.my_array[:,:,self.channel[colour]] = self.my_array[:,:,self.channel[self.image_colour]]
            self.my_array[:,:,self.channel[self.image_colour]] = np.zeros(np.shape(self.my_array[:,:,self.channel[self.image_colour]]))
        self.image_colour = colour

    def update_plot(self):
        """
        Defines how the plot window is updated for a 2D image.

        In subclass define methods: 
        *`get_data` to extract the new image frame from `self.data_file`, 
        *`update_image` to define how the new image affects the current one,
        *`process_data` to perform any last steps before updating the plot.
        """
        
        # get the new frame
        if self.image_product=="image":
            new_frame = self.reader.collection.image_array(area_correction=False)
            new_frame = rotatation.rotate_matrix(matrix=new_frame, angle=self.image_angle)
            new_frame[new_frame<1e-1] = 0 # because interp 0s causes tiny artifacts
            self.update_method = "fade"
        elif self.image_product=="spectrogram":
            new_frame = self.reader.collection.spectrogram_array(remap=True, 
                                                                  nan_zeros=False, 
                                                                  cmn_sub=False).T
            print("Min/max CdTe frame1",np.min(new_frame),np.max(new_frame))
            new_frame[new_frame>0.01*np.max(new_frame)] = 0.01*np.max(new_frame)
            print("Min/max CdTe frame2",np.min(new_frame),np.max(new_frame))
            self.update_method = "replace"

        # update current plotted data with new frame
        self.update_image(existing_frame=self.my_array, new_frame=new_frame)
        
        # define self.qImageDetails for this particular image product
        self.process_data()

        # # new image
        q_image = pg.QtGui.QImage(*self.qImageDetails)#Format.Format_RGBA64

        # faster long term to remove pervious frame and replot new one
        self.graphPane.removeItem(self.img)
        self.img = QtWidgets.QGraphicsPixmapItem(pg.QtGui.QPixmap(q_image))
        self.graphPane.addItem(self.img)
        self.update()

    def update_image(self, existing_frame, new_frame):
        """
        Add new frame to the current frame while recording the newsest hits in the `new_frame` image. Use 
        the new hits to control the alpha channel via `self.fade_control` to allow old counts to fade out.
        
        Only using the blue and alpha channels at the moment.

        Parameters
        ----------
        existing_frame : `numpy.ndarray`
            This is the RGB (`self.colour_mode='rgb'`) or RGBA (`self.colour_mode='rgba'`) array of shape 
            (`self.deth`,`self.detw`,3) or (`self.deth`,`self.detw`,4), respectively.

        new_frame : `numpy.ndarray`
            This is a 2D array of the new image frame created from the latest data of shape (`self.deth`,`self.detw`).
        """

        # if new_frame is a list then it's empty and so no new frame, make all 0s
        if isinstance(new_frame,list): 
            new_frame = np.zeros((self.deth, self.detw))
        
        if self.update_method=="fade":
            # what pixels have a brand new hit? (0 = False, not 0 = True)
            new_hits = new_frame.astype(bool) 
            
            self.fade_control(new_hits_array=new_hits)#, control_with=self.image_colour)

            # add the new frame to the blue channel values and update the `self.my_array` to be plotted
            self.my_array[:,:,self.channel[self.image_colour]] = existing_frame[:,:,self.channel[self.image_colour]] + new_frame
        elif self.update_method=="replace":
            self.my_array[:,:,self.channel[self.image_colour]] = new_frame

        self._turn_pixels_on_and_off()

    def _turn_pixels_on_and_off(self):
        """ Turn pixels alpha channels on and off. """
        _frame = self.my_array[:,:,self.channel[self.image_colour]]
        _lowest_value_to_view = np.max(_frame)/1e6 #i.e., dynamic range of 1e6
        self.my_array[:,:,self.alpha][_frame>_lowest_value_to_view] = self.max_val
        self.my_array[:,:,self.alpha][_frame<=_lowest_value_to_view] = self.min_val

    def fade_control(self, new_hits_array, control_with="rgb"):
        """
        Fades out pixels that haven't had a new count in steps of `self.max_val//self.fade_out` until a pixel has not had an 
        event for `self.fade_out` frames. If a pixel has not had a detection in `self.fade_out` frames then reset the colour 
        channel to zero and the alpha channel back to `self.max_val`.

        Parameters
        ----------
        new_hits_array : `numpy.ndarray`, `bool`
            This is a 2D boolean array of shape (`self.deth`,`self.detw`) which shows True if the pixel has just detected 
            a new count and False if it hasn't.

        control_with : `str`
            Sets how to control the image fade. Can choose rgb, and it will control the fade with `self.image_colour` or
            set to alpha and it will use th alpha channel if it can.
            Default: 'rgb'
        """

        # add to counter if pixel has no hits
        self.no_new_hits_counter_array += ~new_hits_array

        # reset counter if pixel has new hit
        self.no_new_hits_counter_array[new_hits_array] = 0

        if (control_with=="alpha") and (self.colour_mode=="rgba"):
            # set alpha channel, fade by decreasing steadily over `self.fade_out` steps 
            # (a step for every frame the pixel has not detected an event)
            self.my_array[:,:,self.alpha] = self.max_val - (self.max_val/self.fade_out)*self.no_new_hits_counter_array

            # find where alpha is zero (completely faded)
            turn_off_colour = (self.my_array[:,:,self.alpha]==self._min_fade_alpha)

            # now set the colour back to zero and return alpha to max, ready for new counts
            for k in self.channel.keys():
                self.my_array[:,:,self.channel[k]][turn_off_colour] = 0

            # reset alpha
            self.my_array[:,:,self.alpha][turn_off_colour] = self.max_val

        elif control_with=="rgb":# in ["red", "green", "blue"]:
            cw = self.image_colour
            index = self.channel[cw]
            self.my_array[:,:,index] = self.my_array[:,:,index] - (self.my_array[:,:,index]/self.fade_out)*self.no_new_hits_counter_array
            #sometimes the above line doesn't set an entry to zero, just really really close to it
            self.my_array[:,:,index][self.my_array[:,:,index]<1e-1] = 0 

        # reset the no hits counter when max is reached
        self.no_new_hits_counter_array[self.no_new_hits_counter_array>=self.fade_out] = 0

    def process_data(self):
        """
        An extra processing step for the data before it is plotted.
        """
    
        # make sure everything is normalised between 0--255
        norm = np.max(self.my_array, axis=(0,1))
        norm[norm==0] = 1 # can't divide by 0
        uf = self.max_val*self.my_array//norm

        # allow this all to be looked at if need be
        self.qImageDetails = [uf.astype(self.numpy_format), self.detw, self.deth, self.cformat]

    def set_labels(self, graph_widget, xlabel="", ylabel="", title=""):
        """
        Method just to easily set the x, y-label andplot title without having to write all lines below again 
        and again.

        [1] https://stackoverflow.com/questions/74628737/how-to-change-the-font-of-axis-label-in-pyqtgraph

        arameters
        ----------
        graph_widget : `PyQt6 PlotWidget`
            The widget for the labels

        xlabel, ylabel, title : `str`
            The strings relating to each label to be set.
        """

        graph_widget.setTitle(title)

        # Set label for both axes
        graph_widget.setLabel('bottom', xlabel)
        graph_widget.setLabel('left', ylabel)

    def set_image_ndarray(self):
        """
        Set-up the numpy array and define colour format from `self.colour_mode`.
        """
        # colours range from 0->255 in RGBA8888 and RGB888
        # do we want alpha channel or not
        if self.colour_mode == "rgba":
            self.my_array = np.zeros((self.deth, self.detw, 4))
            self.cformat = pg.QtGui.QImage.Format.Format_RGBA8888
            # for all x and y, turn alpha to max
            self.my_array[:,:,3] = self.max_val 
        if self.colour_mode == "rgb":
            self.my_array = np.zeros((self.deth, self.detw, 3))
            self.cformat = pg.QtGui.QImage.Format.Format_RGB888

        # define array to keep track of the last hit to each pixel
        self.no_new_hits_counter_array = (np.zeros((self.deth, self.detw))).astype(self.numpy_format)

    def resizeEvent(self,event):
        """ Define how the widget can be resized and keep the same apsect ratio. """
        super().resizeEvent(event)
        # Create a square base size of 10x10 and scale it to the new size
        # maintaining aspect ratio.
        # if self.image_product=="spectrogram":
        #     print("ere", event.size().width(), event.size().height())
        if event is None:
            return 
        
        new_size = QtCore.QSize(self.detw, int(self.detw / self.aspect_ratio)) #width, height/(width/height)
        new_size.scale(event.size(), QtCore.Qt.AspectRatioMode.KeepAspectRatio)

        self.resize(new_size)


if __name__=="__main__":
    app = QApplication([])

    # different data files to try
    # datafile = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/CdTeImages/no2022_03/NiFoilAm241/10min/test_20230609a_det03_00012_001"
    # datafile = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/berkeley/prototype_vibe_test/fromBerkeley_postVibeCheckFiles/Am241/test_berk_20230803_proto_Am241_1min_postvibe2_00006_001"
    # datafile = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/berkeley/prototype_vibe_test/fromBerkeley_postVibeCheckFiles/Fe55/test_berk_20230803_proto_Fe55_1min__postvibe2_00008_001"
    # datafile = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/CdTeImages/no2021_05/Am241/1min/test_berk_20230728_det05_00005_001"
    # datafile = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/CdTeImages/no2021_05/Fe55/1min/test_berk_20230728_det05_00006_001"
    # datafile = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/CdTeImages/no2021_05/Cr51/1min/test_berk_20230728_det05_00007_001"
    # datafile = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/berkeley/prototype_vibe_test/vibetest_presinez_berk_20230802_proto_00012_001"
    
    import os
    FILE_DIR = os.path.dirname(os.path.realpath(__file__))
    datafile = FILE_DIR+"/../data/test_berk_20230728_det05_00007_001"
    datafile = "/Users/kris/Desktop/test_230306_00001_001_nohk"
    datafile="/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/calibration/j-sideRootData/usingDAQ/raw2root/backgrounds-20230331-newGrounding/20230331_bkg_00001_001"
    # datafile = "/Users/kris/Desktop/cdte_20231030.log"
    # datafile = "/Users/kris/Desktop/cdte_20231030_postsend.log"
    # datafile = "/Users/kris/Desktop/cdte_20231030_presend.log"
    datafile = "/Users/kris/Desktop/cdte_20231030_fullread.log"
    datafile = "/Users/kris/Desktop/cdte_src_mod.log"
    datafile = "/Users/kris/Desktop/gse_mod.log"
    datafile = "/Users/kris/Desktop/from_de.log"
    # datafile = "/Users/kris/Desktop/from_gse.log"
    datafile = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/CdTeTrialsOfParser-20231102/cdte.log"
    # datafile = ""

    # `datafile = FILE_DIR+"/../data/cdte.log"`
    reader = CdTeFileReader(datafile)#CdTeReader(data_file)
    # reader = CdTeReader(datafile)

    f0 = CdTeWindow(reader=reader, plotting_product="spectrogram")
    f1 = CdTeWindow(reader=reader, plotting_product="image")
    # print(R.collections)
    f0.show()
    f1.show()
    app.exec()