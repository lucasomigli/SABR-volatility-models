from initialize import *
from SABR import *
from plotting import *


class hestonModelSurface:
    def __init__(self, params, label=""):
        (self.v0, self.kappa, self.theta, self.sigma, self.rho) = params
        self.label = label
        self.strks, self.marketValue, self.modelValue, self.relativeError = ([], [], [
        ], [])

        self.initialize()

    def initialize(self):
        process = ql.HestonProcess(flat_ts, dividend_ts,
                                   ql.QuoteHandle(
                                       ql.SimpleQuote(current_price)),
                                   self.v0, self.kappa, self.theta, self.sigma, self.rho)
        self.hestonModel = ql.HestonModel(process)
        self.engine = ql.AnalyticHestonEngine(self.hestonModel)
        self.errors = []

        self.heston_helpers = []
        black_var_surface.setInterpolation("bicubic")
        one_year_idx = -1
        date = dates[one_year_idx]

        for j, s in enumerate(strikes):
            t = (date - today)
            p = ql.Period(t, ql.Days)
            sigma = vols[one_year_idx][j]

            helper = ql.HestonModelHelper(p, calendar, current_price, s,
                                          ql.QuoteHandle(
                                              ql.SimpleQuote(sigma)),
                                          flat_ts,
                                          dividend_ts)
            helper.setPricingEngine(self.engine)
            self.heston_helpers.append(helper)

        lm = ql.LevenbergMarquardt(1e-8, 1e-8, 1e-8)
        self.hestonModel.calibrate(self.heston_helpers, lm,
                                   ql.EndCriteria(500, 300, 1.0e-8, 1.0e-8, 1.0e-8))
        self.v0, self.kappa, self.theta, self.sigma, self.rho = self.hestonModel.params()

        self.set_surface()
        self.compute_errors()

    def set_surface(self):
        # Boilerplate to get to the Vol Surface object
        heston_handle = ql.HestonModelHandle(self.hestonModel)
        self.heston_vol_surface = ql.HestonBlackVolSurface(heston_handle)
        self.heston_vol_surface.enableExtrapolation()

        # compute errors
        for j in range(len(dates)):
            heston_vols = [self.heston_vol_surface.blackVol(
                dates[j], s) for s in strikes]
            error = ((heston_vols - np.array(vols[i]))**2).mean() ** .5
            self.errors.append(error)

    def compute_errors(self):
        # Statistical analysis on the Heston model and plotting

        self.avgError = 0
        for i, opt in enumerate(self.heston_helpers):
            err = (opt.modelValue()/opt.marketValue() - 1.0)
            self.strks.append(strikes[i])
            self.marketValue.append(opt.marketValue())
            self.modelValue.append(opt.modelValue())
            self.relativeError.append(
                100.0*(opt.modelValue()/opt.marketValue() - 1.0))
            self.avgError += abs(err)
        self.avgError = self.avgError*100.0/len(self.heston_helpers)
        self.to_data()

    def to_data(self):
        self.errors_data = pd.DataFrame({"Strikes": self.strks, "Market Value": self.marketValue,
                                        "Model Value": self.modelValue, "Relative Error (%)": self.relativeError})
        self.var_data = pd.DataFrame(data=[self.v0, self.kappa, self.theta, self.sigma, self.rho, self.avgError], index=[
                                     "v0", "kappa", "theta", "sigma", "rho", "avgError"], columns=["Value"])
