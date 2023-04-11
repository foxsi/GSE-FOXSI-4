"""Test classes in `visualization` module."""

import logging # needs to go first

FILE_NAME = "test_visualization.py"
TEST_DIRECTORY = __file__[:-len(FILE_NAME)]
LOG_FILE = TEST_DIRECTORY+'test_visualization.log'
logging.basicConfig(filename=LOG_FILE, encoding='utf-8', level=logging.DEBUG) # used to check button-method match

import FoGSE.visualization as vis
from PyQt6 import QtWidgets, QtTest, QtCore
import numpy as np

TEST_FILE_1D = TEST_DIRECTORY+"test_data/test_file0.txt"
TEST_FILE_2D = TEST_DIRECTORY+"test_data/test_file3.txt"

def _initWindow(window, file):
    """Saves writing the QApplication and data file lines each time."""
    q = QtWidgets.QApplication([])
    w = window()
    w.dataFile = file
    # return q or widget doesn't stay open
    return q,w

def _openLogFileAndDeleteContents():
    """Read contents of LOG_FILE and then remove contents."""
    with open(LOG_FILE, "r+") as lf:
        lines = lf.readlines()
        # delete the text in LOG_FILE
        lf.seek(0)
        lf.truncate()
    return lines
_openLogFileAndDeleteContents() # log file isn't rewritten every time this is run and just grows and grows, want to start fresh

def _compareHalvesOfLog(buttonName, method):
    """
    Compare the two halves of the LOG_FILE when first half will be 
    from button press and second will be from running the method from 
    the button press directly.
    """
    lines = _openLogFileAndDeleteContents()
    cut = len(lines)//2 # 2 entries go from [:1] and [1:], 4 entries go from [:2] and [2:], etc.
    assert lines[:cut]==lines[cut:], f"uh oh! Button press `{buttonName}` doesn\'t give same behaviour as the method it is meant to call ({method})."

def _leftMouseClick(button):
    """Pass button to be pressed by the left mouse button."""
    QtTest.QTest.mouseClick(button, QtCore.Qt.MouseButton.LeftButton)

def _checkButtonAndMethod(buttonName, button, method, *args, **kwargs):
    """
    Press button then run method to which button should be attached 
    and compare outputs.
    """
    # click button
    _leftMouseClick(button)
    # run method the button *should* have run
    method(*args, **kwargs)
    # compare their outputs
    _compareHalvesOfLog(buttonName, method)


def test_DetectorPlotView():
    """
    Test base class for all detector panels.
    
    Aim: To check the buttons are mapped to the correct functions.
    """

    # check we can initialise
    q, w = _initWindow(vis.DetectorPlotView, TEST_FILE_1D)

    # check buttons can be pressed and don't cause error and give same log output as the methods they should be attached to
    #_checkButtonAndMethod(buttonName, button, method, *argsForMethod, **kwargsForMethod)
    _checkButtonAndMethod("modalPlotButton", w.modalFocusButton, w.modalFocusButtonClicked, 0)
    _checkButtonAndMethod("modalImageButton", w.modalImageButton, w.modalImageButtonClicked, 0)
    _checkButtonAndMethod("modalParamsButton", w.modalParamsButton, w.modalParamsButtonClicked, 0)
    _checkButtonAndMethod("plotADCButton", w.plotADCButton, w.plotADCButtonClicked, 0)
    _checkButtonAndMethod("plotEnergyButton", w.plotEnergyButton, w.plotEnergyButtonClicked, 0)
    _checkButtonAndMethod("plotStyleButton", w.plotStyleButton, w.plotStyleButtonClicked, 0)
    _checkButtonAndMethod("modalStartPlotDataButton", w.modalStartPlotDataButton, w.startPlotUpdate)
    _checkButtonAndMethod("modalStopPlotDataButton", w.modalStopPlotDataButton, w.stopPlotUpdate)


def test_DetectorPlotView1D():
    """
    Test base class for all 1D detector panels.
    
    Aim: To make sure (x,y) data can be plotted and is initially 
    (None, None).
    """

    # check we can initialise
    q, w = _initWindow(vis.DetectorPlotView1D, TEST_FILE_1D)

    # should return (None,None). I.e., empty X and Y coords
    xy = w.dataLine.getData()
    assert xy==(None, None), "No data should initially be in the base `DDetectorPlotView1D` class. Should have (x,y)=(None, None)."

def test_DetectorPlotViewTP():
    """
    Test class for all 1D detector panels showing a time profile.
    
    Aim: Run the `updatePlotData` method and check the plot was 
    updated as expected.
    """

    # check we can initialise
    q, w = _initWindow(vis.DetectorPlotViewTP, TEST_FILE_1D)

    # don't do any averaging over the read values, i.e. average every 1 entry
    w.averageEvery = 1

    # run method that updates the plot
    w.updatePlotData()

    # get the plotted x-y time profile data
    xy = w.dataLine.getData()

    # file contents, 0 and 48 are removed to ensure only full lines are read
    expectedOut = (np.array([ 1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 
                             21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 
                             41, 42, 43, 44, 45, 46, 47]), 
                   np.array([0.88362272, 0.38144622, 0.48121859, 0.90842814, 0.42707235, 0.39976809, 0.56749541, 
                             0.90863165, 0.65304751, 0.90004677, 0.37707034, 0.65115518, 0.91277799, 0.93946875, 
                             0.15574359, 0.14958422, 0.2540671 , 0.6946276 , 0.52728559, 0.0664187 , 0.76010147, 
                             0.33091427, 0.17412407, 0.34274228, 0.11767251, 0.66062807, 0.92743467, 0.28975906, 
                             0.5481932 , 0.87047187, 0.58350458, 0.33861692, 0.67974917, 0.57711151, 0.66190906,
                             0.65658346, 0.58056049, 0.20847921, 0.0051289 , 0.91222681, 0.20961444, 0.35287432, 
                             0.26730068, 0.65341421, 0.78410969, 0.34130229, 0.11820357]))
    
    # compare output
    assert (np.all(xy[0]==expectedOut[0]) and np.all(xy[0]==expectedOut[0])), "The x and y time profile data doesn\'t match the file data."

def test_DetectorPlotViewSP():
    """
    Test class for all 1D detector panels showing a spectrum.
    
    Aim: Run the `updatePlotData` method and check the plot was 
    updated as expected.
    """

    # check we can initialise
    q, w = _initWindow(vis.DetectorPlotViewSP, TEST_FILE_1D)

    # run method that updates the plot
    w.updatePlotData()

    # get the plotted x-y spectrum data
    xy = w.dataLine.getData()

    # file contents, data is binned between 1 and 50 for just now (will change)
    expectedOut = (np.array([ 1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 
                             21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 
                             41, 42, 43, 44, 45, 46, 47, 48, 49, 50]), 
                   np.array([0.88362272, 0.38144622, 0.48121859, 0.90842814, 0.42707235, 0.39976809, 0.56749541, 
                             0.90863165, 0.65304751, 0.90004677, 0.37707034, 0.65115518, 0.91277799, 0.93946875, 
                             0.15574359, 0.14958422, 0.2540671 , 0.6946276 , 0.52728559, 0.0664187 , 0.76010147, 
                             0.33091427, 0.17412407, 0.34274228, 0.11767251, 0.66062807, 0.92743467, 0.28975906, 
                             0.5481932 , 0.87047187, 0.58350458, 0.33861692, 0.67974917, 0.57711151, 0.66190906,
                             0.65658346, 0.58056049, 0.20847921, 0.0051289 , 0.91222681, 0.20961444, 0.35287432, 
                             0.26730068, 0.65341421, 0.78410969, 0.34130229, 0.11820357, 0.        , 0.        , 
                             0.        ]))
    
    # compare output
    assert (np.all(xy[0]==expectedOut[0]) and np.all(xy[0]==expectedOut[0])), "The x and y spectrum data doesn\'t match the file data."


def test_DetectorPlotView2D():
    """
    Test base class for all 2D detector panels.
    
    Aim: To make array is initialised properly for the image.
    """

    # check we can initialise
    q, w = _initWindow(vis.DetectorPlotView2D, TEST_FILE_2D)
    
    # check default, x and y for all r, g, b, and a cannels with values of rgb at 0 anda at 255
    carr = np.zeros((w.detH, w.detW, 4))
    carr[:,:,3] = 255 # rgb =0, a=255
    assert np.all(w.myArray==carr), "Initial 2D array default is not of shape (w.detH, w.detW, 4) with [:,:,3]==w.maxVal."

    # check we can change the height and width of the array being plotted (diff. detectors or something)
    height, width = 5, 5
    w.updateImageDimensions(height=height, width=width)
    carr = np.zeros((w.detH, w.detW, 4))
    carr[:,:,3] = w.maxVal
    assert ((w.detH==height) and (width==width)), "Changing image dimesnions via `DetectorPlotView2D.updateImageDimensions` has not worked."
    assert np.all(w.myArray==carr), "Changing image dimensions via `DetectorPlotView2D.updateImageDimensions` has not changed the array to be plotted."

    # make sure we can change the colour format, essentially remove the alpha channel
    w.updateImageColourFormat(colourFormat="rgb")
    assert np.all(w.myArray==np.zeros((height, width, 3))), "Changing image colour format via `DetectorPlotView2D.updateImageColourFormat` has not changed the array to be plotted."


def test_DetectorPlotViewIM():
    """
    Test class for all 2D detector panels showing an image.
    
    Aim: Run the `updatePlotData` method and check the plot was 
    updated as expected.
    """

    # check we can initialise
    q, w = _initWindow(vis.DetectorPlotViewIM, TEST_FILE_2D)

    # don't want to test against a 100x10 array
    w.updateImageDimensions(height=5, width=5)

    # run method that updates the plot
    w.updatePlotData()

    # details used to update the plot
    # [array, height, width, colourFormat]
    # file contents, data is binned between 1 and 50 for just now (will change)
    # array is [[[red,green,blue,alpha]]]
    expectedOut = [np.array([[[  0,   0, 191, 255],
                              [  0,   0, 255, 255],
                              [  0,   0, 127, 255],
                              [  0,   0, 255, 255],
                              [  0,   0,  63, 255]],

                             [[  0,   0,  63, 255],
                              [  0,   0, 127, 255],
                              [  0,   0,  63, 255],
                              [  0,   0, 255, 255],
                              [  0,   0,   0, 230]],

                             [[  0,   0,  63, 255],
                              [  0,   0, 127, 255],
                              [  0,   0, 127, 255],
                              [  0,   0,  63, 255],
                              [  0,   0,  63, 255]],

                             [[  0,   0,   0, 230],
                              [  0,   0, 191, 255],
                              [  0,   0, 255, 255],
                              [  0,   0,  63, 255],
                              [  0,   0,   0, 230]],

                             [[  0,   0, 127, 255],
                              [  0,   0, 127, 255],
                              [  0,   0,  63, 255],
                              [  0,   0, 191, 255],
                              [  0,   0, 127, 255]]], dtype=np.uint8), 
                   5, 5, "Format.Format_RGBA8888"]
    
    # check the 4 items that are used to create the qImage for each frame
    assert np.all(w.qImageDetails[0]==expectedOut[0]), "RGBA array data doesn\'t match the file data."
    assert ((w.qImageDetails[1]==expectedOut[1]) and (w.qImageDetails[2]==expectedOut[2])), f"Image array dimensions ({w.qImageDetails[1]}, {w.qImageDetails[2]}) do not match expected ({expectedOut[1]},{expectedOut[2]})."
    assert str(w.qImageDetails[3])==expectedOut[3], f"Colour format of image ({str(w.qImageDetails[3])}) doesn\'t match expected ({expectedOut[3]})"


if __name__=="__main__":
    # try to do a thorough test...

    # test detector panel base class
    test_DetectorPlotView()
    # test 1D detector panel base class
    test_DetectorPlotView1D()
    # test time profile detector panel class
    test_DetectorPlotViewTP()
    # test spectrum detector panel class
    test_DetectorPlotViewSP()
    # test 2D detector panel base class
    test_DetectorPlotView2D()
    # test image detector panel class
    test_DetectorPlotViewIM()