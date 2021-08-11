import pandas as pd
import numpy as np
from pandas.io.sql import read_sql_query
from tqdm import tqdm

from billions.back_traders.profolio import *

# TODO: 换仓周期
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

    def __init__(self, data, amount, profolio=euqal_profolio, peride='D'):
        """
        init function
        """
        self.type = profolio
        self.amount = amount
        self.profolio = profolio(amount)
        self.peride = peride

        self.dates = []
        self.lable = 1

    # mid function
    def get_trade_date(self):
        """
        it can return the trade date you need.
        """
        if self.peride == 'D':
            self.trade_dates = self.dates

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
            self.profolio = self.type(self.amount)

    # main function
    def trade(self, date):
        """
        Your trade in certain date
        """
        pass

    def run(self, lable=-1, peride=-1, reset=True):
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
        return result


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

    def __init__(self, data, amount, profolio=euqal_profolio, peride='D', number=5, inverse=False):
        """
        init fuction
        """
        trader.__init__(self, data, amount, profolio, peride)

        self.dates = np.unique(np.array(list(data.index))[:, 0])
        self.factor = data[['factor']]
        self.close = data[['close']]
        self.inverse = inverse
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
        for code in self.profolio.get_profolio():
            if code not in codes:
                self.profolio.sell_all(code)
        for code in codes:
            if code not in self.profolio.get_profolio():
                self.profolio.add(code)

    def run_top(self, lable, peride, reset):
        return super().run(lable=lable, peride=peride, reset=reset)

    def run(self, peride=-1):
        """
        run for all lable
        """
        if peride!=-1:
            self.set_peride(peride)
        results = []
        for lable in range(1, self.number+1, 1):
            result = self.run_top(lable=lable, peride=self.peride, reset=True)
            results.append(result)
        self.daily = pd.concat(
            list(map(lambda x: x.sum(axis=1), results)), axis=1)
        self.daily.columns = list(
            map(lambda x: 'group-' + str(x), range(1, self.number+1, 1)))

    # child tool function
    def get_lable_code(self, date):
        """
        get code list in a certain date
        """
        today_factor = self.factor.loc[date, :].sort_values(
            'factor', ascending=self.inverse).reset_index()
        today_factor['factor'] = pd.qcut(
            today_factor['factor'], self.number, labels=range(1, self.number+1, 1))
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
