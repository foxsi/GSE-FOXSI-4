"""
Module is for common PyQt6 layout functions.
"""

def set_all_spacings(layout, s=0, grid=False):
        """ Default is to remove all margins"""
        """ 
        Uniformly stretches the cells of a A Pyqt6 layout object.
        
        Parameters
        ----------
        layout : `PyQt6.QtWidgets.QLayout`
                A Pyqt6 layout object.

        s : `int`
                Spacing for the layout.
                Default: 0

        grid : `bool`
                Is the layout a grid layout (rows and columns).
                Default: False
        Returns
        -------
        None
        """
        if grid:
            layout.setHorizontalSpacing(s)
            layout.setVerticalSpacing(s)
        else:
            layout.setSpacing(s)
        layout.setContentsMargins(s, s, s, s)
