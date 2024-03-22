import matplotlib
matplotlib.use("QtAgg")#  # Use the Qt backend for Matplotlib
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.style as mplstyle
mplstyle.use('fast')



class MPLCanvas(FigureCanvasQTAgg):
    """
    Allows a nice container for matplotlib.pyplot plots when added as 
    widgets using PyQt6.
    """
    def __init__(self, parent=None, **kwargs):
        fig_kwargs = {"dpi":80} | kwargs 
        self.fig = Figure(**fig_kwargs)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)

class DrawPlot:
    def __init__(self, graphPane, artist, blit=False, **kwargs):
        self.graphPane = graphPane
        self.artist = artist
        self.blit = blit
        self.kwargs = kwargs

        self.save_background()
        self.update_canvas()

    def save_background(self):
        self.graphPane.axbackground = self.graphPane.fig.canvas.copy_from_bbox(self.graphPane.axes.bbox)

    def update_canvas(self):
        if not self.blit:
            self.graphPane.fig.canvas.draw()
            return
        
        self.graphPane.fig.canvas.restore_region(self.graphPane.axbackground)

        self.graphPane.axes.draw_artist(self.artist, **self.kwargs)

        self.graphPane.fig.canvas.blit(self.graphPane.axes.bbox)
     