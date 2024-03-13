"""
A demo to walk through an existing CdTe raw file.
"""

import numpy as np

from PyQt6 import QtCore
from PyQt6.QtWidgets import QWidget, QGridLayout

from FoGSE.widgets.layout_tools.stretch import unifrom_layout_stretch
from FoGSE.widgets.layout_tools.spacing import set_all_spacings


class BaseWindow(QWidget):
    """
    An individual window to display CdTe data read from a file.

    Parameters
    ----------
    data_file : `str` 
        The file to be passed to `base_essential_get_reader`.
        If given, takes priority over `reader` input.
        Default: None

    reader : instance of `FoGSE.readers.BaseReader.BaseReader()`
        The reader already given a file.
        Default: None

    plotting_product : `str`
        String to determine whether an "image", "spectrogram", or "lightcurve" 
        should be shown.
        Default: \"\"

    image_angle : `int`, `float`, etc.
        The angle of roation for the plot. Positive is anti-clockwise and 
        negative is clockwise.
        Default: 0
    
    integrate : `bool`
        Indicates whether the frames (if that is relevant `plotting_product`)
        should be summed continously, unless told otherwise.
        Default: False
    
    name : `str`
        A useful string that can be used as a label.
        Default: \"\"
        
    colour : `str`
        The colour channel used, if used for the `plotting_product`. 
        Likely from [\"red\", \"green\", \"blue\"].
        Default: \"green\"
    """
    base_qwidget_entered_signal = QtCore.pyqtSignal()
    base_qwidget_left_signal = QtCore.pyqtSignal()

    def __init__(self, data_file=None, reader=None, plotting_product="", image_angle=0, integrate=False, name="", colour="green", parent=None):

        QWidget.__init__(self, parent)

        self.layoutMain = QGridLayout()
        self.layoutMain.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layoutMain)

        self.name = name
        self.integrate = integrate
        self.colour = colour

        # decide how to read the data
        if data_file is not None:
            # probably the main way to use it
            self.reader = self.base_essential_get_reader()(data_file)
        else:
            # useful for testing and if multiple windows need to share the same file
            self.reader = reader

        self.name = self.base_essential_get_name()

        # make this available everywhere, incase a rotation is specified for the image
        self.image_angle = image_angle
            
        self.plotting_product = plotting_product
        setup_func = self.base_essential_setup_product(self.plotting_product)

        if setup_func is None:
            print(f"How do I set-up {self.plotting_product}?")
            return 
        
        setup_func()

        set_all_spacings(self.layoutMain)
        unifrom_layout_stretch(self.layoutMain, grid=True)

        self.installEventFilter(self)
        self.setMouseTracking(True)

        self.reader.value_changed_collection.connect(self.base_essential_update_plot)

    def base_essential_get_reader(self):
        """ Return default reader here. """
        pass

    def base_essential_get_name(self):
        """ Define a custom way to get the name. Can be used as a label. """
        return self.name

    def base_essential_setup_product(self, product):
        """ 
        Given a plotting product (e.g., image, etc.), return a function 
        to set up that product.
        """
        product_setup_map = {}

        return product_setup_map.get(product, None)
    
    def base_essential_update_plot(self):
        """ Define how the plot should be updated. """
        return None

    # methods that are very common for a variety of plotting products
    def base_set_image_colour(self, colour):
        """ Define image colour to use. """

        if colour not in list(self.channel):
            print("Need colour of:", list(self.channel))
            return

        if hasattr(self, "image_colour") and hasattr(self, "my_array"):
            self.my_array[:,:,self.channel[colour]] = self.my_array[:,:,self.channel[self.image_colour]]
            self.my_array[:,:,self.channel[self.image_colour]] = np.zeros(np.shape(self.my_array[:,:,self.channel[self.image_colour]]))
        self.image_colour = colour

    def base_set_fade_out(self, no_of_frames):
        """ Define how many frames to fade a count out over. """
        self.fade_out = no_of_frames
        # the minimum fade for a pixel, should be redunant but this can end up being 
        # an incredibly small value (e.g, 1e-14) instead of exactly 0
        self._min_fade_alpha = self.max_val - (self.max_val/self.fade_out)*self.fade_out

    def base_2d_image_settings(self):
        """ Settings for a 2D product. """
        self.colour_mode = "rgba"
        self.channel = {"red":0, "green":1, "blue":2}
        # alpha index
        self.alpha = 3
        # colours range from 0->255 in RGBA
        self.min_val, self.max_val = 0, 255

        # define how many frames to fade a count out over
        self.base_set_fade_out(no_of_frames=25)

    def base_2d_image_handling(self):
        """ 
        Once an image has been created, add to the widget then make sure 
        `base_2d_image_settings` are applied.

        Attributes needed to be set are:
        * `layoutMain`
        * `graphPane`
        * `colour`

        Methods needed are:
        * `base_set_image_ndarray`
        * `base_set_image_colour`
        """
        self.layoutMain.addWidget(self.graphPane)

        self.base_set_image_ndarray()

        self.base_set_image_colour(self.colour)

    def base_apply_update_style(self, existing_frame, new_frame):
        """
        Add new frame to the current frame while recording the newest hits in the `new_frame` image. Use 
        the new hits to control the alpha channel via `self.base_fade_control` to allow old counts to fade out.

        Attributes needed to be set are:
        * `deth`
        * `detw`
        * `update_method`
        * `channel`
        * `image_colour`
        * `my_array`

        Methods needed are:
        * `base_fade_control`
        * `base_turn_pixels_on_and_off`

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
            
            self.base_fade_control(new_hits_array=new_hits)#, control_with=self.image_colour)

            # add the new frame to the blue channel values and update the `self.my_array` to be plotted
            self.my_array[:,:,self.channel[self.image_colour]] = existing_frame[:,:,self.channel[self.image_colour]] + new_frame
        elif self.update_method=="replace":
            self.my_array[:,:,self.channel[self.image_colour]] = new_frame
        elif self.update_method=="integrate":
            self.my_array[:,:,self.channel[self.image_colour]] += new_frame

        self.base_turn_pixels_on_and_off()

    def base_turn_pixels_on_and_off(self):
        """
        Turn pixels alpha channels on and off. 

        Attributes needed to be set are:
        * `my_array`
        * `channel`
        * `image_colour`
        * `alpha`
        * `max_val`
        * `min_val`
        """
        _frame = self.my_array[:,:,self.channel[self.image_colour]]
        _lowest_value_to_view = np.max(_frame)/1e6 #i.e., dynamic range of 1e6
        self.my_array[:,:,self.alpha][_frame>_lowest_value_to_view] = self.max_val
        self.my_array[:,:,self.alpha][_frame<=_lowest_value_to_view] = self.min_val

    def base_fade_control(self, new_hits_array, control_with="rgb"):
        """
        Fades out pixels that haven't had a new count in steps of `self.max_val//self.fade_out` until a pixel has not had an 
        event for `self.fade_out` frames. If a pixel has not had a detection in `self.fade_out` frames then reset the colour 
        channel to zero and the alpha channel back to `self.max_val`.


        Attributes needed to be set are:
        * `no_new_hits_counter_array`
        * `colour_mode`
        * `my_array`
        * `alpha`
        * `max_val`
        * `fade_out`
        * `_min_fade_alpha`
        * `channel`
        * `image_colour`

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

    def base_set_image_ndarray(self):
        """
        Set-up the numpy array and define colour format from `self.colour_mode`.
        """
        # do we want alpha channel or not
        if self.colour_mode == "rgba":
            self.my_array = np.zeros((self.deth, self.detw, 4))
            # for all x and y, turn alpha to max
            self.my_array[:,:,3] = self.max_val 
        if self.colour_mode == "rgb":
            self.my_array = np.zeros((self.deth, self.detw, 3))

        # define array to keep track of the last hit to each pixel
        self.no_new_hits_counter_array = (np.zeros((self.deth, self.detw)))

    # window/GUI methods
    def eventFilter(self, obj, event):
        """ 
        Allows better event handling that matplotlib for hovering 
        mouse actions. 
        """
        # clue for these types is in printout of `print(event.type(), event)` which gives `Type.Enter <PyQt6.QtGui.QEnterEvent object at 0x13997af80>`
        if event.type() == QtCore.QEvent.Type.Enter:
            self.base_qwidget_entered_signal.emit()
        elif event.type() == QtCore.QEvent.Type.Leave:
            self.base_qwidget_left_signal.emit()
        return super(BaseWindow, self).eventFilter(obj, event)
    
    def base_update_aspect(self, aspect_ratio):
        """ Update the image aspect ratio (width/height). """
        self.aspect_ratio = aspect_ratio

    def resizeEvent(self,event):
        """ Define how the widget can be resized and keep the same apsect ratio. """
        super().resizeEvent(event)
        # Create a square base size of 10x10 and scale it to the new size
        # maintaining aspect ratio.
        # if self.plotting_product=="spectrogram":
        #     print("ere", event.size().width(), event.size().height())
        if event is None:
            return 
        
        new_size = QtCore.QSize(self.detw, int(self.detw / self.aspect_ratio)) #width, height/(width/height)
        new_size.scale(event.size(), QtCore.Qt.AspectRatioMode.KeepAspectRatio)

        self.resize(new_size)

