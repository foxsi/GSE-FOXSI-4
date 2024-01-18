import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import rotate

def rotate_matrix(matrix, angle):
    """ 
    Rotates a matrix by a given angle.
    
    Parameters
    ----------
    matrix : `numpy.ndarray`
            The matrix representing an image.

    angle : `int`, `float`
            In degrees, the angle to rotate clockwise (+ve is clockwise, 
            and -ve is anti-clockwise).

    Returns
    -------
    `numpy.ndarray` : 
            The newly rotated image where the number of pixels has been 
            increased to accomodate the rotation
    """
    return rotate(matrix, angle=angle)

if __name__=="__main__":
    x = np.random.randint(1, 256, size=[100, 100, 3])/256
    rotated = rotate(x, angle=45)
    rotated1 = rotate(x, angle=10)

    fig, axs = plt.subplots(1,3)
    axs[0].imshow(x)
    axs[1].imshow(rotated1)
    axs[2].imshow(rotated)
    plt.show()