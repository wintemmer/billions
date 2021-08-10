import pandas as pd
import numpy as np
from pandas.io.sql import read_sql_query
from tqdm import tqdm

from billions.back_traders.profolio import *


class trader:
    def __init__(self, amount, profolio=euqal_profolio, peride='D'):
        self.profolio = profolio(amount)
        self.peride = peride

        self.daterange = []

    def get_trade_date(self):
        self.dates = self.daterange
        # TODO

    def trade(self, date):
        pass

    def run(self):
        self.get_trade_date()
        result = {}
        for date in tqdm(self.dates):
            self.trade(date)
            result[date] = self.profolio
        self.daily = pd.DataFrame(result)
        return self.daily


class group_trader(trader):
    def __init__(self, data, lable, amount, profolio=euqal_profolio, peride='D', inverse=False):
        trader.__init__(self)

        self.daterange = np.unique(np.array(list(data.index))[:, 0])
        self.factor = data[['factor']]
        self.close = data[['close']]
        self.inverse = inverse
        self.lable = lable

    def get_trade_date(self):
        return super().get_trade_date()

    def trade(self, date):
        codes = self.get_lable_code()
        for code in self.profolio.get_profolio():
            if code not in codes:
                self.profolio.sell_all(code)
        for code in codes:
            if code not in self.profolio.get_profolio():
                self.profolio.add(code)

    def run(self):
        return super().run()

    def get_lable_code(self, date):
        today_factor = self.factor.loc[date, :].sort_values(
            'factor', ascending=self.inverse).reset_index()
        today_factor['factor'] = pd.qcut(
            today_factor['factor'], 5, labels=range(1, 6, 1))
        codes = list(today_factor[today_factor['factor'] == 1]['code'])
        return codes
