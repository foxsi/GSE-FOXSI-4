"""
A class to help handle displaying a matplotlib image in a PyQt window.
"""

import numpy as np
from matplotlib import transforms
import sys

from PyQt6 import QtCore
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QGridLayout, QWidget
import pyqtgraph as pg

from FoGSE.windows.images.patches import circle_patch
from FoGSE.windows.mpl.MPLCanvas import MPLCanvas
        

class Image(QWidget):
    """
    An individual window to display Timepix data read from a file.

    Updated with the `add_plot_data()` method.

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

    keep_aspect : `bool`
        Defines whether to plot the axes spines, ticks and tick-marks.
        Default: False

    keep_aspect : `bool`
        Defines whether it is important to keep the aspect ratio of the 
        plot.
        Default: False
    
    loose_axes : `bool`
        Set to True to avoid removing some whitespace around the axes.
        Default: False
    
    custom_plotting_kwargs : `dict`, `NoneType` 
        Any custom kwargs that are required to be sent to `.pcolormesh(**custom_plotting_kwargs)` 
        or `.imshow(**custom_plotting_kwargs). E.g., `{"vmin":0, "vmax":1}`

    figure_kwargs : `dict`, `NoneType` 
        Any custom kwargs that are required to be sent to the `matplotlib.figure.Figure`
        when creating the plot.
    """

    mpl_click_signal = QtCore.pyqtSignal()
    mpl_axes_enter_signal = QtCore.pyqtSignal()
    mpl_axes_leave_signal = QtCore.pyqtSignal()

    def __init__(self, pcolormesh=None, imshow=None, rotation=0, keep_axes=False, keep_aspect=False, loose_axes=False, custom_plotting_kwargs=None, figure_kwargs=None, parent=None):
        """ 
        Set up the plot with an initial grid of zeros, limits, etc., and 
        connect some `matplotlib` connections to methods that emit some 
        `PyQt6` signals.
        """

        QWidget.__init__(self, parent)

        self.detw, self.deth = 400, 400
        self.aspect_ratio = self.detw / self.deth
        # self.resize(self.detw, self.deth)

        self.rotation = rotation
        self.pcolormesh = pcolormesh
        self.imshow = imshow
        custom_plotting_kwargs = {} if custom_plotting_kwargs is None else custom_plotting_kwargs
        figure_kwargs = {} if figure_kwargs is None else figure_kwargs

        self.graphPane = MPLCanvas(self, **figure_kwargs)

        self.layoutMain = QVBoxLayout()
        self.layoutMain.addWidget(self.graphPane)

        self.layoutMain.setContentsMargins(0, 0, 0, 0)
        self.layoutMain.setSpacing(0)

        tr = transforms.Affine2D().rotate_deg(self.rotation) #rotation_in_degrees
        # "cmap" is ignored if data is RGB(A)
        _plotting_kwargs = {"origin":"lower", "interpolation":"nearest", "rasterized":True, "transform":tr + self.graphPane.axes.transData} | custom_plotting_kwargs
        self.affine_transform =_plotting_kwargs["transform"]

        # Create the pcolormesh plot
        if self.pcolormesh is not None:
            _plotting_kwargs.pop("origin", None)
            _plotting_kwargs.pop("interpolation", None)
            self.im_obj = self.graphPane.axes.pcolormesh(self.pcolormesh["x_bins"], self.pcolormesh["y_bins"], self.pcolormesh["data_matrix"], **_plotting_kwargs)
        elif self.imshow is not None:
            self.im_obj = self.graphPane.axes.imshow(self.imshow["data_matrix"], **_plotting_kwargs)
            self.get_new_limits_post_rotation()
        else:
            print("Please, I need to know `pcolormesh` or `imshow` at least!")

        if not keep_axes:
            self.graphPane.axes.axis('off')
        if not loose_axes:
            self.graphPane.fig.tight_layout(pad=0)
            self.graphPane.fig.subplots_adjust(left=0, bottom=0, right=1, top=1)
        if keep_aspect:
            self.graphPane.axes.set_aspect('equal')  # Maintain aspect ratio

        self.setLayout(self.layoutMain)
        
        self.graphPane.mpl_connect("button_press_event", self.on_click)
        self.graphPane.mpl_connect("axes_enter_event", self.on_enter)
        self.graphPane.mpl_connect("axes_leave_event", self.on_leave)

    def on_click(self, event):
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

    def points_post_rotation(self, data_points):
        """ Given data-points before any rotation, get their new coordinates. """

        # maybe I will return and see if there is a more direct way, but for now...
        # get new display coordniates of the image corners after the transform
        new_display_corners = self.affine_transform.transform(data_points)
        # can now convert the display coords to data coords
        return np.array(self.graphPane.axes.transData.inverted().transform(new_display_corners))

    def get_new_limits_post_rotation(self):
        """ 
        So `imshow()` does not rescale the limits of the plot after performing 
        an affine transformation to it so need to find the new plot limits
        after a rotation has been performed.

        Note: `pcolormesh` rescales its limts by default.
        """

        new_data_corners = self.get_new_corners()

        self.graphPane.axes.set_xlim([np.min(new_data_corners[:,0]), 
                                      np.max(new_data_corners[:,0])])
        self.graphPane.axes.set_ylim([np.min(new_data_corners[:,1]), 
                                      np.max(new_data_corners[:,1])])
        
    def get_image_extent(self):
        """ Get the extent of the image. """
        if self.pcolormesh is not None:
            x1, x2 = self.pcolormesh["x_bins"][0], self.pcolormesh["x_bins"][-1]
            y1, y2 = self.pcolormesh["y_bins"][0], self.pcolormesh["y_bins"][-1]
        elif self.imshow is not None:
            # extent is for non-rotated array
            x1, x2, y1, y2 = self.im_obj.get_extent() 
        return x1, x2, y1, y2
        
    def get_new_corners(self):
        """ After any rotation, where are the image corners. """
        x1, x2, y1, y2 = self.get_image_extent()

        return self.points_post_rotation(data_points=[(x1,y1), (x2,y1), (x1,y2), (x2,y2)])
    
    def draw_extent(self, **kwargs):
        """ 
        Method to draw box around new rotated image. 
        
        **kwargs:
            Passed to `matplotlib.pyplot.plot`.
        """
        x1, x2, y1, y2 = self.get_new_axes_post_rotation()

        xs = [x1, x2, x2, x1, x1]
        ys = [y1, y1, y2, y2, y1]

        _plotting_kwargs = {"transform":self.affine_transform} | kwargs
        
        # still have to apply rotation afterwords for some reason
        self.extent_box = self.im_obj.axes.plot(xs, ys, **_plotting_kwargs)
        self.graphPane.fig.canvas.draw()
    
    def remove_extent(self):
        """ Remove the extent box drawn by `draw_extent`."""
        if hasattr(self, "extent_box"):
            line = self.extent_box.pop(0)
            line.remove()
            del self.extent_box
            self.graphPane.fig.canvas.draw()

    def get_new_axes_post_rotation(self):
        """
        Attempt to get new plot corners after rotation.
        """
        if self.pcolormesh is not None:
            x1, x2 = self.pcolormesh["x_bins"][0], self.pcolormesh["x_bins"][-1]
            y1, y2 = self.pcolormesh["y_bins"][0], self.pcolormesh["y_bins"][-1]
        elif self.imshow is not None:
            x1, x2, y1, y2 = self.im_obj.get_extent() 

        return x1, x2, y1, y2
        
    def get_new_axes_labels_post_rotation(self):
        """
        Attempt to plot axes labels after rotation.
        """
        # extent is for non-rotated array
        x1, x2, y1, y2 = self.get_new_axes_post_rotation()

        x_label_pos, y_label_pos = self.points_post_rotation(data_points=[(np.mean([x1, x2]), y1), (x1, np.mean([y1, y2]))])

        return x_label_pos, y_label_pos

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
            matrix[np.nonzero(matrix==t)] = w

        return matrix

    def add_plot_data(self, new_matrix, replace=None):
        """ 
        Adds the new data to the array to be plotted. 
        
        Parameters
        ----------
        new_matrix : `numpy.ndarray`
            The new image array to be plotted.

        replace : `dict`
            Input for the `_replace_values` method. 
            E.g., {"this":[0, 500, 453], "with":[np.nan, 475, 450]}
            would mean to replace all 0s, 500s, and 453s in `matrix` 
            with np.nan, 475, and 450, respectively.
            Default: None
        """

        new_matrix = self._replace_values(new_matrix, replace)

        self.im_obj.set_array(new_matrix)
        self.graphPane.fig.canvas.draw()
        self.graphPane.fig.canvas.flush_events()

    def set_labels(self, xlabel="", ylabel="", title="", xlabel_kwargs=None, ylabel_kwargs=None, title_kwargs=None):
        """
        Method just to easily set the x, y-label and title.

        Parameters
        ----------

        xlabel, ylabel, title : `str`
            The strings relating to each label to be set.
            Defaults: "", "", ""

        xlabel_kwargs, ylabel_kwargs, title_kwargs : `dict`, `dict`, `dict`
            Keywords to be passed to the title and axis labels.
            Defaults: None, None, None
        """
        xlabel_kwargs = {} if xlabel_kwargs is None else xlabel_kwargs
        ylabel_kwargs = {} if ylabel_kwargs is None else ylabel_kwargs
        title_kwargs = {} if title_kwargs is None else title_kwargs

        _title_kwargs = {"size":10} | title_kwargs

        self.graphPane.axes.set_title(title, **_title_kwargs)

        # Set label for both axes
        # if a rotation has happened to the image then find new label positions
        x_label_pos, y_label_pos = self.get_new_axes_labels_post_rotation()
        # want the labels to not go upside down
        x_rot = self.rotation if -90<=self.rotation<=90 else self.rotation-180
        y_rot = self.rotation+90 if -180<=self.rotation<=0 else self.rotation-90
        # make the labels
        _xlabel_kwargs = {"size":9, "rotation":x_rot, "va":"center", "ha":"center"} | xlabel_kwargs
        _ylabel_kwargs = {"size":9, "rotation":y_rot, "va":"center", "ha":"center"} | ylabel_kwargs
        self.graphPane.axes.text(*x_label_pos, xlabel, **_xlabel_kwargs)
        self.graphPane.axes.text(*y_label_pos, ylabel, **_ylabel_kwargs)

    def add_label(self, label_pos, label, **kwargs):
        """ 
        Method to add labels to the image plot. 

        Parameters
        ----------
        label_pos : `tuple`
            A tuple of an x- and y-coordinate for the text. Default is to 
            work in \"axes fraction\".

        label : `str`
            The string of text to be drawn.

        **kwargs : 
            Any kwargs to be passed to `matplotlib.text.Annotation`.
        """
        label_kwargs = {"xycoords":"axes fraction"} | kwargs
        return self.graphPane.axes.annotate(label, label_pos, **label_kwargs)

    def add_patch(self, patch):
        """ 
        Method to add patches to the image plot. [1,2] 

        [1] https://matplotlib.org/stable/api/_as_gen/matplotlib.patches.Patch.html
        [2] https://matplotlib.org/stable/api/patches_api.html

        Parameters
        ----------
        patch : `matplotlib.patches.Patch`
            A patch to add to the image.
        """
        self.graphPane.axes.add_patch(patch)

    def draw_arc_distances(self, arc_distance_list, label_pos="top", **kwargs):
        """ 
        Draw a set of arc-distance contours. 
        
        Parameters
        ----------
        arc_distance_list : `list[int, float, etc]`
            The arc-distance radii from the field of view centre. Note,
            the data should already be plotted in arcminutes.

        label_pos : `str`
            Where on the circle should the text be plotted. Will always 
            read from left to right. can pass rotation as a `kwarg` to 
            rotate the text. Options are [\"top\", \"bottom\", \"left\", 
            \"right\"]
            Default: "top"

        **kwargs : 
            To be passed to `add_label`.
        """

        _plotting_kwargs = {"transform":self.affine_transform, "edgecolor":"whitesmoke", "alpha":0.5, "linestyle":"--", "zorder":1} | kwargs

        label_pos_map = {"top":(0,1), "bottom":(0,-1), "left":(-1,0), "right":(1,0)}
        
        self.texts = []
        for arcds in arc_distance_list:
            self.texts.append(self.add_label(np.array(label_pos_map[label_pos])*arcds, f"{round(arcds, 2)}$'$", xycoords="data", size=5, color="w", alpha=0.75, ha="center"))
            self.add_patch(circle_patch(radius=arcds, **_plotting_kwargs))
            
        self.graphPane.fig.canvas.draw()

    def remove_arc_distances(self):
        """ If the arc-distances are there then remove them. """
        [p.remove() for p in self.graphPane.axes.patches]
        [t.remove() for t in self.texts]     
        del self.texts
        self.graphPane.fig.canvas.draw()


    def update_aspect(self, aspect_ratio):
        """ Update the image aspect ratio (width/height). """
        self.aspect_ratio = aspect_ratio

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

    reader : instance of `FoGSE.readers.BaseReader.BaseReader()`
        The reader already given a file.
        Default: None

    x_size, y_size : `int`
        Width and height of image in pixels.

    Example
    -------
    from FoGSE.readers.BaseReader import BaseReader

    class ImageFakeReader(BaseReader):
        \"""
        Reader for fake image arrays.
        \"""

        def __init__(self, array_x, array_y, parent=None):
            \"""
            Raw : binary
            Parsed : human readable
            Collected : organised by intrumentation
            \"""
            BaseReader.__init__(self, "", parent)

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
        """ Just put some examples of the `Image` class in a grid. """
        pg.setConfigOption('background', (255,255,255, 0)) # needs to be first

        QWidget.__init__(self, parent)

        # decide how to read the data
        self.reader = reader

        _x_size, _y_size = x_size, y_size
        pcol_xs, pcol_ys = np.arange(_x_size+1)**2, np.arange(_y_size+1)**2+20.3
        _im_zeros, _pcol_zeros = np.zeros((_y_size, _x_size)), np.zeros((_y_size, _x_size))
        self.imsh0 = Image(imshow={"data_matrix":_im_zeros}, rotation=0, keep_aspect=True, custom_plotting_kwargs={"vmin":0, "vmax":1})
        self.pcol0 = Image(pcolormesh={"x_bins":pcol_xs, "y_bins":pcol_ys, "data_matrix":_pcol_zeros}, rotation=0, keep_aspect=True, custom_plotting_kwargs={"vmin":0, "vmax":1})
        r1_imsh = -120
        self.imsh1 = Image(imshow={"data_matrix":_im_zeros}, rotation=r1_imsh, keep_aspect=True, custom_plotting_kwargs={"vmin":0, "vmax":1})
        r1_pcol = 45
        self.pcol1 = Image(pcolormesh={"x_bins":pcol_xs, "y_bins":pcol_ys, "data_matrix":_pcol_zeros}, rotation=r1_pcol, keep_aspect=True, custom_plotting_kwargs={"vmin":0, "vmax":1})
        r2_imsh = -10
        self.imsh2 = Image(imshow={"data_matrix":_im_zeros}, rotation=r2_imsh, keep_aspect=True, custom_plotting_kwargs={"vmin":0, "vmax":1})
        r2_pcol = 60
        self.pcol2 = Image(pcolormesh={"x_bins":pcol_xs, "y_bins":pcol_ys, "data_matrix":_pcol_zeros}, rotation=r2_pcol, keep_aspect=True, custom_plotting_kwargs={"vmin":0, "vmax":1, "linewidth":0, "antialiased":True})

        self.imsh0.set_labels(xlabel="X-Axis", ylabel="Y-Axis", title="Imshow")
        self.pcol0.set_labels(xlabel="X-Axis", ylabel="Y-Axis", title="Pcolormesh")
        self.imsh1.set_labels(xlabel="X-Axis", ylabel="Y-Axis", title=f"Imshow: rot of {r1_imsh} deg")
        self.pcol1.set_labels(xlabel="X-Axis", ylabel="Y-Axis", title=f"Pcolormesh: rot of {r1_pcol} deg")
        self.imsh2.set_labels(xlabel="X-Axis", ylabel="Y-Axis", title=f"Imshow: rot of {r2_imsh} deg (RGBA)")
        self.pcol2.set_labels(xlabel="X-Axis", ylabel="Y-Axis", title=f"Pcolormesh: rot of {r2_pcol} deg (RGBA)")

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

        self.reader.value_changed_collection.connect(self.update_plot)

    def update_plot(self):
        """
        Defines how the plot window is updated for time series.

        In subclass define methods: 
        *`get_data` to extract the new image frame from `self.data_file`, 
        *`update_image` to define how the new image affects the current one,
        *`process_data` to perform any last steps before updating the plot.
        """
        
        new_array = self.reader.collection
        print("adding data")
        
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

    def closeEvent(self, event):
        """ 
        On close, ensure that the reader's timer is stop.
        
        If the reader and plot updating are going quick enough this 
        start to go a bit mad. This can mean that when the window is
        closed that the reader is too quick to be stopped automatically.
        This method ensure that, as part of the window closing process, 
        the `QTimer` in `reader` is stopped allowing everything to close
        properly.
        """
        self.reader.timer.stop()
        self.deleteLater()
    

if __name__=="__main__":
    # package top-level

    from FoGSE.readers.BaseReader import BaseReader

    class ImageFakeReader(BaseReader):
        """
        Reader for fake image arrays.

        Just generates a random array of a given size on a timer setting 
        the `collection` attribute` each timer loop cycle.
        """

        def __init__(self, array_x, array_y, parent=None):
            """
            Raw : binary
            Parsed : human readable
            Collected : organised by intrumentation
            """
            BaseReader.__init__(self, "", parent)

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
            print("new data")
            self.collection = self.extract_raw_data()


    def initiate_gui():
        app = QApplication([])
        array_x, array_y = 700, 650
        R = ImageFakeReader(array_x, array_y)

        f0 = ImageExample(R, array_x, array_y)

        f0.show()

        f1 = ImageExample(R, array_x, array_y)

        f1.show()

        sys.exit(app.exec())

    initiate_gui()