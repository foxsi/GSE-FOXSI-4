"""
A class to help handle displaying a matplotlib lie plot in a PyQt window.
"""

import numpy as np

from PyQt6 import QtCore
from PyQt6.QtWidgets import QApplication, QSizePolicy, QVBoxLayout, QWidget
import pyqtgraph as pg

from FoGSE.windows.mpl.MPLCanvas import MPLCanvas

from FoGSE.readers.TimepixReader import TimepixReader
        

class LightCurve(QWidget):
    """
    A line profile class.

    Updated with the `add_plot_data()` method.

    Parameters
    ----------
    colour : `str`, `tuple[float]`
        This is the colour of the line being plotted. It could actually 
        be anything a `matplotlib.pyplot` plot will accept as a colour.
        Default: "b"

    facecolour : `str`, `tuple[float]`
        This sets the colour inside the plot axes.
        Default: "w"

    ylim : `list[float, float]` or `NoneType`
    """

    mpl_click_signal = QtCore.pyqtSignal()

    def __init__(self, colour="b", facecolour="w", ylim=None, parent=None):
        """ 
        Set up the plot with the initial plot settings and connect some 
        `matplotlib` connections to methods that emit some `PyQt6` signals.
        """

        QWidget.__init__(self, parent)

        self.detw, self.deth = 400, 150
        self.aspect_ratio = self.detw / self.deth

        self.ylim = ylim

        self.graphPane = MPLCanvas(self)

        self.layoutMain = QVBoxLayout()
        self.layoutMain.addWidget(self.graphPane)

        self.layoutMain.setContentsMargins(0, 0, 0, 0)
        self.layoutMain.setSpacing(0)

        self._plot_ref = None
        self.plot_data_ys = np.array([-1]).astype(float)
        self.plot_data_xs = np.array([-1]).astype(float)
        self._remove_first = True

        plot_refs = self.graphPane.axes.plot(self.plot_data_xs, self.plot_data_ys, colour, marker="o", ms=4)
        self._plot_ref = plot_refs[0]

        self.keep_entries = 60 # entries

        self.setLayout(self.layoutMain)

        self.graphPane.axes.set_facecolor(facecolour)
        
        self.counter = 1
        
        self.graphPane.mpl_connect("button_press_event", self.on_click)

    def on_click(self, event):
        """ 
        The matplotlib way needs a method to shout when it is interacted with. 

        Sends a signal if the plot is clicked on by the mouse.

        Other connections exist. [1]

        [1] https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.pyplot.connect.html
        """
        self.mpl_click_signal.emit()

    def manage_plotting_ranges(self):
        """ Plot the new data and keep track of what's plotted for the ranges. """
        # plot the newly updated x and ys
        _no_nans = ~np.isnan(self.plot_data_ys) # avoid plotting nans
        if len(self.plot_data_ys[_no_nans])>1:
            # easier to start with an initial value
            self.plot(self.plot_data_xs[_no_nans], self.plot_data_ys[_no_nans])
            self.counter += 1

    def _remove_first_artificial_point(self):
        """ 
        First point is artificial since PlotWidget object won't plot 
        a single datapoint by itself.
        
        The check is we still have that entry there (`_remove_first`), 
        and if there are at least two real data points, the just remove 
        the artificial one.
        """
        if self._remove_first and len(self.plot_data_ys)>=3:
            self._remove_first = False
            self.plot_data_ys = self.plot_data_ys[1:]
            self.plot_data_xs = self.plot_data_xs[1:]

    def _replace_values(self, replace):
        """
        Given a dictionary, replace the entries with values "this" with 
        the value indicated by "with" in `self.plot_data_ys`.

        E.g., replace = {"this":[0, 500, 453], "with":[np.nan, 475, 450]}
        would mean to replace all 0s, 500s, and 453s in `self.plot_data_ys` 
        with np.nan, 475, and 450, respectively.
        """
        if replace is None:
            return
        
        if len(self.plot_data_ys)>=3:
            if len(replace["this"])!=len(replace["with"]):
                print("`replace` 'this' and 'with' keys do not have lists the same length.")

            for t, w in zip(replace["this"],replace["with"]):
                self.plot_data_ys[np.nonzero(self.plot_data_ys==t)] = w

    def add_plot_data(self, new_data_y, new_data_x=None, replace=None):
        """ Adds the new data to the array to be plotted. """

        # get new lists
        self.plot_data_ys = np.append(self.plot_data_ys, new_data_y)
        self.plot_data_xs = np.append(self.plot_data_xs, self.plot_data_xs[-1]+1) if new_data_x is None else np.append(self.plot_data_xs, new_data_x)

        self._remove_first_artificial_point()
        self._replace_values(replace)
        
        if len(self.plot_data_ys)>self.keep_entries:
            self.plot_data_ys = self.plot_data_ys[-self.keep_entries:]
            self.plot_data_xs = self.plot_data_xs[-self.keep_entries:]

        # deal with the plotting limits
        self._minmax_x = np.array([np.nanmin(self.plot_data_xs), np.nanmax(self.plot_data_xs)])
        if len(self._minmax_x)==2:
            self.graphPane.axes.set_xlim([np.nanmin(self._minmax_x[0]), np.nanmax(self._minmax_x[1])+1])

        if self.ylim is None:
            self._minmax_y = np.array([np.nanmin(self.plot_data_ys), np.nanmax(self.plot_data_ys)])
            if len(self._minmax_y)==2:
                self.graphPane.axes.set_ylim([np.nanmin(self._minmax_y[0])*0.95, np.nanmax(self._minmax_y[1])*1.05])
        self.graphPane.axes.set_ylim(self.ylim)

    def plot(self, x, y):
        """ Define so easy to plot new data and make sure the plot updates. """
        self._plot_ref.set_data(x, y)
        self.graphPane.fig.canvas.draw()

    def set_labels(self, xlabel="", ylabel="", title="", xlabel_kwargs=None, ylabel_kwargs=None, title_kwargs=None, tick_kwargs=None, offsetsize=1):
        """
        Method just to easily set the x, y-label and title.

        Parameters
        ----------

        xlabel, ylabel, title : `str`
            The strings relating to each label to be set.
            Defaults: "", "", ""

        xlabel_kwargs, ylabel_kwargs, title_kwargs, tick_kwargs : `dict` or `NoneType`
            Keywords to be passed to the title and axis labels.
            Defaults: None, None, None, None

        offsetsize : `int`, `float`, etc.
            The `offsetsize` handles the size of any text offsets (like 
            when values are too large then text appears like "1e9" so the
            tick values can be shown as 1,2, 3 etc.).
            Defaults: 1
        """
        xlabel_kwargs = {} if xlabel_kwargs is None else xlabel_kwargs
        ylabel_kwargs = {} if ylabel_kwargs is None else ylabel_kwargs
        title_kwargs = {} if title_kwargs is None else title_kwargs
        tick_kwargs = {} if tick_kwargs is None else tick_kwargs

        _title_kwargs = {"size":10} | title_kwargs

        self.graphPane.axes.set_title(title, **_title_kwargs)

        # Set label for both axes
        _xlabel_kwargs = {"size":9} | xlabel_kwargs
        _ylabel_kwargs = {"size":9} | ylabel_kwargs
        self.graphPane.axes.set_xlabel(xlabel, **_xlabel_kwargs)
        self.graphPane.axes.set_ylabel(ylabel, **_ylabel_kwargs)

        _tick_kwargs = {"axis":"both", "which":"major", "labelsize":5} | tick_kwargs
        self.graphPane.axes.tick_params(**_tick_kwargs)

        # this handles the exponent, if the data is in 1e10 then it is 
        # usually plotted in smaller numbers with 1e10 off to the side.
        # `get_offset_text` controls the "1e10"
        t = self.graphPane.axes.xaxis.get_offset_text()
        t.set_size(offsetsize)
        t = self.graphPane.axes.yaxis.get_offset_text()
        t.set_size(offsetsize)

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
        self.graphPane.axes.annotate(label, label_pos, **label_kwargs)

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

class MultiLightCurve(QWidget):
    """
    A line profile class to display multiple lines on one plot.

    Updated with the `add_plot_data()` method.

    Parameters
    ----------
    ids : `list[str]`
        Some type of IDs for each line to be plotted. Is assigned to 
        `names` if `names` is None.
        E.g., ["first", "second"].
        Default: ["first]

    colours : `list[str]`
        Must be a one-to-one match with `ids` or a list with a single 
        entry. This is a list of each line's colour.
        E.g, ["b", "k"].
        Default: ["b"]

    names : `list[str]` or `NoneType`
        If, for any reason, the line ID is not reader friendly, then 
        `names` will be used for legend text.
        E.g., ["1","2"].
        Default: None

    facecolour : `str`, `tuple[float]`
        This sets the colour inside the plot axes.
        Default: "w"
    """

    mpl_click_signal = QtCore.pyqtSignal()

    def __init__(self, ids=["first"], colours=["b"], names=None, facecolour="w", ylim=None, parent=None):
        """ 
        Set up the plot with the initial plot settings and connect some 
        `matplotlib` connections to methods that emit some `PyQt6` signals.
        """
        QWidget.__init__(self, parent)

        self.detw, self.deth = 400, 150
        self.aspect_ratio = self.detw / self.deth

        self.ylim = ylim

        self.graphPane = MPLCanvas(self)

        self.layoutMain = QVBoxLayout()

        self.layoutMain.setContentsMargins(0, 0, 0, 0)
        self.layoutMain.setSpacing(0)

        self._plot_ref = [None]*len(ids)

        self.plot_data_ys = [np.array([0]).astype(float)]*len(ids)
        self.plot_data_xs = [np.array([0]).astype(float)]*len(ids)
        self._remove_firsts = [True]*len(ids)

        self.layoutMain.addWidget(self.graphPane)

        colours = colours if len(colours)==len(ids) else colours*len(ids)
        names = ids if names is None else names
        self.plot_lines = []
        for p in range(len(names)):
            plot_refs = self.graphPane.axes.plot(self.plot_data_xs[p], self.plot_data_ys[p], colours[p], marker="o", ms=6, label=names[p])
            self.plot_lines.append(plot_refs[0])
            self._plot_ref[p] = plot_refs[0]
            
        self.graphPane.axes.legend(loc="upper left", fontsize=5, ncol=2)

        self.keep_entries = 60 # entries

        self.setLayout(self.layoutMain)

        self.graphPane.axes.set_facecolor(facecolour)
        
        self.counter = 1

        self.graphPane.mpl_connect("button_press_event", self.on_click)

    def on_click(self, event):
        """ 
        The matplotlib way needs a method to shout when it is interacted with. 

        Sends a signal if the plot is clicked on by the mouse.

        Other connections exist. [1]

        [1] https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.pyplot.connect.html
        """
        self.mpl_click_signal.emit()

    def manage_plotting_ranges(self):
        """ Plot the new data and keep track of what's plotted for the ranges. """
        # plot the newly updated x and ys
        _add_counter = True
        for p in range(len(self.plot_data_ys)):
            _no_nans = ~np.isnan(self.plot_data_ys[p]) #avoid plotting nans
            if len(self.plot_data_ys[p][_no_nans])>1:
                self.plot(self._plot_ref[p], self.plot_data_xs[p][_no_nans], self.plot_data_ys[p][_no_nans])
                self.counter = self.counter+1 if _add_counter else self.counter
                _add_counter = False

    def _remove_first_artificial_point(self):
        """ 
        First point is artificial since PlotWidget object won't plot 
        a single datapoint by itself.
        
        The check is we still have that entry there (`_remove_first`), 
        and if there are at least two real data points, the just remove 
        the artificial one.
        """
        for p in range(len(self.plot_data_ys)):
            if self._remove_firsts[p] and len(self.plot_data_ys[p])>=3:
                self._remove_firsts[p] = False
                self.plot_data_ys[p] = self.plot_data_ys[p][1:]
                self.plot_data_xs[p] = self.plot_data_xs[p][1:]

    def _replace_values(self, replace):
        """
        Given a dictionary, replace the entries with values "this" with 
        the value indicated by "with" in `self.plot_data_ys`.

        E.g., replace = {"this":[0, 500, 453], "with":[np.nan, 475, 450]}
        would mean to replace all 0s, 500s, and 453s in `self.plot_data_ys` 
        with np.nan, 475, and 450, respectively.
        """
        if replace is None:
            return
        
        for p in range(len(self.plot_data_ys)):
            if len(self.plot_data_ys[p])>=3:
                if len(replace["this"])!=len(replace["with"]):
                    print("`replace` 'this' and 'with' keys do not have lists the same length.")

                for t, w in zip(replace["this"],replace["with"]):
                    self.plot_data_ys[p][np.nonzero(self.plot_data_ys[p]==t)] = w

    def add_plot_data(self, new_data_ys, new_data_xs=None, replace=None):
        """ Adds the new data to the array to be plotted. """

        for p in range(len(self.plot_data_ys)):
            self.plot_data_ys[p] = np.append(self.plot_data_ys[p], new_data_ys[p])
            self.plot_data_xs[p] = np.append(self.plot_data_xs[p], self.plot_data_xs[p][-1]+1) if new_data_xs is None else np.append(self.plot_data_xs[p], new_data_xs)

        self._remove_first_artificial_point()
        self._replace_values(replace)
        
        for p in range(len(self.plot_data_ys)):
            if len(self.plot_data_ys[p])>self.keep_entries:
                self.plot_data_ys[p] = self.plot_data_ys[p][-self.keep_entries:]
                self.plot_data_xs[p] = self.plot_data_xs[p][-self.keep_entries:]

        # work out some good axes limits from all the lines being plotted
        _ymins, _ymaxs, _xmins, _xmaxs = [], [], [], []
        for p in range(len(self.plot_data_ys)):
            _ymins.append(np.nanmin(self.plot_data_ys[p]))
            _ymaxs.append(np.nanmax(self.plot_data_ys[p]))
            _xmins.append(np.nanmin(self.plot_data_xs[p]))
            _xmaxs.append(np.nanmax(self.plot_data_xs[p]))

        self.graphPane.axes.set_xlim([np.nanmin(_xmins), np.nanmax(_xmaxs)+1])

        if self.ylim is None:
            self.graphPane.axes.set_ylim([np.nanmin(_ymins)*0.95, np.nanmax(_ymaxs)*1.05])
        self.graphPane.axes.set_ylim(self.ylim)

    def plot(self, graph_widget_plot_ref, x, y):
        """ Define so easy to plot new data and make sure the plot updates. """
        graph_widget_plot_ref.set_data(x, y)
        self.graphPane.fig.canvas.draw()
    
    def set_labels(self, xlabel="", ylabel="", title="", xlabel_kwargs=None, ylabel_kwargs=None, title_kwargs=None, tick_kwargs=None, offsetsize=1):
        """
        Method just to easily set the x, y-label and title.

        Parameters
        ----------

        xlabel, ylabel, title : `str`
            The strings relating to each label to be set.
            Defaults: "", "", ""

        xlabel_kwargs, ylabel_kwargs, title_kwargs, tick_kwargs : `dict` or `NoneType`
            Keywords to be passed to the title and axis labels.
            Defaults: None, None, None, None

        offsetsize : `int`, `float`, etc.
            The `offsetsize` handles the size of any text offsets (like 
            when values are too large then text appears like "1e9" so the
            tick values can be shown as 1,2, 3 etc.).
            Defaults: 1
        """
        xlabel_kwargs = {} if xlabel_kwargs is None else xlabel_kwargs
        ylabel_kwargs = {} if ylabel_kwargs is None else ylabel_kwargs
        title_kwargs = {} if title_kwargs is None else title_kwargs
        tick_kwargs = {} if tick_kwargs is None else tick_kwargs

        _title_kwargs = {"size":10} | title_kwargs

        self.graphPane.axes.set_title(title, **_title_kwargs)

        # Set label for both axes
        _xlabel_kwargs = {"size":9} | xlabel_kwargs
        _ylabel_kwargs = {"size":9} | ylabel_kwargs
        self.graphPane.axes.set_xlabel(xlabel, **_xlabel_kwargs)
        self.graphPane.axes.set_ylabel(ylabel, **_ylabel_kwargs)

        _tick_kwargs = {"axis":"both", "which":"major", "labelsize":5} | tick_kwargs
        self.graphPane.axes.tick_params(**_tick_kwargs)
        self.graphPane.axes.tick_params(**_tick_kwargs)

        # this handles the exponent, if the data is in 1e10 then it is 
        # usually plotted in smaller numbers with 1e10 off to the side.
        # `get_offset_text` controls the "1e10"
        t = self.graphPane.axes.xaxis.get_offset_text()
        t.set_size(offsetsize)
        t = self.graphPane.axes.yaxis.get_offset_text()
        t.set_size(offsetsize)

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
        self.graphPane.axes.annotate(label, label_pos, **label_kwargs)

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

class LightCurveTwinX(LightCurve):
    """
    A line profile class.

    Updated with the `add_plot_data()` method.

    Parameters
    ----------
    colour : `str`, `tuple[float]`
        This is the colour of the line being plotted. It could actually 
        be anything a `matplotlib.pyplot` plot will accept as a colour.
        Default: "b"

    facecolour : `str`, `tuple[float]`
        This sets the colour inside the plot axes.
        Default: "w"
    """

    mpl_click_signal = QtCore.pyqtSignal()

    def __init__(self, colour="b", facecolour="w", ylim=None, colour_twin="r", ylim_twin=None, parent=None):
        """ 
        Set up the plot with the initial plot settings and connect some 
        `matplotlib` connections to methods that emit some `PyQt6` signals.
        """
        LightCurve.__init__(self, colour=colour, facecolour=facecolour, ylim=ylim, parent=parent)

        # now instantiate the second axis
        self.axes_twin = self.graphPane.axes.twinx() 

        self.colour_twin = colour_twin
        self.ylim_twin = ylim_twin

        self._plot_ref_twin = None
        self.plot_data_ys_twin = np.array([-1]).astype(float)
        self._remove_first_twin = True

        plot_refs = self.axes_twin.plot(self.plot_data_xs, self.plot_data_ys_twin, colour_twin, marker="+", ms=4)
        self._plot_ref_twin = plot_refs[0]

    def manage_plotting_ranges_twin(self):
        """ Plot the new data and keep track of what's plotted for the ranges. """
        # plot the newly updated x and ys
        self.manage_plotting_ranges()
        _no_nans = ~np.isnan(self.plot_data_ys_twin) # avoid plotting nans
        if len(self.plot_data_ys_twin[_no_nans])>1:
            # easier to start with an initial value
            self.plot_twin(self.plot_data_xs[_no_nans], self.plot_data_ys_twin[_no_nans])
            self.counter += 1

    def _remove_first_artificial_point_twin(self):
        """ 
        First point is artificial since PlotWidget object won't plot 
        a single datapoint by itself.
        """
        self._remove_first_artificial_point()
        if self._remove_first_twin and not self._remove_first:
            self._remove_first_twin = False
            self.plot_data_ys_twin = self.plot_data_ys_twin[1:]

    def _replace_values_twin(self, replace):
        """
        Given a dictionary, replace the entries with values "this" with 
        the value indicated by "with" in `self.plot_data_ys`.

        E.g., replace = {"this":[0, 500, 453], "with":[np.nan, 475, 450]}
        would mean to replace all 0s, 500s, and 453s in `self.plot_data_ys` 
        with np.nan, 475, and 450, respectively.
        """
        self._replace_values(replace)

        if replace is None:
            return
        
        if len(self.plot_data_ys_twin)>=3:
            if len(replace["this"])!=len(replace["with"]):
                print("`replace` 'this' and 'with' keys do not have lists the same length.")

            for t, w in zip(replace["this"],replace["with"]):
                self.plot_data_ys_twin[np.nonzero(self.plot_data_ys_twin==t)] = w

    def add_plot_data_twin(self, new_data_y, new_data_y_twin, new_data_x=None, replace=None):
        """ Adds the new data to the array to be plotted. """

        self.add_plot_data(new_data_y, new_data_x=new_data_x, replace=replace)

        # get new lists
        self.plot_data_ys_twin = np.append(self.plot_data_ys_twin, new_data_y_twin)
        
        self._remove_first_artificial_point_twin()
        self._replace_values_twin(replace)
        
        if len(self.plot_data_ys_twin)>self.keep_entries:
            self.plot_data_ys_twin = self.plot_data_ys_twin[-self.keep_entries:]

        # deal with the plotting limits
        if self.ylim_twin is None:
            self._minmax_y_twin = np.array([np.nanmin(self.plot_data_ys_twin), np.nanmax(self.plot_data_ys_twin)])
            if len(self._minmax_y_twin)==2:
                self.axes_twin.set_ylim([np.nanmin(self._minmax_y_twin[0])*0.95, np.nanmax(self._minmax_y_twin[1])*1.05])
        self.axes_twin.set_ylim(self.ylim_twin)

    def plot_twin(self, x, y_twin):
        """ Define so easy to plot new data and make sure the plot updates. """
        self._plot_ref_twin.set_data(x, y_twin)
        self.graphPane.fig.canvas.draw()

    def set_labels_twin(self, ylabel_twin="", ylabel_twin_kwargs=None, tick_twin_kwargs=None, offsetsize_twin=1, **kwargs):
        """
        Helps set the labels of the twin axes.

        Parameters
        ----------

        ylabel_twin : `str`
            The strings relating to each label to be set.
            Defaults: "", "", ""

        ylabel_twin_kwargs, tick_twin_kwargs : `dict` or `NoneType`
            Keywords to be passed to the title and axis labels.
            Defaults: None, None, None, None

        offsetsize_twin : `int`, `float`, etc.
            The `offsetsize` handles the size of any text offsets (like 
            when values are too large then text appears like "1e9" so the
            tick values can be shown as 1,2, 3 etc.).
            Defaults: 1

        **kwargs :
            Passed to `set_labels`.
        """
        self.set_labels(**kwargs)
        ylabel_kwargs = {} if ylabel_twin_kwargs is None else ylabel_twin_kwargs
        tick_kwargs = {} if tick_twin_kwargs is None else tick_twin_kwargs

        # Set label for twin axes
        _ylabel_kwargs = {"size":9, "color":self.colour_twin} | ylabel_kwargs
        self.axes_twin.set_ylabel(ylabel_twin, **_ylabel_kwargs)

        _tick_kwargs = {"axis":"both", "which":"major", "labelsize":5, "labelcolor":self.colour_twin} | tick_kwargs
        self.axes_twin.tick_params(**_tick_kwargs)

        # this handles the exponent, if the data is in 1e10 then it is 
        # usually plotted in smaller numbers with 1e10 off to the side.
        # `get_offset_text` controls the "1e10"
        t = self.axes_twin.yaxis.get_offset_text()
        t.set_size(offsetsize_twin)


class LightCurveExample(QWidget):
    """
    An individual window to display Timepix data read from a file.

    Parameters
    ----------
    data_file : `str` 
        The file to be passed to `FoGSE.readers.TimepixReader.TimepixReader()`.
        If given, takes priority over `reader` input.
        Default: None

    reader : instance of `FoGSE.readers.BaseReader.BaseReader()`
        The reader already given a file.
        Default: None

    Example
    -------
    import os
    DATAFILE = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/timepix/for_Kris/fake_data_for_parser/example_timepix_frame_writing.bin"

    def initiate_gui():
        app = QApplication([])
        R = TimepixReader(DATAFILE)

        f0 = LightCurveExample(reader=R)

        f0.show()
        app.exec()

    initiate_gui()
    """
    def __init__(self, data_file=None, reader=None, parent=None, name="Timepix"):

        pg.setConfigOption('background', (255,255,255, 0)) # needs to be first

        QWidget.__init__(self, parent)

        # decide how to read the data
        if data_file is not None:
            # probably the main way to use it
            self.reader = TimepixReader(data_file)
        elif reader is not None:
            # useful for testing and if multiple windows need to share the same file
            self.reader = reader
        else:
            print("How do I read the Timepix data?")

        self.lc = LightCurve()
        self.mlc = MultiLightCurve(ids=["first", "second"], colours=["b", "k"], names=["1","2"])
        self.lct = LightCurveTwinX()

        self.lc.set_labels(xlabel="", ylabel="Some Light Curve", title=" ")
        self.mlc.set_labels(xlabel="", ylabel="Multi Light Curve", title=" ")
        self.lct.set_labels_twin(xlabel="", ylabel="Some Light Curve", title=" ", ylabel_twin="Second Light Curve")

        self.reader.value_changed_collection.connect(self.update_plot)

        self.layoutMain = QVBoxLayout()
        self.layoutMain.setContentsMargins(0, 0, 0, 0)
        self.layoutMain.setSpacing(0)
        self.layoutMain.addWidget(self.lc)
        self.layoutMain.addWidget(self.mlc)
        self.layoutMain.addWidget(self.lct)
        self.setLayout(self.layoutMain)

        self.detw, self.deth = self.lc.detw, self.lc.deth*3
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
        
        new_mean_tot = self.reader.collection.get_mean_tot()
        
        # defined how to add/append onto the new data arrays
        self.lc.add_plot_data(new_mean_tot)
        self.mlc.add_plot_data([new_mean_tot, new_mean_tot-100])
        self.lct.add_plot_data_twin(new_mean_tot, new_mean_tot**2)

        # plot the newly updated x and ys
        self.lc.manage_plotting_ranges()
        self.mlc.manage_plotting_ranges()
        self.lct.manage_plotting_ranges_twin()

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
    import os
    DATAFILE = os.path.dirname(os.path.realpath(__file__)) + "/../../../fake_temperatures.txt"
    DATAFILE = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/timepix/for_Kris/fake_data_for_parser/example_timepix_frame.bin"
    DATAFILE = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/timepix/for_Kris/fake_data_for_parser/example_timepix_frame_writing.bin"

    def initiate_gui():
        app = QApplication([])

        R = TimepixReader(DATAFILE)

        f0 = LightCurveExample(reader=R)

        f0.show()
        app.exec()

    initiate_gui()