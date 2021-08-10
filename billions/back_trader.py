import pandas as pd
import numpy as np
from pandas.io.sql import read_sql_query

from billions.back_traders.profolio import *

class trader:
    def __init__(self, amount, profolio = euqal_profolio):
        self.profolio = profolio(amount)
        self.daterange = []

    def trade(self):
        pass

    def run(self):
        result = {}
        for date in self.daterange:
            self.trade()
            result[date] = self.profolio
        self.daily = pd.DataFrame(result)
        return self.daily
