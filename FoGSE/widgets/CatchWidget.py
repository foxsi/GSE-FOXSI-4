"""
A widget to show off CdTe data.
"""
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout

from FoGSE.readers.CatchReader import CatchReader
from FoGSE.widgets.layout_tools.stretch import unifrom_layout_stretch
from FoGSE.widgets.layout_tools.spacing import set_all_spacings

class CatchWidget(QWidget):
    """
    An individual window to display Power data read from a file.

    Parameters
    ----------
    data_file : `str` 
        The file to be passed to `FoGSE.readers.PowerReader.PowerReader()`.
        Default: None
    """
    def __init__(self, data_file=None, name="Catch", parent=None):

        QWidget.__init__(self, parent)
        catch_parser = self.get_catch_parsers()
        self.reader_catch = catch_parser(datafile=data_file)

        self._default_qvaluewidget_value = "<span>&#129418;</span>" #fox

        self.setWindowTitle(f"{name}")
        self.setStyleSheet("border-width: 2px; border-style: outset; border-radius: 10px; border-color: white; background-color: white;")
        self.detw, self.deth = 300, 150
        self.setGeometry(100,100,self.detw, self.deth)
        # self.setMinimumSize(self.detw, self.deth) # stops the panel from stretching and squeezing when changing times
        self.aspect_ratio = self.detw/self.deth

        self.panels = dict() # for all the background panels

        # need to groupd some of these for the layout
        first_layout = QGridLayout()
        self._first_layout = self.layout_bkg(main_layout=first_layout, 
                                             panel_name="first_panel", 
                                             style_sheet_string=self._layout_style("white", "white"), grid=True)
        title = QtWidgets.QLabel("Catch Log", alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        self._first_layout.addWidget(title, 0, 0) 

        self.scroll_box = ScrollBox()
        self._first_layout.addWidget(self.scroll_box, 1, 0, 10, 1) 

        unifrom_layout_stretch(self._first_layout, grid=True)
        unifrom_layout_stretch(first_layout, grid=True)
        
        set_all_spacings(self._first_layout)
        set_all_spacings(first_layout)
        # set_all_spacings(self._second_layout)

        self.reader_catch.value_changed_collection.connect(self.add_line)

        ## all widgets together
        global_layout = QGridLayout()
        set_all_spacings(global_layout)

        global_layout.addLayout(first_layout, 0, 0, 1, 1)#,
        # global_layout.addLayout(second_layout, 6, 0, 1, 9)#,

        unifrom_layout_stretch(global_layout, grid=True)
        # unifrom_layout_stretch(self._second_layout, grid=True)

        self._first_layout.setContentsMargins(0, 0, 0, 0)
        # self._second_layout.setContentsMargins(0, 0, 0, 0)
        # self._second_layout.setSpacing(6)

        # asic_layout.setSpacing(0)
        first_layout.setSpacing(0)
        # second_layout.setSpacing(0)
        # ping_layout.setSpacing(0)
        global_layout.setHorizontalSpacing(0)
        global_layout.setVerticalSpacing(0)
        global_layout.setContentsMargins(0, 0, 0, 0)

        # actually display the layout
        self.setLayout(global_layout)

    def get_catch_parsers(self):
        """ A way the class can be inherited from but use different parsers. """
        return CatchReader
    
    def add_line(self):
        """ Add a text line to the scroll box. """
        line = self.reader_catch.collection.get_last_line()
        if line is None:
            return
        self.scroll_box.add_line(line)

    def layout_bkg(self, main_layout, panel_name, style_sheet_string, grid=False):
        """ Adds a background widget (panel) to a main layout so border, colours, etc. can be controlled. """
        # create panel widget
        self.panels[panel_name] = QtWidgets.QWidget()

        # make the panel take up the main layout 
        main_layout.addWidget(self.panels[panel_name])

        # edit the main layout widget however you like
        self.panels[panel_name].setStyleSheet(style_sheet_string)

        # now return a new, child layout that inherits from the panel widget
        if grid:
            return QtWidgets.QGridLayout(self.panels[panel_name])
        else:
            return QtWidgets.QVBoxLayout(self.panels[panel_name])

    def _layout_style(self, border_colour, background_colour):
        """ Define a global layout style. """
        # return f"border-width: 2px; border-style: outset; border-radius: 10px; border-color: {border_colour}; background-color: {background_colour};"
        return f"border-width: 2px; border-style: outset; border-radius: 0px; border-color: {border_colour}; background-color: {background_colour};"
    
    def update_aspect(self, aspect_ratio):
        """ Update the lc aspect ratio (width/height). """
        self.aspect_ratio = aspect_ratio

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
        Runs when widget is close and ensure the `reader` attribute's 
        `QTimer` is stopped so it can be deleted properly. 
        """
        self.reader_catch.timer.stop()
        # self.deleteLater()


class ScrollBox(QWidget):
    """ Class to display lines of text in a scrollable window. """

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.main_layout = QVBoxLayout()   
        self.scroll = QtWidgets.QScrollArea()             # Scroll Area which contains the widgets, set as the centralWidget
        self.widget = QWidget()                 # Widget that contains the collection of Vertical Box
        self.vbox = QVBoxLayout()               # The Vertical Box that contains the Horizontal Boxes of  labels and buttons

        self.widget.setLayout(self.vbox)

        #Scroll Area Properties
        self.scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)

        # self.setCentralWidget(self.scroll)
        self.main_layout.addWidget(self.scroll)
        self.setLayout(self.main_layout)

        # for i in range(1,50):
        #     self.add_line("TextLabel")

    def add_line(self, line):
        """ Add a text line to the scroll box. """
        label = QtWidgets.QLabel(line)
        label.setWordWrap(True)
        self.vbox.addWidget(label)
        self.vbox.addWidget(QtWidgets.QLabel("----------"))
        

class CatchExample(QWidget):
    """
    Example of using the catch code.
    """
    def __init__(self, parent=None):
        """ Just put some examples of the `Image` class in a grid. """

        QWidget.__init__(self, parent)

        # decide how to read the data
        self.imsh0 = CatchWidget(data_file="")

        self.layoutMain = QGridLayout()
        self.layoutMain.setContentsMargins(0, 0, 0, 0)
        self.layoutMain.setSpacing(0)
        self.layoutMain.addWidget(self.imsh0, 0, 0)
        self.setLayout(self.layoutMain)

        self.detw, self.deth = self.imsh0.detw, self.imsh0.deth
        self.aspect_ratio = self.detw / self.deth

        self.setMinimumSize(self.detw, self.deth)
        self.resize(self.detw, self.deth)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000) # fastest is every millisecond here, with a value of 1
        self.timer.timeout.connect(self.add_labels) # call self.update_plot_data every cycle
        self.timer.start()

    def add_labels(self):
        """ Add different labels. """
        self.imsh0.scroll_box.add_line("sfgafdgasefhsdhshbshaes hsefbsbgsgbnsgnbsdbna")


if __name__=="__main__":
    app = QApplication([])
    datafile = "/Users/kris/Downloads/feb17_no_cmos/run22/17-2-2024_21-2-23/catch.log"
    
    # w.resize(1000,500)
    # w = CatchWidget(data_file=datafile)
    w = CatchExample()
    # w = QValueWidgetTest()
    w.show()
    app.exec()