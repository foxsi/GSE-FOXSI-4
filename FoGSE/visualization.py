import sys, typing, math
import numpy as np
from PyQt6 import QtCore
from PyQt6.QtGui import QPainter, QBrush, QPen, QColor
from PyQt6.QtCharts import QChart, QChartView, QLineSeries, QAbstractSeries
from PyQt6.QtWidgets import QWidget, QPushButton, QRadioButton, QLabel, QGridLayout, QVBoxLayout, QHBoxLayout
import pyqtgraph as pg

class AbstractVisualization(QWidget):
    
    def __init__(self):
        super().__init__()
        self.widgets = []               # store widgets that comprise the visualization
        self.layout = None              # store layout of widgets
        self.data = np.array([])        # store source data for display (may be singleton or whole spectra in dict etc.)
        
        pass

    def updateDisplay(self):
        pass

    def retrieveData(self, source):
        pass

class DetectorPanel(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.graphPane = pg.PlotWidget(self)
        self.spacing = 20
        # view = self.graphPane.addViewBox()
        # self.plot = pg.PlotItem()
        # view.addItem(self.plot)
        somex = np.linspace(-10,10,100)
        somey = np.cumsum(np.random.randn(100))
        self.graphPane.plot(
            somex, 
            somey,
            title="A chart",
            xlabel="x",
            ylabel="y"
        )

        self.modalPlotButton = QPushButton("Focus Plot", self)
        # self.modalPlotButton.setStyleSheet("font-size: 12px")
        self.modalImageButton = QPushButton("Strips/Pixels", self)
        self.modalParamsButton = QPushButton("Parameters", self)
        self.debugButton = QPushButton("DEBUG", self)
        self.debugButton.setStyleSheet("background-color: red")

        self.plotADCButton = QRadioButton("Plot in ADC bin", self)
        self.plotADCButton.setChecked(True)
        self.plotEnergyButton = QRadioButton("Plot in energy bin", self)
        self.restyleToMatchButton = QPushButton("Restyle all widgets", self)

        self.temperatureLabel = QLabel("Temperature (ºC):", self)
        self.voltageLabel = QLabel("Voltage (mV):", self)
        self.currentLabel = QLabel("Current (mA):", self)

        # organize layout
        self.layoutLeftTop = QVBoxLayout()
        self.layoutLeftTop.addWidget(
            self.modalPlotButton,
            alignment=QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignTop
        )
        self.layoutLeftTop.addWidget(
            self.modalImageButton,
            alignment=QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignTop
        )
        self.layoutLeftTop.addWidget(
            self.modalParamsButton,
            alignment=QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignTop
        )
        self.layoutLeftTop.addStretch(self.spacing)

        self.layoutLeftBottom = QVBoxLayout()
        self.layoutLeftBottom.addWidget(
            self.temperatureLabel,
            alignment=QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignTop
        )
        self.layoutLeftBottom.addWidget(
            self.voltageLabel,
            alignment=QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignTop
        )
        self.layoutLeftBottom.addWidget(
            self.currentLabel,
            alignment=QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignTop
        )
        self.layoutLeftBottom.addStretch(self.spacing)

        self.layoutRightTop = QVBoxLayout()
        self.layoutRightTop.addWidget(
            self.plotADCButton,
            alignment=QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop
        )
        self.layoutRightTop.addWidget(
            self.plotEnergyButton,
            alignment=QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop
        )
        self.layoutRightTop.addWidget(
            self.restyleToMatchButton,
            alignment=QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop
        )
        self.layoutRightTop.addStretch(self.spacing)

        self.layoutRightBottom = QVBoxLayout()
        self.layoutRightBottom.addStretch(self.spacing)
        self.layoutRightBottom.addWidget(
            self.debugButton,
            alignment=QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignBottom
        )

        self.layoutLeft = QVBoxLayout()
        self.layoutLeft.addLayout(self.layoutLeftTop)
        self.layoutLeft.addLayout(self.layoutLeftBottom)

        self.layoutRight = QVBoxLayout()
        self.layoutRight.addLayout(self.layoutRightTop)
        self.layoutRight.addLayout(self.layoutRightBottom)

        self.layoutMain = QHBoxLayout()
        self.layoutMain.addLayout(self.layoutLeft)
        self.layoutMain.addWidget(self.graphPane)
        self.layoutMain.addLayout(self.layoutRight)

        self.setLayout(self.layoutMain)
        
        # connect to callbacks
        self.modalPlotButton.clicked.connect(self.modalPlotButtonClicked)
        self.debugButton.clicked.connect(self.debugButtonClicked)
        self.plotADCButton.clicked.connect(self.plotADCButtonClicked)
        self.plotEnergyButton.clicked.connect(self.plotEnergyButtonClicked)

        # self.createWidgets()

    # def createWidgets(self):
    #     button = QPushButton("breakout plot", self)
    #     # button.move(100,100)

    def modalPlotButtonClicked(self, events):
        print("focus plot")

    def plotADCButtonClicked(self, events):
        print("plotting in ADC space")
    
    def plotEnergyButtonClicked(self, events):
        print("plotting in energy space")

    def debugButtonClicked(self, events):
        # print(self.children())
        for child in self.children():
            if isinstance(child, QWidget):
                print("widget size: ", "W: ", child.width(), "\tH: ", child.height())
        # for p, v in vars(self).items():
        #     print(p, ":", v)

class DetectorArrayDisplay(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        # self.H = 800
        # self.W = 1280
        self.H = parent.height() - 100
        self.W = parent.width() - 100

        self.setGeometry(10,10,self.W,self.H)

        # making hex geometry
        self.border = 0
        self.center = [0*self.x() + self.width()/2, self.y() + self.height()/2]
        # self.wradius = (self.center[0] - self.border)*2/3
        # self.hradius = (self.center[1] - self.border)*2/3

        # width of a panel within display
        self.panelWidth = 1/3*(self.width() - 2*self.border)
        self.panelHeight = 1/3*(self.height() - 2*self.border)
        # radius from self.center to center of rectangular pane
        self.wradius = self.panelWidth
        self.hradius = self.panelHeight
        self.hexagon = [self.center]
        for i in range(6):
            x = self.center[0] + self.wradius*math.cos(2*math.pi*i/6)
            y = self.center[1] + self.hradius*math.sin(2*math.pi*i/6)
            self.hexagon.append([x,y])

        print("semiwidth: ", self.panelWidth, ", semiheight: ", self.panelHeight)
        print("hexagon: ", self.hexagon)

        self.detectorPanels = [DetectorPanel(self)]
        for i in range(6):
            self.detectorPanels.append(DetectorPanel(self))

        # putting rectangles in hexagon
        # rects = [QtCore.QRect(
        #     self.center[0] - self.panelWidth/2, 
        #     self.center[1] - self.panelHeight/2,
        #     self.panelWidth,
        #     self.panelHeight
        #     )]

        xs = []
        ys = []
        widths = []
        heights = []
        rects = []
        for i in range(7):
            xs.append(self.hexagon[i][0] - self.panelWidth/2)
            ys.append(self.hexagon[i][1] - self.panelHeight/2)
            widths.append(self.panelWidth)
            heights.append(self.panelHeight)

            rects.append(QtCore.QRect(
                self.hexagon[i][0] - self.panelWidth/2,
                self.hexagon[i][1] - self.panelHeight/2,
                self.panelWidth,
                self.panelHeight
            ))

        

        grids = self.fitToGrid(rects, 20, 20, 1)
        print("grids: ", grids)

        intersections = self._rectsIntersect(grids[0], grids[1], grids[2], grids[3])
        print("grid intersections: ", intersections)

        intersectionsF = self._rectsIntersectF(xs, ys, widths, heights)
        print("original intersections: ", intersectionsF)

        # layouting
        self.layout = QGridLayout()
        for i in range(7):
            self.layout.addWidget(
                self.detectorPanels[i],
                grids[1][i], grids[0][i], grids[3][i], grids[2][i],
                # alignment=QtCore.Qt.AlignmentFlag.AlignCenter | QtCore.Qt.AlignmentFlag.AlignVCenter
            )
        self.setLayout(self.layout)
        # self.setFixedSize(self.layout.sizeHint())

        # self.detectorBoundingBoxes = rects



    # def paintEvent(self, event):
    #     painter = QPainter(self)
    #     painter.setPen(QPen(QColor(255,255,255), 2))
    #     painter.setBrush(QBrush(QColor(32,32,32)))
    #     for pane in self.detectorPanels:
    #         painter.drawRect(pane.rect())

    def fitToGrid(self, rects, nrow, ncol, gridpad):
        minx = np.Inf
        maxx = -np.Inf
        miny = np.Inf
        maxy = -np.Inf


        #  get corner coords for each  rect
        N = len(rects)
        xl = [rect.x() for rect in rects]
        yl = [rect.y() for rect in rects]
        xh = [rect.x() + rect.width() for rect in rects]
        yh = [rect.y() + rect.height() for rect in rects]

        # get available rows, cols for rects by removing the padding
        rows = nrow - 2*gridpad
        cols = ncol - 2*gridpad
        if rows <= 0 or cols <= 0:
            raise Exception("too much pad or too little rows/cols")
        
        # scale factor from source space to grid
        xscale = rows/(max(xl) - min(xl))
        yscale = cols/(max(yl) - min(yl))

        # scale all rects into grid space
        xli = [gridpad + xscale*(xl[i] - min(xl)) for i in range(N)]
        yli = [gridpad + yscale*(yl[i] - min(yl)) for i in range(N)]
        xhi = [gridpad + xscale*(xh[i] - min(xl)) for i in range(N)]
        yhi = [gridpad + yscale*(yh[i] - min(yl)) for i in range(N)]

        print("xli: ", xli)

        # scale widths/heights to grid space and round to grid
        widths = [round(xhi[i] - xli[i]) for i in range(N)]
        heights = [round(yhi[i] - yli[i]) for i in range(N)]
        # round root corner of grid-space rects to grid
        xs = [round(xli[i]) for i in range(N)]
        ys = [round(yli[i]) for i in range(N)]

        return (xs, ys, widths, heights)

    def _rectsIntersect(self, xs, ys, widths, heights):
        N = len(xs)
        rects = []
        for i in range(N):
            rects.append(QtCore.QRect(xs[i], ys[i], widths[i], heights[i]))

        indexIntersect = []
        for i in range(N):
            for j in range(N):
                if i != j:
                    indexIntersect.append(rects[i].intersects(rects[j]))
        
        return indexIntersect


    def _rectsIntersectF(self, xs, ys, widths, heights):
        N = len(xs)
        rects = []
        for i in range(N):
            rects.append(QtCore.QRectF(xs[i], ys[i], widths[i], heights[i]))

        indexIntersect = []
        for i in range(N):
            for j in range(N):
                if i != j:
                    indexIntersect.append(rects[i].intersects(rects[j]))
        
        return indexIntersect
    
    def _drawBoundingBoxes(self, rects):
        painter = QPainter(self)
        painter.setPen(QPen(QColor(255,255,255), 2))
        painter.setBrush(QBrush(QColor(32,32,32)))
        for rect in rects:
            painter.drawRect(rect)
        
        self.show()