import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import pandas as pd
import time
import datetime
import math
import QuantLib as ql
from scipy.optimize import minimize

data = "SILVER"


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

if data == "OIL":
    data_label = "WTI Crude Oil"
    df = pd.read_csv(r'datasets/oil_new.csv', sep=";")
    df["Date"] = pd.to_datetime(df["Date"], format='%m/%d/%y')

    # Remove strikes from Dataframe
    fltr = np.arange(36, 84, 1)
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
elif data == "SILVER":
    data_label = "Silver"
    df = pd.read_csv(r'datasets/silver.csv', sep=";")
    df["Date"] = pd.to_datetime(df["Date"], format='%m/%d/%y')

    # Remove strikes from Dataframe
    fltr = np.arange(17, 35, 1)
    df = df[df['Strike'].isin(fltr)]
    df["IV"] = df["IV"] / 100

    current_time = pd.Timestamp(year=2021, month=8, day=31, hour=19)
    today = date_pd_to_ql(current_time)
    current_price = 25.
    ATM_price = 25.


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
