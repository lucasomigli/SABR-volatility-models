import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import pandas as pd
import time
import datetime
import math
import QuantLib as ql
from scipy.optimize import minimize

data = "OIL"


def date_pd_to_ql(date):
    date = pd.to_datetime(date)
    day = date.day
    month = date.month
    year = date.year

    return ql.Date(day, month, year)


current_time = current_price = ATM_price = None

df = pd.DataFrame()
data_label = None
eonia_rates = pd.read_csv(r'datasets/eonia.csv', sep=";")

if data == "SPX":
    data_label = "SP500"

    df = pd.read_csv(r'datasets/spx_SABR.csv')
    df['Date'] = pd.to_datetime(df['Date'], format='%y%m%d')

    # Remove strikes from Dataframe
    fltr = np.arange(3100., 4600., 100)
    df = df[df['Strike'].isin(fltr)]

    current_time = pd.Timestamp(year=2021, month=8, day=3, hour=12)
    today = date_pd_to_ql(current_time)
    current_price = 4300.
    ATM_price = 4300.

elif data == "NASDAQ":
    data_label = "Nasdaq100"
    df = pd.read_csv(r'datasets/NASDAQ.csv', sep=";")
    df["Date"] = pd.to_datetime(df["Date"], format='%d/%m/%Y')

    # Remove strikes from Dataframe
    fltr = np.arange(11000., 18000., 200)
    df = df[df['Strike'].isin(fltr)]
    df["IV"] = df["IV"] / 100

    current_time = pd.Timestamp(year=2021, month=8, day=30, hour=19)
    today = date_pd_to_ql(current_time)
    current_price = 15605.
    ATM_price = 15600.

elif data == "OIL":
    data_label = "WTI Crude Oil"
    df = pd.read_csv(r'datasets/oil.csv', sep=";")
    df["Date"] = pd.to_datetime(df["Date"], format='%m/%d/%y')

    # Remove strikes from Dataframe
    fltr = [41, 45, 47, 48, 50, 52, 54, 55, 60, 62, 64, 66, 70, 72, 75, 80]
    df = df[df['Strike'].isin(fltr)]
    df["IV"] = df["IV"] / 100

    current_time = pd.Timestamp(year=2021, month=8, day=30, hour=19)
    today = date_pd_to_ql(current_time)
    current_price = 67.61
    ATM_price = 66.

elif data == "GOLD":
    data_label = "Gold"
    df = pd.read_csv(r'datasets/gold.csv', sep=";")
    df["Date"] = pd.to_datetime(df["Date"], format='%m/%d/%y')

    # Remove strikes from Dataframe
    fltr = np.arange(1550., 2250., 50)
    df = df[df['Strike'].isin(fltr)]
    df["IV"] = df["IV"] / 100

    current_time = pd.Timestamp(year=2021, month=8, day=31, hour=19)
    today = date_pd_to_ql(current_time)
    current_price = 1820.
    ATM_price = 1800.

elif data == "COFFEE":
    data_label = "Coffee"
    df = pd.read_csv(r'datasets/coffee.csv', sep=";")
    df["Date"] = pd.to_datetime(df["Date"], format='%m/%d/%y')

    # Remove strikes from Dataframe
    fltr = np.arange(100., 300., 10)
    df = df[df['Strike'].isin(fltr)]
    df["IV"] = df["IV"] / 100

    current_time = pd.Timestamp(year=2021, month=8, day=31, hour=19)
    today = date_pd_to_ql(current_time)
    current_price = 200.
    ATM_price = 200.


maturities = df["Date"].unique()
strikes = df["Strike"].unique()

ql.Settings.instance().evaluationDate = today
calendar = ql.NullCalendar()
day_count = ql.Actual365Fixed()

spot_quote = ql.QuoteHandle(ql.SimpleQuote(current_price))
rate = ql.SimpleQuote(-0.00482)
riskFreeCurve = ql.FlatForward(
    today, ql.QuoteHandle(rate), ql.Actual365Fixed())
flat_ts = ql.YieldTermStructureHandle(riskFreeCurve)
dividend_ts = ql.YieldTermStructureHandle(riskFreeCurve)

vols = [np.array(df[df["Date"] == maturities[m]]["IV"])
        for m in range(len(maturities))]

plot_size = (12, 5)

dates = [date_pd_to_ql(d) for d in maturities]
