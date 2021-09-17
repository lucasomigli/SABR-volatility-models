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


def density_IV(model, date):
    t = (date - today) / 365
    calls = []
    minStrike, maxStrike = (
        model.vol_surface.minStrike()*.5, model.vol_surface.maxStrike()*1.5)
    dK = (maxStrike-minStrike)/len(strikes)/2

    for K in np.arange(minStrike, maxStrike, dK):
        sigma = model.vol_surface.blackVol(t, K)
        price = ql.QuoteHandle(ql.SimpleQuote(current_price))
        option = ql.EuropeanOption(ql.PlainVanillaPayoff(
            ql.Option.Call, K), ql.EuropeanExercise(date))
        volatility = ql.BlackConstantVol(
            0, ql.TARGET(), sigma, ql.Actual365Fixed())
        process = ql.BlackScholesProcess(price, ql.YieldTermStructureHandle(riskFreeCurve),
                                         ql.BlackVolTermStructureHandle(volatility))
        engine = ql.AnalyticEuropeanEngine(
            process)
        option.setPricingEngine(engine)
        C = option.NPV()
        calls.append(C)

    xs = np.arange(minStrike, maxStrike, dK)
    dCdK = np.gradient(calls, dK)
    d2cdK2 = np.gradient(dCdK, dK)

    return xs, d2cdK2


def plot_densityIV(model):

    plt.figure(figsize=plot_size)
    fig, axs = plt.subplots(2, 4, figsize=plot_size)
    plt.subplots_adjust(left=None, bottom=None, right=1.5,
                        top=1.5, wspace=None, hspace=None)

    for i, d in enumerate([dates[round((len(dates)-1) * x)] for x in np.arange(0, .5, .5/4)]):
        axs[0, i].plot(density_IV(model, d)[0],
                       density_IV(model, d)[1])
        axs[0, i].set_title('tenor: {}'.format(d))
        axs[0, i].set(xlabel='Strikes', ylabel='IV')
    for i, d in enumerate([dates[round((len(dates)-1) * x)] for x in np.arange(.5, 1, .5/4)]):
        axs[1, i].plot(density_IV(model, d)[0],
                       density_IV(model, d)[1])
        axs[1, i].set_title('tenor: {}'.format(d))
        axs[1, i].set(xlabel='Strikes', ylabel='IV')
