# ---------------------- Metadata ----------------------
#
# File name:  __init__.py
# Author:     Gianluca Bianco (biancogianluca9@gmail.com)
# Date:       2023-11-07
# Copyright:  (c) 2023 Gianluca Bianco under the MIT license.

from .CustomLogger import get_custom_logger
from .Generic import try_parse_float, try_parse_str, try_parse_int
from .Statistics import transpose_matrix, divide_by_bin_width, run_toy, array_to_TH1D
