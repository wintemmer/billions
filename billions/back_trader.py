import pandas as pd
import numpy as np
from pandas.io.sql import read_sql_query
from tqdm import tqdm

from billions.back_traders.profolio import *
from billions.back_traders.deal_time import *
from billions.back_traders.ploter import *

# TODO: 手续费
# TODO：买入和卖出价格


class trader:
    """
    This is the parent class for all trader class. In fact, you can use it to test many strategy.

    args:
    data: data you need
    amount: money you have in your account.
    profolio: profolio type (myprofolio, euqal_profolio)
    peride: the peride you need to change your profolio
    """

    def __init__(self, data, amount=1000000, fluent=1, profolio=euqal_profolio, peride='D'):
        """
        init function
        """
        self.type = profolio
        self.amount = amount
        self.fluent = fluent
        self.profolio = profolio(amount, fluent)
        self.peride = peride

        self.dates = np.unique(np.array(list(data.index))[:, 0])
        self.lable = 1
        self.results = {}

    # mid function
    def get_trade_date(self):
        """
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

    def today_return(self, date):
        """
        it can get returns in certain date
        """
        return

    # set function
    def set_lable(self, lable):
        if lable != -1:
            self.lable = lable

    def set_peride(self, peride):
        if peride != -1:
            self.peride = peride

    def reset_profolio(self, reset):
        if reset:
            self.profolio = self.type(self.amount, self.fluent)

    # analysis function
    def ploter(self):
        return theploter(self)

    # main function
    def trade(self, date):
        """
        Your trade in certain date
        """
        pass

    def run_top(self, lable=-1, peride=-1, reset=True):
        """
        it's where everything begin

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
        result = {}
        for date in tqdm(self.dates, leave=False, desc="lable-" + str(self.lable)):
            ret = self.today_return(date)
            self.profolio.adjust_price(ret)  # adjust daily price
            if date in self.trade_dates:
                self.trade(date)
            result[date] = self.profolio.profolio.copy()
        result = pd.DataFrame(result.values(), index=result.keys())
        result = result.fillna(0)
        self.results[self.lable] = result
        return result

    def run(self, peride=-1):
        result = self.results[self.lable]
        networth = pd.DataFrame(result.sum(axis=1))
        networth.columns = ['networth']


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

    def __init__(self, data, amount=1000000, fluent=1, profolio=euqal_profolio, peride='D', number=5, inverse=False):
        """
        init fuction
        """
        trader.__init__(self, data, amount, fluent, profolio, peride)

        self.factor = data[['factor']]
        self.close = data[['close']]
        self.inverse = not inverse
        self.lable = number
        self.number = number

        self.ret = self.caculate_return()

    # mid function
    def get_trade_date(self):
        """
        it can return the trade date you need.
        """
        return super().get_trade_date()

    def today_return(self, date):
        """
        it can get returns in certain date
        """
        r = self.ret.loc[date].reset_index()[['code', 'return']]
        return dict(r.set_index('code')['return'])

    # set function
    def set_lable(self, lable):
        return super().set_lable(lable)

    def set_peride(self, peride):
        return super().set_peride(peride)

    def reset_profolio(self, reset):
        return super().reset_profolio(reset)

    # main function
    def trade(self, date):
        """
        trade function: change profolio to target
        """
        codes = self.get_lable_code(date)
        buys = []
        sells = []
        for code in self.profolio.get_profolio():
            if code not in codes:
                sells.append(code)
        for code in codes:
            if code not in self.profolio.get_profolio():
                buys.append(code)

        self.profolio.add_n_sell(buys, sells)

    def run_top(self, lable=-1, peride=-1, reset=True):
        return super().run_top(lable=lable, peride=peride, reset=reset)

    def run(self, peride=-1):
        """
        run for all lable
        """
        if peride != -1:
            self.set_peride(peride)
        results = []
        for lable in range(1, self.number+1, 1):
            result = self.run_top(lable=lable, peride=self.peride, reset=True)
            results.append(result)

        # get networth
        self.networth = pd.concat(
            list(map(lambda x: x.sum(axis=1), results)), axis=1)
        self.networth.columns = list(
            map(lambda x: 'group-' + str(x), range(1, self.number+1, 1)))

        # get long short
        self.longshort = self.networth.copy()
        self.longshort['long/short-1'] = self.networth['group-' +
                                                       str(1)] / self.networth['group-'+str(self.number)]
        self.longshort['long/short-2'] = self.networth['group-' +
                                                       str(2)] / self.networth['group-'+str(self.number-1)]
        for i in range(1, self.number+1, 1):
            self.longshort = self.longshort.drop('group-'+str(i), axis=1)

    # child tool function
    def get_lable_code(self, date):
        """
        get code list in a certain date
        """
        today_factor = self.factor.loc[date, :].sort_values(
            'factor', ascending=self.inverse).reset_index()
        if self.inverse:
            def change(x): return -x
        else:
            def change(x): return x
        today_factor['factor'] = pd.qcut(
            change(today_factor['factor']), self.number, labels=range(1, self.number+1, 1))
        codes = list(
            today_factor[today_factor['factor'] == self.lable]['code'])
        return codes

    def caculate_return(self):
        """
        get return from close
        """
        c = self.close.reset_index().pivot('trade_dt', 'code')['close']
        ret = (c - c.shift())/c.shift()
        ret = ret.fillna(0)
        ret = pd.DataFrame(ret.stack())
        ret.columns = ['return']
        return ret
