"""
Module is for common PyQt6 layout functions.
"""

def unifrom_layout_stretch(layout):
    """ 
    Uniformly stretches the cells of a A Pyqt6 layout object.
    
    Parameters
    ----------
    layout : `PyQt6.QtWidgets.QLayout`
            A Pyqt6 layout object.

    Returns
    -------
    None
    """
    # make sure all cell sizes in the grid expand in proportion
    for col in range(layout.columnCount()):
            layout.setColumnStretch(col, 1)
    for row in range(layout.rowCount()):
            layout.setRowStretch(row, 1)
