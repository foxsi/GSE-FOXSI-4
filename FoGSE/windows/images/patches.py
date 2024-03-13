from matplotlib.patches import Circle

def circle_patch(**kwargs):
    """ 
    Get a circle patch for arc-distance contours in images.
    
    Parameters
    ----------
    radius : `int`, `float`, etc.
            The matrix representing an image.

    Returns
    -------
    `matplotlib.patches.Circle` : 
            A circle patch.
    """
    patch_kwargs = {"xy":(0, 0), "radius":1, "facecolor":"none", "edgecolor":"b"} | kwargs
    return Circle(**patch_kwargs)
