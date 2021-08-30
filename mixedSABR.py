# CALIBRATE MIXED SABR

class MixedSABRSmile:
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
        self.current_price = current_price
        self.newVols = None
        self.error = None

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
            # {'type': 'eq', 'fun': lambda x: x[0] - x[4] * math.log(current_price)**self.beta_free},
            # {'type': 'ineq', 'fun': lambda x: x[4] - 0.001},
            # {'type': 'eq', 'fun': lambda x: x[1]},
            # {'type': 'eq', 'fun': lambda x: x[5] - self.beta_free},
            # {'type': 'eq', 'fun': lambda x: x[2] - x[6] / (1 - self.beta_free)},
            # {'type': 'ineq', 'fun': lambda x: x[6] - 0.001},
            # {'type': 'ineq', 'fun': lambda x: .99 - x[3]**2},
            # {'type': 'eq', 'fun': lambda x: x[7]},

            {'type': 'eq', 'fun': lambda x: x[0] - self.alpha_free * \
                math.log(current_price)**self.beta_free},
            {'type': 'eq', 'fun': lambda x: x[4] - self.alpha_free},
            {'type': 'eq', 'fun': lambda x: x[1]},
            {'type': 'eq', 'fun': lambda x: x[5] - self.beta_free},
            {'type': 'eq', 'fun': lambda x: x[2] - \
                self.nu_free / (1 - self.beta_free)},
            {'type': 'eq', 'fun': lambda x: x[6] - self.nu_free},
            {'type': 'ineq', 'fun': lambda x: x[3]},
            {'type': 'ineq', 'fun': lambda x: .99 - x[3]},
            {'type': 'eq', 'fun': lambda x: x[7]},
        )

        x = self.set_init_conds()

        result = minimize(self.f, x, constraints=cons, method="SLSQP")
        self.error = result['fun']
        params = [self.alpha_N, self.beta_N, self.nu_N, self.rho_N, self.alpha_free,
                  self.beta_free, self.nu_free, self.rho_free] = result['x']

        self.newVols = [self.calibrate_volatilities(
            strike, params) for strike in strikes]

    def set_init_conds(self):
        return [self.alpha_N, self.beta_N, self.nu_N, self.rho_N, self.alpha_free, self.beta_free, self.nu_free, self.rho_free]

    def calibrate_volatilities(self, strike, params):

        alpha_N, beta_N, nu_N, rho_N = [params[i] for i in range(4)]
        alpha_free, beta_free, nu_free, rho_free = [
            params[i] for i in range(4, 8)]

        alpha_N = alpha_free * math.log(current_price)**beta_free
        nu_N = nu_free / (1 - beta_free)
        p = (alpha_N * beta_free * math.exp(self.s)) / \
            ((alpha_N * beta_free * math.exp(self.s)) + abs(nu_N * rho_N))

        normalSABR = ql.sabrVolatility(
            strike, self.fwd, self.expiryTime, alpha_N, beta_N, nu_N, rho_N)

        print(alpha_N, beta_N, nu_N, rho_N, normalSABR)
        return math.sqrt((p**2) * self.freeSABR.newVols[int(np.where(strikes == strike)[0])] + ((1-p)**2) * normalSABR)

    def f(self, params):

        alpha_N, beta_N, nu_N, rho_N, alpha_free, beta_free, nu_free, rho_free = params

        beta_N = self.beta_N
        rho_free = self.rho_free
        beta_free = self.beta_free

        # Force parameters bounds
        alpha_N = max(alpha_N, 1e-8)
        alpha_free = max(alpha_free, 1e-8)
        nu_N = max(nu_N, 1e-8)
        rho_N = max(rho_N, -0.999)
        rho_N = min(rho_N, 0.999)

        params = [alpha_N, beta_N, nu_N, rho_N,
                  alpha_free, beta_free, nu_free, rho_free]

        mixed_vols = np.array([self.calibrate_volatilities(
            strike, params) for strike in strikes])

        self.error = ((mixed_vols - np.array(self.marketVols))**2).mean() ** .5

        return self.error


class MixedSABRVolatilitySurface:
    def __init__(self, fwd=current_price, label="", dates=dates):
        self.fwd = fwd
        self.label = label
        self.dates = dates
        self.vol_surface_vector, self.errors = [], []
        self.alpha_N, self.beta_N, self.nu_N, self.rho_N = [], [], [], []
        self.alpha_free, self.beta_free, self.nu_free, self.rho_free = [], [], [], []

        self.initialize()

    def initialize(self):
        self.SABRVolMatrix, self.SABRVolDiffMatrix = (ql.Matrix(
            len(strikes), len(self.dates)), ql.Matrix(len(strikes), len(self.dates)))

        for i, d in enumerate(self.dates):
            volMixedSABR = MixedSABRSmile(date=d, fwd=self.fwd)

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

    def to_dataframe(self):
        d = {'alpha_free': self.alpha_free, 'beta_free': self.beta_free, 'nu_free': self.nu_free, 'rho_free': self.rho_free,
             'alpha_N': self.alpha_free, 'beta_N': self.beta_N, 'nu_N': self.nu_N, 'rho_N': self.rho_N}
        return pd.DataFrame(data=d, index=self.dates)


MixedSABRVolatilitySurface(dates=dates[4:]).to_dataframe()
