import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QGridLayout, QGroupBox, QTabWidget, QTableWidget, QPushButton



# Prototyping popout-able containers detector data. 



class TestContainer(QWidget):   # like DetectorContainer
    def __init__(self, parent=None, name="PLACEHOLDER"):
        super().__init__()
        self.button = QPushButton("button")
        self.label = QLabel("label")
        self.label.hide()
        self.popped = False
        self.next = None

        self.box = QGroupBox("box", self)
        
        self.layout = QGridLayout()
        self.layout.addWidget(self.button, 1,1,1,1)
        self.layout.addWidget(self.label, 2,1,1,1)
        self.setLayout(self.layout)
        self.box.setLayout(self.layout)

        self.button.clicked.connect(self.onButtonPress)
    
    def onButtonPress(self, event):
        self.handlePopout()

    def handlePopout(self):
        self.popped = True
        self.next = TestPopout(self)
        self.next.show()

    def handlePopin(self, widget):
        print(self == widget) # this is True

        widget.layout.addWidget(widget.button, 1,1,1,1)
        widget.layout.addWidget(widget.label, 2,1,1,1)

        self.popped = False
        widget.label.hide()
        widget.setLayout(self.layout)
        widget.button.show()
        widget.box.setLayout(self.layout)
        print(self.box)
        print(self.label.parent())

    #  same as handlePopin(self, widget) since self==widget
    def handlePopin(self):
        self.layout.addWidget(self.button, 1,1,1,1)
        self.layout.addWidget(self.label, 2,1,1,1)

        self.popped = False
        self.label.hide()
        self.setLayout(self.layout)
        self.button.show()
        self.box.setLayout(self.layout)
        print(self.label.parent())



class TestPopout(QWidget):
    def __init__(self, add_widget):
        super().__init__()

        self.widget = add_widget
        self.widget_parent = self.widget.parent()
        self.label = QLabel("another label")
        self.tabs = QTabWidget()
        self.tabs.addTab(self.widget.button, "widget")
        self.tabs.addTab(self.widget.label, "label")

        self.layout = QGridLayout()
        self.layout.addWidget(self.tabs, 1,1,1,1)
        self.setLayout(self.layout)
    
    def closeEvent(self, event):
        # self.widget.handlePopin(self.widget)
        self.widget.handlePopin()
        event.accept()



class TestLayout(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.container1 = TestContainer(self, name="container1")
        self.container2 = TestContainer(self, name="container2")

        self.layout = QGridLayout()
        self.layout.addWidget(self.container1, 1,1,1,1)
        self.layout.addWidget(self.container2, 1,2,1,1)
        self.setLayout(self.layout)



class TestMain(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setCentralWidget(TestLayout())



app = QApplication([])
window = TestMain()
window.show()
sys.exit(app.exec())
