"""
Module is for common PyQt6 layout functions.
"""

def unifrom_layout_stretch(layout, grid=False):
    """ 
    Uniformly stretches the cells of a A Pyqt6 layout object.
    
    Parameters
    ----------
    layout : `PyQt6.QtWidgets.QLayout`
            A Pyqt6 layout object.

    grid : `bool`
            Is the layout a grid layout (rows and columns).
            Default: False
    Returns
    -------
    None
    """
    # make sure all cell sizes in the grid expand in proportion
    if grid:
        for col in range(layout.columnCount()):
                layout.setColumnStretch(col, 1)
        for row in range(layout.rowCount()):
                layout.setRowStretch(row, 1)
    else:
        for w in range(layout.count()):
            layout.setStretch(w, 1)
        layout.addStretch()
