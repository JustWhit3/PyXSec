# ---------------------- Metadata ----------------------
#
# File name:  Statistics.py
# Author:     Gianluca Bianco (biancogianluca9@gmail.com)
# Date:       2023-11-08
# Copyright:  (c) 2023 Gianluca Bianco under the MIT license.

# Data science modules
from ROOT import TH2


def quick_clone(obj, type):
    """
    Clone the object if it is not None, otherwise return None.

    Parameters:
        obj (object): The object to clone.
        type (type): The type of object to return.

    Returns:
        object: The cloned object or None if obj is None.
    """

    return obj if obj is None else type(obj.Clone())


def transpose_matrix(h2):
    """
    Transpose a matrix represented as a ROOT.TH2.

    Parameters:
        h2 (ROOT.TH2): The bidimensional histogram to transpose.
    """

    hTemp = quick_clone(h2, TH2)
    hTemp.SetDirectory(0)
    h2.GetXaxis().SetTitle(h2.GetYaxis().GetTitle())
    h2.GetYaxis().SetTitle(h2.GetXaxis().GetTitle())
    h2.Transpose(hTemp)
