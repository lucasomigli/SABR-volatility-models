import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import pandas as pd
import time
import datetime
import math
import QuantLib as ql
from scipy.optimize import minimize

from initialize import *
from SABR import *
from mixedSABR import *
from Heston import *


def compute_time():
    times_data = dict()

    # Local Volatility
    start = time.time()

    volMatrix = ql.Matrix(len(strikes), len(dates))

    for i in range(len(vols)):
        for j in range(len(vols[i])):
            volMatrix[j][i] = vols[i][j]

    black_var_surface = ql.BlackVarianceSurface(
        today, calendar, dates, strikes, volMatrix, day_count)
    black_var_surface.enableExtrapolation()

    black_var_surface.setInterpolation("bicubic")
    local_vol_handle = ql.BlackVolTermStructureHandle(black_var_surface)
    local_vol_surface = ql.LocalVolSurface(
        local_vol_handle, flat_ts, dividend_ts, spot_quote)

    end = time.time()
    times_data.update({"Local Volatility": end-start})

    # Heston
    start = time.time()
    m1_params, m2_params = ((0.5, 0.5, 1.25, 0.3, 0.00),
                            (0.01, 0.5, 0.5, 0.1, 0.03))
    hestonModelSurface(m1_params)
    hestonModelSurface(m2_params)
    end = time.time()
    times_data.update({"Heston": (end-start)/2})

    # SABR
    start = time.time()
    SABRVolatilitySurface()
    end = time.time()
    times_data.update({"SABR": end-start})

    # Shifted SABR
    start = time.time()
    SABRVolatilitySurface(strks=strikes, beta=1, shift=shft)
    end = time.time()
    times_data.update({"Shifted SABR": end-start})

    # Free Boundary SABR
    start = time.time()
    SABRVolatilitySurface(
        beta=.5, shift=0, method="floch-kennedy", strks=strikes)
    end = time.time()
    times_data.update({"Free Boundary SABR": end-start})

    # Mixture SABR
    start = time.time()
    MixtureSABRVolatilitySurface(dates=dates)
    end = time.time()
    times_data.update({"Mixture SABR": end-start})

    return times_data


compute_time()
