import matplotlib
matplotlib.use('QtAgg')  # Use the Qt backend for Matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

class MPLCanvas(FigureCanvasQTAgg):
    """
    Allows a nice container for matplotlib.pyplot plots when added as 
    widgets using PyQt6.
    """
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)
