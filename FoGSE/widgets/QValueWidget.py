"""
A widget to display a value and its status.
"""

import numpy as np
import re
import collections
from copy import copy

from PyQt6.QtWidgets import QWidget, QApplication, QSizePolicy,QVBoxLayout,QGridLayout, QLabel, QToolTip
from PyQt6.QtCore import QSize, QTimer
from PyQt6 import QtGui
import pyqtgraph as pg


class QValueWidget(QWidget):
    """
    A widget to be added to a GUI to display values and their status.

    The is a base class but can be used just to display a given value 
    and/or update one.

    Example
    -------
    class test(QWidget):
        \""" A test widget class to use QValueWidget. \"""
        def __init__(self, parent=None):
            \""" Initialise a grid on a widget and add different iterations of the QValueWidget widget. \"""
            QWidget.__init__(self,parent)

            # define layout
            l = QGridLayout()

            # create value widget and add it to the layout
            self.value0 = QValueWidget(name="This", value=5)
            l.addWidget(self.value0, 0, 0) # widget, -y, x

            # actually display the layout
            self.setLayout(l)

            # test the changing values
            self.timer = QTimer()
            self.timer.setInterval(1000) # fastest is every millisecond here
            self.timer.timeout.connect(self.cycle_values) # call self.update_plot_data every cycle
            self.timer.start()

        def cycle_values(self):
            \""" Add new data, update widget.\"""
            r = np.random.randint(20, size=1)
            self.value0.update_label(r[0])

    # for testing
    app = QApplication([])
    window = test()
    window.show()
    app.exec()
    """
    def __init__(self, name, value, condition=None, border_colour="grey", separator=" : ", tool_tip_values=None, name_plus="", loud=False, parent=None, **kwargs):
        """ 
        Constructs the widget and adds the latest plotted data to the widget.

        Widget colour:
            white : nominal
            red : outside condition range
            orange : unexpected value 
        
        Parameters
        ----------
        name : `str`
                The name to display for `value`.

        value : any
                The initial value to be displayed for the widget.

        condition : `dict` (or any)
                Dictionary of 2 entries describing the bounds of 
                `value` (keys:`low` and `high`, priority) describing the 
                condition for the nominal value. The dictionary 
                can instead contain information of two lists with the 
                acceptable and unacceptable states of `value` 
                (keys:`acceptable` and `unacceptable`)
                Default: None

        border_colour : `str`
                The border colour of the label. E.g., "blue", "rgba(255,255,9,100)",
                and "rgb(255,255,9)"
                Default: "grey"

        separator : `str`
                The character used to separate the value name and the 
                value in the label, this includes spaces between them.
                Default: " : "

        tool_tip_values : `dict`
                Dictionary where the key is the value name and the value 
                is a tuple of legnth 2. The first tuple entry is the value
                and the second is the relevant `QValueWidget` with the desired 
                conditioning condition if different from the main widget condition.
                Default: None

        name_plus : `str`
                String to be added after `name` in the label. E.g., could be used 
                to indicate box with "<sup>*</sup>" to show it is special but the 
                box can still just be edited with `name`.

        Methods
        -------
        update_label(self, new_value) : will update the label with the 
                new value showing and change the background in relation 
                to the conditions given.
        unexpected(self, **kwargs) : used to print out unexpected values
                and other items.

        Attributes
        ----------
        `name` : `str`, name for the value
        `condition` : `dict`, holds condition info for the value
        `layout` : `PyQt6.QtWidgets.QGridLayout`, to hold the widget
        `panel` : `PyQt6.QtWidgets.QVBoxLayout`, give more editing power
        `_value_label` : `PyQt6.QtWidgets.QLabel`, the label itself

        Notes
        -----
        For specific conditions, just inherit from this and redefine the 
        following methods with the specific checks and behaviour:
        * `check_condition_input(self, condition)`
        * `condition_colour(self, value):`
        """
        QWidget.__init__(self, parent, **kwargs)
        # self.setSizePolicy(
        #     QSizePolicy.Policy.MinimumExpanding,
        #     QSizePolicy.Policy.MinimumExpanding
        # )

        # make sure the name can be obtained anywhere
        self.name = name
        self.value = value
        self.condition = self.check_condition_input(condition)
        self.tool_tip_value_info = tool_tip_values
        self.name_plus = name_plus
        self.loud = loud

        # set main layout for widget
        self.layout = QGridLayout()

        self.bkg_layout = self.layout_bkg(main_layout=self.layout)

        # make the label for the value
        self._border_colour = border_colour
        self.separator = separator
        self.make_label(self.value)
        
        # style the label widgets
        self._style_label()

        # set the main layout for the widget
        self.setLayout(self.layout)

        self.layout.setContentsMargins(0, 0, 0, 0)
        self.bkg_layout.setContentsMargins(1, 1, 1, 1)
        self.setMinimumSize(2, 1)

        # QToolTip.setFont(QFont('SansSerif', 20))
        self._last_event_pos = None
        self.setup_tool_tip()
    
    def check_condition_input(self, condition):
        """ 
        Check that the condition given is workable. 
        
        ** Rewrite this method for different conditions and checks.**
        """
        return condition
        
    def layout_style(self, border_colour, background_colour):
        """ Define a global layout style. """
        # return "QLabel {"+f"border-width: 2px; border-style: outset; border-radius: 0px; border-color: {border_colour}; background-color: {background_colour};"+"} QToolTip {background-color: white;};"
        return f"border-width: 2px; border-style: outset; border-radius: 0px; border-color: {border_colour}; background-color: {background_colour};"

    def layout_bkg(self, main_layout, grid=False):
        """ Adds a background widget (panel) to a main layout so border, colours, etc. can be controlled. """
        # create panel widget
        self.panel = QWidget()

        # make the panel take up the main layout 
        main_layout.addWidget(self.panel)

        # now return a new, child layout that inherits from the panel widget
        if grid:
            return QGridLayout(self.panel)
        else:
            return QVBoxLayout(self.panel)

    def _data_style(self):
        """ Define the style for the label widgets. """
        return "border-width: 0px; color: black;"
    
    def _style_label(self):
        """ Assign the style for the label widget. """
        self._value_label.setStyleSheet(self._data_style())

    def update_border_colour(self, colour):
        """ Set the widget border colour. """
        self._border_colour = colour

    def make_label(self, value):
        """ Create the intial label. """
        self._value_label = QLabel(f"{self.name}{self.name_plus}{self.separator}{value}")
        # self._value_label.setWordWrap(True)

        # self.panel.setStyleSheet(self.layout_style(self._border_colour, 
        #                                             self.condition_colour(value)))
        self.panel.setStyleSheet(self.layout_style(self._border_colour, 
                                                    self.condition_colour(value)))

        self.bkg_layout.addWidget(self._value_label)

    def condition_colour(self, value):
        """ 
        Returns the widget colour for the value being displayed. 
        
        ** Rewrite this method for different conditions and checks.**
        """
        return "white"
        
    def update_label(self, new_value):
        """ Get the most current value and update the QLabel. """
        
        self._value_label.setText(f"{self.name}{self.name_plus}{self.separator}{new_value}")
        
        self.panel.setStyleSheet(self.layout_style(self._border_colour, 
                                                    self.condition_colour(new_value)))

        self._trigger_label_update()

    def setup_tool_tip(self):
        """ Sets up the main string used for the tool tip. """
        if self.tool_tip_value_info is None:
            return
        _tool_tip_str_list = []
        for key, val in self.tool_tip_value_info.items():
            if not issubclass(type(val), QValueWidget):
                colour = self.condition_colour(val)
            else:
                colour = val.condition_colour(val.value)
                val = val.value
            colour = "black" if colour in ["white", "rgb(255,255,255)", "rgba(255,255,255,255)"] else colour
            _tool_tip_str_list.append(f"<span style='color:{colour}'>{key}{self.separator}{val}</span>")

        self.full_string_tool_tip("\n".join(_tool_tip_str_list))

    def update_tool_tip(self, new_values):
        """ 
        A way to update the tool tip with new values. 
        
        This is a dictionary with the same keys as `self.tool_tip_value_info`
        but all values are just the display value. 

        The `self.tool_tip_value_info` dictionary gets checked to see if the 
        value for that key was set up with a display value, therefore, using 
        the same condition as the hosting widget or if the key was associated 
        with a different QValueWidget and so the colour should be taken from 
        that object.

        Must update all values, if only a subset then only the subset appears 
        in the tool tip.
        """
        if self.tool_tip_value_info is None:
            # could also `raise ValueError("It does not seem any tool tip information was provided during widget set-up.")`
            print("It does not seem any tool tip information was provided during widget set-up.")
            return 
        
        _tool_tip_str_list = []
        for key, val in self.tool_tip_value_info.items():
            if not issubclass(type(val), QValueWidget):
                colour = self.condition_colour(new_values[key])
            else:
                colour = val.condition_colour(new_values[key])
            colour = "black" if colour in ["white", "rgb(255,255,255)", "rgba(255,255,255,255)"] else colour
            _tool_tip_str_list.append(f"<span style='color:{colour}'>{key}{self.separator}{new_values[key]}</span>")

        # get mouse position in the coordinated of the widget (TL is (0,0), BR is (width,length))
        _mouse_pos  = self.mapFromGlobal(QtGui.QCursor.pos()) 

        # want to check is the local mouse position is still in the widget
        if (0<=_mouse_pos.x()<=self.geometry().width()) and (0<=_mouse_pos.y()<=self.geometry().height()):
            _s = "\n".join(_tool_tip_str_list) # new label
            QToolTip.setFont(QtGui.QFont("",15)) # make sure tooltip font size is set at least

            # remove the tooltip to force it to shut off if looking at it while it changes
            QToolTip.hideText()

            QToolTip.showText(self.mapToGlobal(_mouse_pos),f"<p style='white-space:pre'>{_s}</p>") # show new tool tip info
        else:
            self.full_string_tool_tip("\n".join(_tool_tip_str_list))

    def full_string_tool_tip(self, string):
        """ Ensures the full tool tip string doesn't wrap. """
        self._value_label.setStyleSheet("QLabel {border-width: 0px; border-style: outset; border-radius: 0px;} QToolTip {background-color: white; font-size:15pt};")
        self._value_label.setToolTip(f"<p style='white-space:pre'>{string}</p>")

    def sizeHint(self):
        """ Helps define the size of the widget. """
        return QSize(10,10)

    def smallest_dim(self, painter_obj):
        """ Might be useful to help define the size of the widget. """
        return painter_obj.device().width() if (painter_obj.device().width()<painter_obj.device().height()) else painter_obj.device().height()

    def _trigger_label_update(self):
        """ A dedicated method to call and update the widget. """
        self.update()

    def unexpected(self, **kwargs):
        """ Run if unexpected value is caught. """
        if self.loud:
            print(f"Unexpected entry for {self.name}.")
            for key, val in kwargs.items():
                print(f"{key}: {val}")

class QValueRangeWidget(QValueWidget):
    """
    A widget to be added to a GUI to display values and their status.

    To just check if the value being displayed is valid or not by being 
    in a single, simple range.

    Example
    -------
    class test(QWidget):
        \""" A test widget class to use QValueWidget. \"""
        def __init__(self, parent=None):
            \""" Initialise a grid on a widget and add different iterations of the QValueWidget widget. \"""
            QWidget.__init__(self,parent)

            # define layout
            l = QGridLayout()

            # create value widget and add it to the layout
            self.value = QValueRangeWidget(name="That", value=6, condition={"low":2,"high":15})
            l.addWidget(self.value, 0, 1) # widget, -y, x

            # actually display the layout
            self.setLayout(l)

            # test the changing values
            self.timer = QTimer()
            self.timer.setInterval(1000) # fastest is every millisecond here
            self.timer.timeout.connect(self.cycle_values) # call self.update_plot_data every cycle
            self.timer.start()

        def cycle_values(self):
            \""" Add new data, update widget.\"""
            r = np.random.randint(20, size=1)
            self.value.update_label(r[0])

    # for testing
    app = QApplication([])
    window = test()
    window.show()
    app.exec()
    """
    def __init__(self, name, value, condition=None, parent=None, **kwargs):
        """ 
        Constructs the widget and adds the latest plotted data to the widget.
        
        Parameters
        ----------
        name : `str`
                The name to display for `value`.

        value : any
                The initial value to be displayed for the widget.

        condition : `dict`
                Dictionary of 2 entries describing the bounds of 
                `value` (keys:`low` and `high`) describing the 
                condition for the nominal value. 
        """
        QValueWidget.__init__(self, name, value, condition=condition, parent=parent, **kwargs)
    
    def check_condition_input(self, condition):
        """ Check that the condition given is workable. """
        low = condition.get("low", None)
        high = condition.get("high", None)
        if (low is not None) and (high is not None):
            return condition
        raise ValueError("Please have `condition` be a `dict` with keys `low` and `high` with single number values.")

    def condition_colour(self, value):
        """ Returns the widget colour for the value being displayed. """
        try:
            if self.condition["low"]<=value<=self.condition["high"]:
                return "white"
            return "red"
        except Exception as e:
            self.unexpected(error=e, value=value)
            return "orange"


class QValueListWidget(QValueWidget):
    """
    A widget to be added to a GUI to display values and their status.

    To just check if the value being displayed is valid or not by being 
    in a list of acceptable states. If valid then goes with custom colour, 
    else red. If value is not in the acceptable or unacceptable list then
    the colour is orange.

    Example
    -------
    class test(QWidget):
        \""" A test widget class to use QValueWidget. \"""
        def __init__(self, parent=None):
            \""" Initialise a grid on a widget and add different iterations of the QValueWidget widget. \"""
            QWidget.__init__(self,parent)

            # define layout
            l = QGridLayout()

            # create value widget and add it to the layout
            self.value = QValueListWidget(name="Other", value=9, condition={"acceptable":[1,2,3,4,5,6,7,8,9,10],"unacceptable":[0,11,12,13,14,15,16]})
            l.addWidget(self.value, 0, 0) # widget, -y, x

            # actually display the layout
            self.setLayout(l)

            # test the changing values
            self.timer = QTimer()
            self.timer.setInterval(1000) # fastest is every millisecond here
            self.timer.timeout.connect(self.cycle_values) # call self.update_plot_data every cycle
            self.timer.start()

        def cycle_values(self):
            \""" Add new data, update widget.\"""
            r = np.random.randint(20, size=1)
            self.value.update_label(r[0])

    # for testing
    app = QApplication([])
    window = test()
    window.show()
    app.exec()
    """
    def __init__(self, name, value, condition=None, parent=None, **kwargs):
        """ 
        Constructs the widget and adds the latest plotted data to the widget.
        
        Parameters
        ----------
        name : `str`
                The name to display for `value`.

        value : any
                The initial value to be displayed for the widget.

        condition : `dict`
                The dictionary contains information of two lists with the 
                acceptable and unacceptable states of `value` 
                (keys:`acceptable` and `unacceptable`)
        """
        QValueWidget.__init__(self, name, value, condition=condition, parent=parent, **kwargs)
    
    def check_condition_input(self, condition):
        """ Check that the condition given is workable. """
        self.acceptable = condition.get("acceptable", None)
        self.unacceptable = condition.get("unacceptable", None)
        if (self.acceptable is not None) and (self.unacceptable is not None):
            return condition
        raise ValueError("Please have `condition` be a `dict` with keys `acceptable` and `unacceptable` with a list as values.")
    
    def condition_colour(self, value):
        """ Returns the widget colour for the value being displayed. """
        if value in self.acceptable:
            return "white"
        elif value in self.unacceptable:
            return "red"
        else:
            self.unexpected(value=value)
            return "orange"
        
class QValueMultiRangeWidget(QValueWidget):
    """
    A widget to be added to a GUI to display values and their status.

    To just check if the value being displayed is valid or not by being 
    in the ranges given. 

    Example
    -------
    class test(QWidget):
        \""" A test widget class to use QValueWidget. \"""
        def __init__(self, parent=None):
            \""" Initialise a grid on a widget and add different iterations of the QValueWidget widget. \"""
            QWidget.__init__(self,parent)

            # define layout
            l = QGridLayout()

            # create value widget and add it to the layout
            self.value1 = QValueDoubleRangeWidget(name="That", 
                                                  value=6, 
                                                  self.value = QValueMultiRangeWidget(name="Another", value=50, condition={"range1":[100,3_000,"green"],"range2":[-100,100,"white"],"other":"orange"})
            l.addWidget(self.value, 0, 0) # widget, -y, x

            # order not important: {"range1":[100,3_000,"green"],"range2":[-100,100,"white"],"other":"orange"}
            # equivalent to  {"range1":[100,3_000,"green"],"other":"orange","range2":[-100,100,"white"]}
            # and  {"range2":[-100,100,"white"],"range1":[100,3_000,"green"],"other":"orange"}

            # actually display the layout
            self.setLayout(l)

            # test the changing values
            self.timer = QTimer()
            self.timer.setInterval(1000) # fastest is every millisecond here
            self.timer.timeout.connect(self.cycle_values) # call self.update_plot_data every cycle
            self.timer.start()

        def cycle_values(self):
            \""" Add new data, update widget.\"""
            r = np.random.randint(-150,4_000, size=1)
            self.value1.update_label(r[0])

    # for testing
    app = QApplication([])
    window = test()
    window.show()
    app.exec()
    """
    def __init__(self, name, value, condition=None, colour=None, parent=None, **kwargs):
        """ 
        Constructs the widget and adds the latest plotted data to the widget.
        
        Parameters
        ----------
        name : `str`
                The name to display for `value`.

        value : any
                The initial value to be displayed for the widget.

        condition : `dict`
                Dictionary describing the bounds of `value` (keys:`rangeN`) 
                describing the conditions for the nominal value and the 
                colour associated to the range. The "other" key is used 
                when `value` is no in any range (default: "white"). Ranges 
                are inclusive and lower `N` values take priority. 
                E.g., `{"range1":[`low1`, `high1`, `col1`], 
                        ...,
                        "other":"red"}`
        """
        QValueWidget.__init__(self, name, value, condition=condition, parent=parent, **kwargs)
    
    def check_condition_input(self, condition):
        """ Check that the condition given is workable. """

        _conds = {}
        condition_all = copy(condition)

        # deal with the colour outside the range first
        other = condition_all.get("other", "white")
        condition_all.pop("other", None)
        
        error = condition_all.get("error", "purple")
        condition_all.pop("error", None)
        
        # get the ranges from the dictionary and put then in correct order
        for key, value in condition_all.items():
            _r = re.findall("^(range\d+)",key) # find the "rangeN"
            if (len(_r)!=1) or len(value)!=3:
                raise ValueError(f"Current key: {key}\nCurrent value: {value}\nPlease have `condition` be a `dict` with keys `rangeN` with list [low,high,colour]")
            _conds[int(re.findall("(\d+)$",_r[0])[0])] = value # get the N in range N

        _od_conds = collections.OrderedDict(sorted(_conds.items())) # order the ranges by N

        # order list of [[lo1,hi1,col1],[lo2,hi2,col2],...]
        _ordered_conds = list(_od_conds.values()) 
            
        # last is the default
        _ordered_conds.append(error) 
        _ordered_conds.append(other) 

        # order list of [[lo1,hi1,col1],[lo2,hi2,col2],..,col_default]
        return _ordered_conds
        

    def condition_colour(self, value):
        """ Returns the widget colour for the value being displayed. """
        try:
            for cond in self.condition[:-2]:
                if cond[0]<=value<=cond[1]:
                    return cond[2]
            return self.condition[-1]
        except Exception as e:
            self.unexpected(error=e, value=value)
            return self.condition[-2]
        

class QValueCheckWidget(QValueWidget):
    """
    A widget to be added to a GUI to display values and their status.

    To just check if the value being displayed is valid or not. If valid 
    then goes with custom colour, else red.

    Example
    -------
    class test(QWidget):
        \""" A test widget class to use QValueWidget. \"""
        def __init__(self, parent=None):
            \""" Initialise a grid on a widget and add different iterations of the QValueWidget widget. \"""
            QWidget.__init__(self,parent)

            # define layout
            l = QGridLayout()

            # create value widget and add it to the layout
            self.value = QValueCheckWidget(name="Other", value=9, condition={"acceptable":[(1,"white"), ("the","red")])
            l.addWidget(self.value, 0, 0) # widget, -y, x

            # actually display the layout
            self.setLayout(l)

            # test the changing values
            self.timer = QTimer()
            self.timer.setInterval(1000) # fastest is every millisecond here
            self.timer.timeout.connect(self.cycle_values) # call self.update_plot_data every cycle
            self.timer.start()

        def cycle_values(self):
            \""" Add new data, update widget.\"""
            r = np.random.randint(20, size=1)
            self.value.update_label(r[0])

    # for testing
    app = QApplication([])
    window = test()
    window.show()
    app.exec()
    """
    def __init__(self, name, value, condition=None, parent=None, **kwargs):
        """ 
        Constructs the widget and adds the latest plotted data to the widget.
        
        Parameters
        ----------
        name : `str`
                The name to display for `value`.

        value : any
                The initial value to be displayed for the widget.

        condition : `dict`
                The dictionary contains information of a list with the 
                acceptable states of `value` and color (keys:`acceptable`).
                E.g., {"acceptable":[(1,"white"), (2,"purple")]}
        """
        QValueWidget.__init__(self, name, value, condition=condition, parent=parent, **kwargs)
    
    def check_condition_input(self, condition):
        """ Check that the condition given is workable. """
        self.acceptable = condition.get("acceptable", None)
        if (self.acceptable is not None):
            return condition
        raise ValueError("Please have `condition` be a `dict` with key `acceptable` with a list of pair tuples as values.")
    
    def condition_colour(self, value):
        """ Returns the widget colour for the value being displayed. """
        for t in self.acceptable:
            if value==t[0]:
                return t[1]
        self.unexpected(value=value)
        return "red"

class QValueTimeWidget(QValueWidget):
    """
    A widget to be added to a GUI to display values and their status.

    To just check if the value being displayed has been changed or not.
    If it has then goes with custom colour, else red.

    Example
    -------
    class test(QWidget):
        \""" A test widget class to use QValueWidget. \"""
        def __init__(self, parent=None):
            \""" Initialise a grid on a widget and add different iterations of the QValueWidget widget. \"""
            QWidget.__init__(self,parent)

            # define layout
            l = QGridLayout()

            # create value widget and add it to the layout
            self.value = QValueCheckWidget(name="Another1", value=50, time=200, condition=[int, float, np.int64])
            l.addWidget(self.value, 0, 0) # widget, -y, x

            # actually display the layout
            self.setLayout(l)

            # test the changing values
            self.timer = QTimer()
            self.timer.setInterval(1000) # fastest is every millisecond here
            self.timer.timeout.connect(self.cycle_values) # call self.update_plot_data every cycle
            self.timer.start()

        def cycle_values(self):
            \""" Add new data, update widget.\"""
            r = np.random.randint(20, size=1)
            self.value.update_label(r[0])

    # for testing
    app = QApplication([])
    window = test()
    window.show()
    app.exec()
    """
    def __init__(self, name, value, time, condition=None, parent=None, **kwargs):
        """ 
        Constructs the widget and adds the latest plotted data to the widget.
        
        Parameters
        ----------
        name : `str`
                The name to display for `value`.

        value : any
                The initial value to be displayed for the widget.

        time : `int` or `float`
                The time after which the widget will turn red, in milliseconds, 
                if the value has not changed.

        condition : `dict`
                The dictionary contains information of a list with the 
                acceptable states of `value` and color (keys:`acceptable`).
                E.g., {"acceptable":[(1,"white"), (2,"purple")]}
        """
        self.timer_check = False
        self.update_counter, self.old_counter = 0, -1

        QValueWidget.__init__(self, name, value, condition=condition, parent=parent, **kwargs)
    
        # timer to check staleness of widget
        self.timer = QTimer()
        self.timer.setInterval(time) # fastest is every millisecond here
        self.timer.timeout.connect(self.update_label_check) # call self.update_plot_data every cycle
        self.timer.start()

    def check_condition_input(self, condition):
        """ 
        Check that the condition given is workable. 
        
        Should be a list of types. E.g., [int, float, np.int64,...]
        """
        return condition
    
    def update_label_check(self):
        """ Give the timer a function to check the counter. """
        self.timer_check = True
        if hasattr(self, "old_value"):
            self.update_label(self.old_value)
        self.timer_check = False
        self.old_counter = self.update_counter

    def condition_colour(self, value):
        """ Returns the widget colour for the value being displayed. """

        if self.timer_check and (self.update_counter==self.old_counter):
            return "red"
        
        self.old_value = value

        if type(value) not in self.condition:
            # check the value is of valid type first
            self.unexpected(value=value)
            return "orange"

        # to keep track that the label has been updated
        # avoids the counter from getting too big
        self.update_counter = (self.update_counter + 1)%1024 

        return "white"
    

class QValueChangeWidget(QValueWidget):
    """
    A widget to be added to a GUI to display values and their status.

    To just check if the value being displayed is changing or not. If changing
    then goes with white, else red.

    Example
    -------
    class test(QWidget):
        \""" A test widget class to use QValueWidget. \"""
        def __init__(self, parent=None):
            \""" Initialise a grid on a widget and add different iterations of the QValueWidget widget. \"""
            QWidget.__init__(self,parent)

            # define layout
            l = QGridLayout()

            # create value widget and add it to the layout
            self.value = QValueChangeWidget(name="Other", value=9, condition={"acceptable":[(1,"white"), ("the","red")])
            l.addWidget(self.value, 0, 0) # widget, -y, x

            # actually display the layout
            self.setLayout(l)

            # test the changing values
            self.timer = QTimer()
            self.timer.setInterval(1000) # fastest is every millisecond here
            self.timer.timeout.connect(self.cycle_values) # call self.update_plot_data every cycle
            self.timer.start()

        def cycle_values(self):
            \""" Add new data, update widget.\"""
            r = np.random.randint(20, size=1)
            self.value.update_label(r[0])

    # for testing
    app = QApplication([])
    window = test()
    window.show()
    app.exec()
    """
    def __init__(self, name, value, condition=None, parent=None, **kwargs):
        """ 
        Constructs the widget and adds the latest plotted data to the widget.
        
        Parameters
        ----------
        name : `str`
                The name to display for `value`.

        value : any
                The initial value to be displayed for the widget.

        condition : NoneType
                None
        """
        QValueWidget.__init__(self, name, value, condition=condition, parent=parent, **kwargs)
    
    def check_condition_input(self, condition):
        return
    
    def condition_colour(self, value):
        """ Returns the widget colour for the value being displayed. """
        if not hasattr(self, "_old_value"):
            self._old_value = value
            return "white"
        
        if value==self._old_value:
            return "red"
        self._old_value = value
        return "white"
        

class test(QWidget):
    """ A test widget class to use QValueWidget. """
    def __init__(self, parent=None):
        """ Initialise a grid on a widget and add different iterations of the QValueWidget widget. """
        QWidget.__init__(self,parent)

        # define layout
        l = QGridLayout()

        # create value widget and add it to the layout
        self.value0 = QValueWidget(name="This", value=5)
        l.addWidget(self.value0, 0, 0) # widget, -y, x
        self.value1 = QValueRangeWidget(name="That", value=6, condition={"low":2,"high":15})
        l.addWidget(self.value1, 0, 1) # widget, -y, x
        self.value2 = QValueListWidget(name="Other", value=9, condition={"acceptable":[1,2,3,4,5,6,7,8,9,10],"unacceptable":[0,11,12,13,14,15,16]})
        l.addWidget(self.value2, 1, 0) # widget, -y, x
        self.value3 = QValueMultiRangeWidget(name="Another", value=50, condition={"range1":[100,3_000,"green"],"range2":[-100,100,"white"],"other":"orange", "error":"red"})
        l.addWidget(self.value3, 1, 1) # widget, -y, x
        self.value4 = QValueCheckWidget(name="Another", value=50, condition={"acceptable":[(1,"white"), (2,"purple"), (3,"purple"), (8,"green")]})
        l.addWidget(self.value4, 1, 2) # widget, -y, x
        self.value5 = QValueTimeWidget(name="Another1", value=50, time=200, condition=[int, float, np.int64])
        l.addWidget(self.value5, 0, 2) # widget, -y, x
        self.value5 = QValueTimeWidget(name="Another1", value=50, time=800, condition=[int, float, np.int64])
        l.addWidget(self.value5, 2, 2) # widget, -y, x
        self.value6 = QValueRangeWidget(name="YetAnother", 
                                       value=6, 
                                       condition={"low":2,"high":15},
                                       tool_tip_values={"mean?":"N/A", "max?":"N/A"},
                                       name_plus="<sup>*</sup>")
        l.addWidget(self.value6, 2, 0) # widget, -y, x
        self.value7 = QValueChangeWidget(name="blah", value=6)
        l.addWidget(self.value7, 2, 1)
                                      
        
        # actually display the layout
        self.setLayout(l)

        # test the changing values
        self.timer = QTimer()
        self.timer.setInterval(1000) # fastest is every millisecond here
        self.timer.timeout.connect(self.cycle_values) # call self.update_plot_data every cycle
        self.timer.start()

    def cycle_values(self):
        """ Add new data, update widget."""
        r = np.random.randint(20, size=4)
        rr = np.random.randint(-150,4_000, size=1)
        self.value0.update_label(r[0])
        self.value1.update_label(r[1])
        self.value2.update_label(r[2])
        self.value3.update_label(rr[0])
        self.value4.update_label(r[3])
        self.value5.update_label(r[3])
        a = r[3] if r[3]<10 else 10
        self.value7.update_label(a)

        self.value6.update_label(r[0])
        self.value6.update_tool_tip({"mean?":r[2], "max?":r[1]})


if __name__=="__main__":
    # for testing
    app = QApplication([])
    window = test()
    window.show()
    app.exec()