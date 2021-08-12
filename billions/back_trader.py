import pandas as pd
import numpy as np
from pandas.io.sql import read_sql_query
from tqdm import tqdm

from billions.tools.profolio import *
from billions.tools.deal_time import *
from billions.tools.ploter import *

# TODO: 手续费
# TODO：买入和卖出价格，当前均使用收盘价，假设能够以收盘价成交s


class trader:
    """
    This is the parent class for all trader class. In fact, you can use it to test many strategy.

    args:
    data: data you need
    amount: money you have in your account.
    profolio: profolio type (myprofolio, euqal_profolio)
    peride: the peride you need to change your profolio
    """

    def __init__(self, data, total_amount=1000000, fluent=1, profolio=euqal_profolio, peride='D', name='backtest'):
        """
        init function
        """
        self.type = profolio
        self.total_amount = total_amount
        self.fluent = fluent
        self.peride = peride
        self.name = name
        self.lables = [1]
        self.dates = np.unique(np.array(list(data.index))[:, 0])
        self.profolio = profolio(self.dates[0], total_amount, fluent)

        # self.ret = self.caculate_return()

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

    def today_return(self, date):
        """
        it can get returns in certain date
        **You don't want to change this**
        """
        r = self.ret.loc[date].reset_index()[['code', 'return']]
        return dict(r.set_index('code')['return'])

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
            self.profolio = self.type(
                self.dates[0], self.total_amount, self.fluent)

    # analysis function
    def ploter(self):
        """
        return the ploter
        **You don't want to change this**
        """
        return theploter(self)

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
        result = {}
        for date in tqdm(self.dates, leave=False, desc="lable-" + str(self.lable)):
            ret = self.today_return(date)
            self.profolio.adjust_price(date, ret)  # adjust daily price
            if date in self.trade_dates:
                self.trade(date)
            result[date] = self.profolio.profolio.copy()
        result = pd.DataFrame(result.values(), index=result.keys())
        result = result.fillna(0)
        self.results[self.lable] = result

        result = self.results[self.lable]
        self.networth = pd.DataFrame(result.sum(axis=1))
        self.networth.columns = ['networth']
        return self.networth

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

    def trade(self, date):
        pass

    def signal(self):
        return

    def caculate_return(self):
        return


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

    def __init__(self, data, total_amount=1000000, fluent=1, profolio=euqal_profolio, peride='D', number=5, inverse=False, name='backtest'):
        """
        init fuction
        """
        trader.__init__(self, data, total_amount,
                        fluent, profolio, peride, name)

        self.factor = data[['factor']]
        self.close = data[['close']]
        self.inverse = not inverse
        self.number = number

        self.lables = list(range(1, self.number+1, 1))
        self.ret = self.caculate_return()

    # main function
    def trade(self, date):
        """
        trade function: change profolio to target
        """
        codes = self.signal(date)
        buys = []
        sells = []
        for code in self.profolio.get_profolio():
            if code not in codes:
                sells.append(code)
        for code in codes:
            if code not in self.profolio.get_profolio():
                buys.append(code)

        self.profolio.add_n_sell(buys, sells)

    # child tool function
    def signal(self, date):
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
