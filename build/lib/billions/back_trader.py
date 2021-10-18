from billions.tools.analysier import analysier
import pandas as pd
import numpy as np
from tqdm import tqdm

from billions.tools.profolio import *
from billions.tools.deal_time import *

# TODO: 手续费
# TODO：买入和卖出价格，当前均使用收盘价，假设能够以收盘价成交
# TODO: 支持做空（profolio中amount可以为负值）
# TODO: 加入乘子，保证交易金额为整数


class trader:
    """
    This is the parent class for all trader class. In fact, you can use it to test many strategy.

    args:
    data: data you need
    amount: money you have in your account.
    profolio: profolio type (myprofolio, euqal_profolio)
    peride: the peride you need to change your profolio
    """

    def __init__(self, data, total_amount=1000000, peride='D', price_col='close', name='strategy'):
        """
        init function
        """
        data = data.fillna(0)
        self.data = data
        self.dict_data = self.data.to_dict('index')
        self.total_amount = total_amount
        self.peride = peride
        self.price_col = price_col
        self.lable = 1
        self.name = name
        self.closes = self.data.reset_index().pivot(
            'trade_dt', 'code', self.price_col)
        self.closes = self.closes.fillna(0)
        self.closes = self.closes.to_dict('index')

        self.lables = [1]
        self.dates = np.unique(np.array(list(self.data.index))[:, 0])
        self.codes = np.unique(np.array(list(self.data.index))[:, 1])
        self.profolio = profolio(self.dates[0], total_amount)

        self.results = {}

    # mid function

    def get_trade_date(self):
        """
        **You don't want to change this**
        it can return the trade date you need.
        """
        if type(self.peride) == int:
            self.trade_dates = ndays(self.dates, self.peride)
        else:
            if self.peride == 'D':
                self.trade_dates = self.dates
            if self.peride == 'M':
                self.trade_dates = monthly(self.dates)
            if self.peride == 'Mf':
                self.trade_dates = monthly(self.dates, type='first')
            if self.peride == 'Ml':
                self.trade_dates = monthly(self.dates, type='last')

    def today_price(self, date):
        """
        it can get returns in certain date
        **You don't want to change this**
        """
        # prices = self.data.loc[date].reset_index()[['code', self.price_col]]
        # return dict(prices.set_index('code')[self.price_col])
        return self.closes[date]
        

    # set function
    def set_lable(self, lable):
        """
        change the lable
        **You don't want to change this**
        """
        if lable != -1:
            self.lable = lable

    def set_peride(self, peride):
        """
        change the peride
        **You don't want to change this**
        """
        if peride != -1:
            self.peride = peride

    def reset_profolio(self, reset):
        """
        reset the profolio
        **You don't want to change this**
        """
        if reset:
            self.profolio = profolio(
                self.dates[0], self.total_amount)

    # analysis function
    def plot(self):
        """
        return the ploter
        **You don't want to change this**
        """
        self.analysier.plot()

    def trade_summary(self):
        """
        get summary
        **You don't want to change this**
        """
        self.summaries = self.analysier.summary()
        return self.summaries

    def summary(self):
        self.plot()
        self.trade_summary()
        self.analysier.plot_summary()

    # main function
    def _run(self, lable=-1, peride=-1, reset=True):
        """
        it go over every day and get result
        **You don't want to change this**

        return:
        result: everyday profolio and amount
        """
        # set basic info
        self.set_lable(lable)
        self.set_peride(peride)
        self.reset_profolio(reset)

        # get trade date
        self.get_trade_date()

        # satrt to trade
        networths = {}
        result = {}
        for date in tqdm(self.dates, leave=False, desc="lable-" + str(self.lable)):
            prices = self.today_price(date)
            self.profolio.adjust_price(date, prices)  # adjust daily price
            if date in self.trade_dates:
                self.trade(date, prices)
            networths[date] = self.profolio.get_total()
            result[date] = self.profolio.get_profolio()
        # result = pd.DataFrame(result.values(), index=result.keys())
        # result = result.fillna({'amount':0, 'price':0, 'buy_price': 0})
        self.results[self.lable] = result
        return pd.DataFrame([networths]).T

        # result = self.results[self.lable]
        # self.networth = pd.DataFrame(result.sum(axis=1))
        # self.networth.columns = ['networth']
        # return self.networth

    def run(self, peride=-1):
        """
        run for all lable
        **You don't want to change this**
        """
        networths = []
        for lable in self.lables:
            networth = self._run(lable=lable, peride=peride, reset=True)
            networths.append(networth)

        # get networth
        self.networth = pd.concat(networths, axis=1)
        self.networth.columns = list(
            map(lambda x: 'group-' + str(x), self.lables))

        # get long short
        if len(self.lables) > 4:
            self.longshort = self.networth.copy()
            self.longshort['long/short-1'] = self.networth['group-' +
                                                           str(1)] / self.networth['group-'+str(self.number)]
            self.longshort['long/short-2'] = self.networth['group-' +
                                                           str(2)] / self.networth['group-'+str(self.number-1)]
            for i in range(1, self.number+1, 1):
                self.longshort = self.longshort.drop('group-'+str(i), axis=1)
        elif len(self.lables) > 2:
            self.longshort = self.networth.copy()
            self.longshort['long/short-1'] = self.networth['group-' +
                                                           str(1)] / self.networth['group-'+str(self.number)]
            for i in range(1, self.number+1, 1):
                self.longshort = self.longshort.drop('group-'+str(i), axis=1)
        elif len(self.lables) < 2:
            self.longshort = -1
        self.networth = (
            ((self.networth - self.networth.shift())/self.networth.shift()+1).cumprod())
        self.analysier = analysier(self)

    def trade(self, date, prices):
        pass


class group_trader(trader):
    """
    This is the parent class for all trader class. In fact, you can use it to test many strategy.

    !!! : caculator return all using close price.

    parent args:
    data: data you need
    amount: money you have in your account.
    profolio: profolio type (myprofolio, euqal_profolio)
    peride: the peride you need to change your profolio

    unique args:
    number: the number of groups
    inverse: if the factor is inversed
    """

    def __init__(self, data, total_amount=1000000, peride='D', price_col='close', name='strategy', number=5, inverse=False):
        """
        init fuction
        """
        trader.__init__(self, data, total_amount, peride, price_col, name=name)

        # self.factor = data[['factor']]

        self.inverse = not inverse
        self.number = number

        self.lables = list(range(1, self.number+1, 1))

        if self.inverse:
            self.factors = (self.data.reset_index().pivot(
                'trade_dt', 'code', 'factor')*-1).to_dict('index')
        else:
            self.factors = self.data.reset_index().pivot(
                'trade_dt', 'code', 'factor').to_dict('index')

    # main function
    def trade(self, date, prices):
        """
        trade function: change profolio to target
        """
        # get codes
        today_factor = self.factors[date]

        ind = np.where(list(pd.qcut(list(today_factor.values()),
                            self.number, labels=range(1, self.number+1, 1)) == self.lable))[0]

        codes = np.array(list(today_factor.keys()))[ind]

        # trade
        buys = []
        sells = []
        for code in self.profolio.get_profolio():
            if code not in codes:
                sells.append(code)
        for code in codes:
            if code not in self.profolio.get_profolio():
                buys.append(code)

        self.profolio.add_n_sell(buys, sells, prices)


class top_trader(trader):

    def __init__(self, data, total_amount=1000000, peride='D', price_col='close', name='strategy', top=1):
        """
        init fuction
        """
        trader.__init__(self, data, total_amount, peride, price_col, name=name)

        self.top = top
        self.factor = data[['factor']]
        self.close = data[['close']]

        self.factors = (self.data.reset_index().pivot(
            'trade_dt', 'code', 'factor')).to_dict('index')

    # main function
    def trade(self, date, prices):
        """
        trade function: change profolio to target
        """
        today_factor = self.factors[date]
        codes = list(dict(sorted(today_factor.items(),
                                 key=lambda e: e[1], reverse=True)).keys())[:self.top]

        buys = []
        sells = []
        for code in self.profolio.get_profolio():
            if code not in codes:
                sells.append(code)
        for code in codes:
            if code not in self.profolio.get_profolio():
                buys.append(code)

        self.profolio.add_n_sell(buys, sells, prices)
