from initialize import *
from SABR import *
from plots import *

# MIXTURE SABR


class MixtureSABRSmile:
    def __init__(self, date, fwd=current_price, s=0):
        self.date = date
        self.expiryTime = round((self.date - today)/365, 6)
        self.marketVols = vols[dates.index(self.date)]
        self.fwd = fwd
        self.s = s
        self.alpha_N = .1
        self.beta_N = 0.
        self.nu_N = .1
        self.rho_N = .1
        self.alpha_free = .1
        self.beta_free = .5
        self.nu_free = .1
        self.rho_free = 0.

        self.initialize()

    def initialize(self):

        # # calibrate the Free Zero-Correlation SABR first
        self.freeSABR = SABRSmile(
            date=self.date, beta=.5, method="floch-kennedy", fwd=self.fwd, zero_rho=True)
        self.freeSABR.initialize()
        self.alpha_free = self.freeSABR.alpha
        self.beta_free = self.freeSABR.beta
        self.nu_free = self.freeSABR.nu

        # alpha, beta, nu, rho (Normal, free)
        cons = (
            {'type': 'eq', 'fun': lambda x: x[0] - self.alpha_free *
                math.log(current_price)**self.beta_free},
            {'type': 'eq', 'fun': lambda x: x[4] - self.alpha_free},
            {'type': 'eq', 'fun': lambda x: x[1]},
            {'type': 'eq', 'fun': lambda x: x[5] - self.beta_free},
            {'type': 'eq', 'fun': lambda x: x[2] -
                self.nu_free / (1 - self.beta_free)},
            {'type': 'eq', 'fun': lambda x: x[6] - self.nu_free},
            {'type': 'ineq', 'fun': lambda x: x[3]},
            {'type': 'ineq', 'fun': lambda x: .99 - x[3]},
            {'type': 'eq', 'fun': lambda x: x[7]},
        )

        # Set initial conditions
        x = [self.alpha_N, self.beta_N, self.nu_N, self.rho_N,
             self.alpha_free, self.beta_free, self.nu_free, self.rho_free]

        result = minimize(self.f, x, constraints=cons, method="SLSQP")
        self.error = result['fun']
        params = [self.alpha_N, self.beta_N, self.nu_N, self.rho_N, self.alpha_free,
                  self.beta_free, self.nu_free, self.rho_free] = result['x']

        self.newVols = [self.calibrate_volatilities(
            strike, params) for strike in strikes]

    def calibrate_volatilities(self, strike, params):

        p = (params[0] * params[5] * math.exp(self.s)) / \
            ((params[0] * params[5] * math.exp(self.s)) +
             abs(params[2] * params[3]))

        normalSABR = ql.sabrVolatility(
            strike, self.fwd, self.expiryTime, *params[:4])

        return math.sqrt((p**2) * self.freeSABR.newVols[int(np.where(strikes == strike)[0])] + ((1-p)**2) * normalSABR)

    def f(self, params):

        mixture_vols = np.array([self.calibrate_volatilities(
            strike, params) for strike in strikes])

        self.error = ((mixture_vols - np.array(self.marketVols))
                      ** 2).mean() ** .5

        return self.error


class MixtureSABRVolatilitySurface:
    def __init__(self, fwd=current_price, label="Mixture SABR, {}".format(data_label), dates=dates):
        self.fwd = fwd
        self.label = label
        self.dates = dates
        self.vol_surface_vector, self.errors = [], []
        self.alpha_N, self.beta_N, self.nu_N, self.rho_N = [], [], [], []
        self.alpha_free, self.beta_free, self.nu_free, self.rho_free = [], [], [], []

        self.initialize()

    def initialize(self):
        self.SABRVolMatrix, self.SABRVolDiffMatrix = (
            ql.Matrix(len(strikes), len(self.dates)),
            ql.Matrix(len(strikes), len(self.dates))
        )

        for i, d in enumerate(self.dates):
            volMixedSABR = MixtureSABRSmile(date=d, fwd=self.fwd)

            self.alpha_N.append(volMixedSABR.alpha_N)
            self.alpha_free.append(volMixedSABR.alpha_free)
            self.beta_N.append(volMixedSABR.beta_N)
            self.beta_free.append(volMixedSABR.beta_free)
            self.nu_N.append(volMixedSABR.nu_N)
            self.nu_free.append(volMixedSABR.nu_free)
            self.rho_N.append(volMixedSABR.rho_N)
            self.rho_free.append(volMixedSABR.rho_free)

            self.errors.append(volMixedSABR.error)

            smile = volMixedSABR.newVols
            self.vol_surface_vector.extend(smile)

            # constructing the SABRVolatilityMatrix
            for j in range(len(smile)):
                self.SABRVolMatrix[j][i] = smile[j]
                self.SABRVolDiffMatrix[j][i] = (
                    smile[j] - vols[i][j]) / vols[i][j]

            self.vol_surface = ql.BlackVarianceSurface(
                today, calendar, self.dates, strikes, self.SABRVolMatrix, day_count)
            self.vol_surface.enableExtrapolation()

    def to_data(self):
        d = {'alpha_free': self.alpha_free, 'beta_free': self.beta_free, 'nu_free': self.nu_free, 'rho_free': self.rho_free,
             'alpha_N': self.alpha_free, 'beta_N': self.beta_N, 'nu_N': self.nu_N, 'rho_N': self.rho_N,
             'MSE': self.errors,
             }
        return pd.DataFrame(data=d, index=self.dates)

    def plot(self):
        fig, axs = plt.subplots(2, 4, figsize=plot_size)
        plt.subplots_adjust(right=2, top=2)

        x_values = [(x-today)/365. for x in self.dates]

        axs[0, 0].plot(x_values, self.alpha_free, label="alpha_free")
        axs[0, 0].set_title('Alpha Free-Boundary SABR')
        axs[0, 0].set(xlabel='time to expiry (in years)', ylabel='value')
        axs[0, 0].legend()
        axs[0, 1].plot(x_values, self.nu_free, label="nu_free")
        axs[0, 1].set_title('Nu Free-Boundary SABR')
        axs[0, 1].set(xlabel='time to expiry (in years)', ylabel='value')
        axs[0, 1].legend()
        axs[0, 2].plot(x_values, self.alpha_N, label="alpha_N")
        axs[0, 2].set_title('Alpha Normal SABR')
        axs[0, 2].set(xlabel='time to expiry (in years)', ylabel='value')
        axs[0, 2].legend()
        axs[0, 3].plot(x_values, self.nu_N, label="nu_N")
        axs[0, 3].set_title('Nu Normal SABR')
        axs[0, 3].set(xlabel='time to expiry (in years)', ylabel='value')
        axs[1, 3].legend()
        axs[1, 0].plot(x_values, self.rho_N, label="rho_N")
        axs[1, 0].set_title('Rho Normal SABR')
        axs[1, 0].set(xlabel='time to expiry (in years)', ylabel='value')
        axs[1, 0].legend()
        axs[1, 1].plot(x_values, self.errors, label="Relative Error %")
        axs[1, 1].set_title('Relative Error %')
        axs[1, 1].set(xlabel='time to expiry (in years)', ylabel='value')
        axs[1, 1].legend()
