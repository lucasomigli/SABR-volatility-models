import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from initialize import *
from SABR import *

# Plot volatility Surface


def plot_vol_surface(vol_surface, plot_years=np.arange(0.1, (dates[-1] - today) / 365., 0.1), plot_strikes=strikes, funct='blackVol', title="", size=plot_size):
    if type(vol_surface) != list:
        surfaces = [vol_surface]
    else:
        surfaces = vol_surface

    fig = plt.figure(figsize=plot_size)
    ax = fig.add_subplot(projection='3d')
    ax.set_xlabel('Strikes')
    ax.set_ylabel('Maturities')
    ax.set_zlabel('Implied Volatility')
    ax.set_title(title)
    X, Y = np.meshgrid(plot_strikes, plot_years)

    for surface in surfaces:
        method_to_call = getattr(surface, funct)

        Z = np.array([method_to_call(float(y), float(x))
                      for xr, yr in zip(X, Y)
                      for x, y in zip(xr, yr)]
                     ).reshape(len(X), len(X[0]))

        surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, linewidth=0.3)


def plot_smile(date, smiles, title="", bounds=None, market=True, size=(15, 4)):

    market_vols = vols[dates.index(date)]

    fig, ax = plt.subplots(figsize=size)
    for smile in smiles:
        ax.plot(strikes, smile[0], label=smile[1])
    if market:
        ax.plot(strikes, market_vols, "rX", label="Actual")
        ax.plot([ATM_price], market_vols[strikes.tolist().index(
            ATM_price)], "o", label="ATM")

    if bounds:
        ax.set_xbound(bounds[0], bounds[1])
    if title == "":
        ax.set_title("Volatility Smile, {} on {}".format(date, data_label))
    else:
        ax.set_title(title)

    ax.set_xlabel("Strikes", size=12)
    ax.set_ylabel("Vols", size=12)
    legend = ax.legend(loc="upper right")

# Plot Volatility Smile Comparisons


def smiles_comparison(models=[], heston_models=[], local_models=[], points=(.2, .4, .6, .8, 1), black_volatility=False):
    for i in [round((len(dates)-1) * x) for x in points]:
        tenor = dates[i]
        l = []
        l.extend([([model.vol_surface.blackVol(tenor, s)
                    for s in strikes], model.label) for model in models])
        if black_volatility:
            l.extend([([black_var_surface.blackVol(tenor, s)
                     for s in strikes], "Market IV")])
        if len(heston_models) > 0:
            l.extend([([x.heston_vol_surface.blackVol(tenor, s)
                     for s in strikes], "Heston") for x in heston_models])
        if len(local_models) > 0:
            l.extend([([x.localVol(tenor, s)
                     for s in strikes], "Local Volatility") for x in local_models])
        plot_smile(
            tenor, l, title="Volatility Smile for options expiring on {}".format(tenor))
