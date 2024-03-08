"""
A class to help handle displaying a matplotlib image in a PyQt window.
"""

import numpy as np
from matplotlib import transforms
# from matplotlib.pyplot import draw, pause

from PyQt6 import QtCore
from PyQt6.QtWidgets import QApplication, QSizePolicy, QVBoxLayout, QGridLayout, QWidget
import pyqtgraph as pg

from FoGSE.windows.mpl.MPLCanvas import MPLCanvas
        

class Image(QWidget):
    """
    An individual window to display Timepix data read from a file.

    Parameters
    ----------
    pcolormesh : `dict`, `NoneType` 
        Information to get a `pcolormesh` plot on the go.
        E.g., `{"x_bins":np.arange(151), "y_bins":np.arange(201), "data_matrix":np.zeros((200, 150))}`.
        Default: None
    
    imshow : `dict`, `NoneType`  
        Information to get a `pcolormesh` plot on the go. The `pcolormesh`
        input takes priority.
        E.g., `{"data_matrix":_zeros}`.
        Default: None
    
    rotation : `int`, `float`, etc.
        The rotation affine transormation angle to be applied to the 
        axes (not the data).
        Default: 0
    
    custom_plotting_kwargs : `dict`, `NoneType` 
        Any custom kwargs that are required to be sent to `.pcolormesh(**custom_plotting_kwargs)` 
        or `.imshow(**custom_plotting_kwargs). E.g., `{"vmin":0, "vmax":1}`
    """

    mpl_click_signal = QtCore.pyqtSignal()
    mpl_axes_enter_signal = QtCore.pyqtSignal()
    mpl_axes_leave_signal = QtCore.pyqtSignal()

    def __init__(self, pcolormesh=None, imshow=None, rotation=0, custom_plotting_kwargs=None, name="image", parent=None):
        pg.setConfigOption('background', (255,255,255, 0)) # needs to be first

        QWidget.__init__(self, parent)

        self.detw, self.deth = 400, 400
        self.aspect_ratio = self.detw / self.deth
        # self.resize(self.detw, self.deth)

        self.pcolormesh = pcolormesh
        self.imshow = imshow
        custom_plotting_kwargs = {} if custom_plotting_kwargs is None else custom_plotting_kwargs

        self.graphPane = MPLCanvas(self)

        self.layoutMain = QVBoxLayout()
        self.layoutMain.addWidget(self.graphPane)

        self.layoutMain.setContentsMargins(0, 0, 0, 0)
        self.layoutMain.setSpacing(0)

        tr = transforms.Affine2D().rotate_deg(rotation) #rotation_in_degrees
        # "cmap" is ignored if data is RGB(A)
        _plotting_kwargs = {"origin":"lower", "rasterized":True, "cmap":"viridis", "transform":tr + self.graphPane.axes.transData} | custom_plotting_kwargs

        # Create the pcolormesh plot
        if self.pcolormesh is not None:
            _plotting_kwargs.pop("origin", None)
            self.im_obj = self.graphPane.axes.pcolormesh(self.pcolormesh["x_bins"], self.pcolormesh["y_bins"], self.pcolormesh["data_matrix"], **_plotting_kwargs)
        elif self.imshow is not None:
            self.im_obj = self.graphPane.axes.imshow(self.imshow["data_matrix"], **_plotting_kwargs)
            self.get_new_limits_post_rotation(affine_transform=_plotting_kwargs["transform"])
        else:
            print("Please, I need to know `pcolormesh` or `imshow` at least!")

        self.graphPane.axes.axis('off')
        self.graphPane.axes.set_aspect('equal')  # Maintain aspect ratio (optional)

        self.setLayout(self.layoutMain)
        
        self.graphPane.mpl_connect("button_press_event", self.on_click)
        self.graphPane.mpl_connect("axes_enter_event", self.on_enter)
        self.graphPane.mpl_connect("axes_leave_event", self.on_leave)

    def on_click(self,event):
        """ 
        The matplotlib way needs a method to shout when it is interacted with. 

        Sends a signal if the plot is clicked on by the mouse.

        Other connections exist. [1]

        [1] https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.pyplot.connect.html
        """
        self.mpl_click_signal.emit()

    def on_enter(self, event):
        """ 
        The matplotlib way needs a method to shout when it is interacted with. 

        Sends a signal if the mouse enters the plot (started hovering).

        Other connections exist. [1]

        [1] https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.pyplot.connect.html
        """
        # https://stackoverflow.com/questions/7908636/how-to-add-hovering-annotations-to-a-plot
        self.mpl_axes_enter_signal.emit()

    def on_leave(self, event):
        """ 
        The matplotlib way needs a method to shout when it is interacted with. 

        Sends a signal if the mouse leaves the plot (ended hovering).

        Other connections exist. [1]

        [1] https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.pyplot.connect.html
        """
        # https://stackoverflow.com/questions/7908636/how-to-add-hovering-annotations-to-a-plot
        self.mpl_axes_leave_signal.emit()

    def get_new_limits_post_rotation(self, affine_transform):
        """ 
        So `imshow()` does not rescale the limits of the plot after performing 
        an affine transformation to it so need to find the new plot limits
        after a rotation has been performed.

        Note: `pcolormesh` rescales its limts by default.
        """
        # extent is for non-rotated array
        x1, x2, y1, y2 = self.im_obj.get_extent() 

        # maybe I will return and see if there is a more direct way, but for now...
        # get new display coordniates of the image corners after the transform
        new_display_corners = affine_transform.transform([(x1,y1), (x2,y1), (x1,y2), (x2,y2)])
        # can now convert the display coords to data coords
        new_data_corners = np.array(self.graphPane.axes.transData.inverted().transform(new_display_corners))

        self.graphPane.axes.set_xlim([np.min(new_data_corners[:,0]), 
                                      np.max(new_data_corners[:,0])])
        self.graphPane.axes.set_ylim([np.min(new_data_corners[:,1]), 
                                      np.max(new_data_corners[:,1])])

    def _replace_values(self, matrix, replace):
        """
        Given a dictionary, replace the entries with values "this" with 
        the value indicated by "with" in `matrix`.

        E.g., replace = {"this":[0, 500, 453], "with":[np.nan, 475, 450]}
        would mean to replace all 0s, 500s, and 453s in `matrix` 
        with np.nan, 475, and 450, respectively.
        """
        if replace is None:
            return matrix
        
        if len(replace["this"])!=len(replace["with"]):
            print("`replace` 'this' and 'with' keys do not have lists the same length.")

        for t, w in zip(replace["this"],replace["with"]):
            matrix[np.where(matrix==t)] = w

        return matrix

    def add_plot_data(self, new_matrix, replace=None):
        """ Adds the new data to the array to be plotted. """

        new_matrix = self._replace_values(new_matrix, replace)
        
        if self.pcolormesh is not None:
            self.im_obj.set_array(new_matrix)
        elif self.imshow is not None:
            self.im_obj.set_data(new_matrix)

        self.graphPane.draw()

    def set_labels(self, graph_widget, xlabel="", ylabel="", title="", fontsize=9, ticksize=9, titlesize=10, offsetsize=1):
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
        graph_widget.axes.set_title(title, size=titlesize)#, **styles)

        # Set label for both axes
        graph_widget.axes.set_xlabel(xlabel, size=fontsize)#, **styles)
        graph_widget.axes.set_ylabel(ylabel, size=fontsize)#, **styles)

        graph_widget.axes.tick_params(axis='both', which='major', labelsize=ticksize)
        graph_widget.axes.tick_params(axis='both', which='minor', labelsize=ticksize)

        # this handles the exponent, if the data is in 1e10 then it is 
        # usually plotted in smaller numbers with 1e10 off to the side.
        # `get_offset_text` controls the "1e10"
        t = graph_widget.axes.xaxis.get_offset_text()
        t.set_size(offsetsize)

    def resizeEvent(self,event):
        """ Define how the widget can be resized and keep the same apsect ratio. """
        super().resizeEvent(event)
        
        if event is None:
            return 
        
        new_size = QtCore.QSize(self.detw, int(self.detw / self.aspect_ratio)) #width, height/(width/height)
        new_size.scale(event.size(), QtCore.Qt.AspectRatioMode.KeepAspectRatio)

        self.resize(new_size)


class ImageExample(QWidget):
    """
    An individual window to display Timepix data read from a file.

    Parameters
    ----------

    reader : instance of `FoGSE.read_raw_to_refined.readRawToRefinedBase.ReaderBase()`
        The reader already given a file.
        Default: None

    x_size, y_size : `int`
        Width and height of image in pixels.

    Example
    -------
    from FoGSE.read_raw_to_refined.readRawToRefinedBase import ReaderBase

    class ImageFakeReader(ReaderBase):
        \"""
        Reader for fake image arrays.
        \"""

        def __init__(self, array_x, array_y, parent=None):
            \"""
            Raw : binary
            Parsed : human readable
            Collected : organised by intrumentation
            \"""
            ReaderBase.__init__(self, "", parent)

            self.array_x, self.array_y = array_x, array_y
            
            self.call_interval(10)

        def extract_raw_data(self):
            \"""
            Generate random array.

            Returns
            -------
            `numpy.ndarray` :
                Random frame.
            \"""
            rand_array = np.random.rand(self.array_y, self.array_x)
            rand_array[0, 0] = -1 #stays the same always, to help track orientaion
            rand_array[-1, -1] = 1 #stays the same always, to help track orientaion
            return rand_array
        
        def raw_2_collected(self):
            \""" 
            Method to control the flow from raw data to parsed to 
            collected. 

            Sets the `collections` attribute.
            \"""

            # assign the collected data and trigger the `emit`
            self.collection = self.extract_raw_data()
            self.value_changed_collection.emit()

    def initiate_gui():
        app = QApplication([])
        array_x, array_y = 300, 200
        R = ImageFakeReader(array_x, array_y)

        f0 = ImageExample(R, array_x, array_y)

        f0.show()
        app.exec()

    initiate_gui()
    """
    def __init__(self, reader, x_size, y_size, parent=None, name="Images"):

        pg.setConfigOption('background', (255,255,255, 0)) # needs to be first

        QWidget.__init__(self, parent)

        # decide how to read the data
        self.reader = reader

        _x_size, _y_size = x_size, y_size
        pcol_xs, pcol_ys = np.arange(_x_size+1), np.arange(_y_size+1)+20.3
        _zeros = np.zeros((_y_size, _x_size))
        self.imsh0 = Image(imshow={"data_matrix":_zeros}, rotation=0, custom_plotting_kwargs={"vmin":0, "vmax":1})
        self.pcol0 = Image(pcolormesh={"x_bins":pcol_xs, "y_bins":pcol_ys, "data_matrix":_zeros}, rotation=0, custom_plotting_kwargs={"vmin":0, "vmax":1})
        r1_imsh = -120
        self.imsh1 = Image(imshow={"data_matrix":_zeros}, rotation=r1_imsh, custom_plotting_kwargs={"vmin":0, "vmax":1})
        r1_pcol = 45
        self.pcol1 = Image(pcolormesh={"x_bins":pcol_xs, "y_bins":pcol_ys, "data_matrix":_zeros}, rotation=r1_pcol, custom_plotting_kwargs={"vmin":0, "vmax":1})
        r2_imsh = -10
        self.imsh2 = Image(imshow={"data_matrix":_zeros}, rotation=r2_imsh, custom_plotting_kwargs={"vmin":0, "vmax":1})
        r2_pcol = 60
        self.pcol2 = Image(pcolormesh={"x_bins":pcol_xs, "y_bins":pcol_ys, "data_matrix":_zeros}, rotation=r2_pcol, custom_plotting_kwargs={"vmin":0, "vmax":1})

        self.imsh0.set_labels(self.imsh0.graphPane, xlabel="", ylabel="", title="Imshow")
        self.pcol0.set_labels(self.pcol0.graphPane, xlabel="", ylabel="", title="Pcolormesh")
        self.imsh1.set_labels(self.imsh1.graphPane, xlabel="", ylabel="", title=f"Imshow: rot of {r1_imsh} deg")
        self.pcol1.set_labels(self.pcol1.graphPane, xlabel="", ylabel="", title=f"Pcolormesh: rot of {r1_pcol} deg")
        self.imsh2.set_labels(self.imsh2.graphPane, xlabel="", ylabel="", title=f"Imshow: rot of {r2_imsh} deg (RGBA)")
        self.pcol2.set_labels(self.pcol2.graphPane, xlabel="", ylabel="", title=f"Pcolormesh: rot of {r2_pcol} deg (RGBA)")

        self.reader.value_changed_collection.connect(self.update_plot)

        self.layoutMain = QGridLayout()
        self.layoutMain.setContentsMargins(0, 0, 0, 0)
        self.layoutMain.setSpacing(0)
        self.layoutMain.addWidget(self.imsh0, 0, 0)
        self.layoutMain.addWidget(self.pcol0, 1, 0)
        self.layoutMain.addWidget(self.imsh1, 0, 1)
        self.layoutMain.addWidget(self.pcol1, 1, 1)
        self.layoutMain.addWidget(self.imsh2, 0, 2)
        self.layoutMain.addWidget(self.pcol2, 1, 2)
        self.setLayout(self.layoutMain)

        self.detw, self.deth = self.imsh0.detw*3, self.imsh0.deth*2
        self.aspect_ratio = self.detw / self.deth

        self.setMinimumSize(self.detw, self.deth)
        self.resize(self.detw, self.deth)

    def update_plot(self):
        """
        Defines how the plot window is updated for time series.

        In subclass define methods: 
        *`get_data` to extract the new image frame from `self.data_file`, 
        *`update_image` to define how the new image affects the current one,
        *`process_data` to perform any last steps before updating the plot.
        """
        
        new_array = self.reader.collection
        
        # defined how to add/append onto the new data arrays
        self.imsh0.add_plot_data(new_array)
        self.pcol0.add_plot_data(new_array)
        self.imsh1.add_plot_data(new_array)
        self.pcol1.add_plot_data(new_array)

        new_array = (new_array-np.min(new_array))/(np.max(new_array)-np.min(new_array))
        _zs = np.zeros(np.shape(new_array))
        rgba_array_blue = np.concatenate((_zs[:,:,None], _zs[:,:,None], new_array[:,:,None], new_array[:,:,None]), axis=2)
        self.imsh2.add_plot_data(rgba_array_blue)
        rgba_array_red = np.concatenate((new_array[:,:,None], _zs[:,:,None], _zs[:,:,None], new_array[:,:,None]), axis=2)
        self.pcol2.add_plot_data(rgba_array_red)

    def resizeEvent(self,event):
        """ Define how the widget can be resized and keep the same apsect ratio. """
        super().resizeEvent(event)
        
        if event is None:
            return 
        
        new_size = QtCore.QSize(self.detw, int(self.detw / self.aspect_ratio)) #width, height/(width/height)
        new_size.scale(event.size(), QtCore.Qt.AspectRatioMode.KeepAspectRatio)

        self.resize(new_size)
    

if __name__=="__main__":
    # package top-level

    from FoGSE.read_raw_to_refined.readRawToRefinedBase import ReaderBase

    class ImageFakeReader(ReaderBase):
        """
        Reader for fake image arrays.
        """

        def __init__(self, array_x, array_y, parent=None):
            """
            Raw : binary
            Parsed : human readable
            Collected : organised by intrumentation
            """
            ReaderBase.__init__(self, "", parent)

            self.array_x, self.array_y = array_x, array_y
            
            self.call_interval(10)

        def extract_raw_data(self):
            """
            Generate random array.

            Returns
            -------
            `numpy.ndarray` :
                Random frame.
            """
            rand_array = np.random.rand(self.array_y, self.array_x)
            rand_array[0, 0] = -1 #stays the same always, to help track orientaion
            rand_array[-1, -1] = 1 #stays the same always, to help track orientaion
            return rand_array
        
        def raw_2_collected(self):
            """ 
            Method to control the flow from raw data to parsed to 
            collected. 

            Sets the `collections` attribute.
            """

            # assign the collected data and trigger the `emit`
            self.collection = self.extract_raw_data()
            self.value_changed_collection.emit()

    def initiate_gui():
        app = QApplication([])
        array_x, array_y = 300, 200
        R = ImageFakeReader(array_x, array_y)

        f0 = ImageExample(R, array_x, array_y)

        f0.show()
        app.exec()

    initiate_gui()