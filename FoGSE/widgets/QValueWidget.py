"""
A widget to display a value and its status.
"""

import numpy as np
from PyQt6.QtWidgets import QWidget, QApplication, QSizePolicy,QVBoxLayout,QGridLayout, QLabel
from PyQt6.QtCore import QSize, QTimer


class QValueWidget(QWidget):
    """
    A widget to be added to a GUI to display values and their status.

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
            self.value0 = QValueWidget(name="This", value=5, condition={"low":2,"high":15})
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
    def __init__(self, name, value, condition=None, parent=None, **kwargs):
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
        QWidget.__init__(self,parent, **kwargs)
        self.setSizePolicy(
            QSizePolicy.Policy.MinimumExpanding,
            QSizePolicy.Policy.MinimumExpanding
        )

        # make sure the name can be obtained anywhere
        self.name = name
        self.condition = self.check_condition_input(condition)

        # set main layout for widget
        self.layout = QGridLayout()

        self.bkg_layout = self.layout_bkg(main_layout=self.layout)

        # make the label for the value
        self.make_label(value)
        
        # style the label widgets
        self._style_label()

        # set the main layout for the widget
        self.setLayout(self.layout)

    def check_condition_input(self, condition):
        """ 
        Check that the condition given is workable. 
        
        ** Rewrite this method for different conditions and checks.**
        """
        return condition
        
    def layout_style(self, border_colour, background_colour):
        """ Define a global layout style. """
        return f"border-width: 2px; border-style: outset; border-radius: 10px; border-color: {border_colour}; background-color: {background_colour};"

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

    def make_label(self, value):
        """ Create the intial label. """
        self._value_label = QLabel(f"{self.name} : {value}")

        self.panel.setStyleSheet(self.layout_style("grey", 
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
        
        self._value_label.setText(f"{self.name} : {new_value}")
        
        self.panel.setStyleSheet(self.layout_style("grey", 
                                                    self.condition_colour(new_value)))

        self._trigger_label_update()

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
        print(f"Unexpected entry for {self.name}.")
        for key, val in kwargs.items():
            print(f"{key}: {val}")

class QValueRangeWidget(QValueWidget):
    """
    A widget to be added to a GUI to display values and their status.

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
            self.value1 = QValueRangeWidget(name="That", value=6, condition={"low":2,"high":15})
            l.addWidget(self.value1, 0, 1) # widget, -y, x

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
            self.value1.update_label(r[0])

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
            self.value2 = QValueListWidget(name="Other", value=9, condition={"acceptable":[1,2,3,4,5,6,7,8,9,10],"unacceptable":[0,11,12,13,14,15,16]})
            l.addWidget(self.value2, 1, 0) # widget, -y, x

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
            self.value2.update_label(r[0])

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
                The dictionary 
                can instead contain information of two lists with the 
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


class test(QWidget):
    """ A test widget class to use QValueWidget. """
    def __init__(self, parent=None):
        """ Initialise a grid on a widget and add different iterations of the QValueWidget widget. """
        QWidget.__init__(self,parent)

        # define layout
        l = QGridLayout()

        # create value widget and add it to the layout
        self.value0 = QValueWidget(name="This", value=5, condition={"low":2,"high":15})
        l.addWidget(self.value0, 0, 0) # widget, -y, x
        self.value1 = QValueRangeWidget(name="That", value=6, condition={"low":2,"high":15})
        l.addWidget(self.value1, 0, 1) # widget, -y, x
        self.value2 = QValueListWidget(name="Other", value=9, condition={"acceptable":[1,2,3,4,5,6,7,8,9,10],"unacceptable":[0,11,12,13,14,15,16]})
        l.addWidget(self.value2, 1, 0) # widget, -y, x

        # actually display the layout
        self.setLayout(l)

        # test the changing values
        self.timer = QTimer()
        self.timer.setInterval(1000) # fastest is every millisecond here
        self.timer.timeout.connect(self.cycle_values) # call self.update_plot_data every cycle
        self.timer.start()

    def cycle_values(self):
        """ Add new data, update widget."""
        r = np.random.randint(20, size=3)
        self.value0.update_label(r[0])
        self.value1.update_label(r[1])
        self.value2.update_label(r[2])


if __name__=="__main__":
    # for testing
    app = QApplication([])
    window = test()
    window.show()
    app.exec()