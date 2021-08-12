import numpy as np
from billions.tools.log import *

class my_profolio:

    def __init__(self, date, total_amount=1000000, fluent=1) -> None:
        self.profolio = {'freemoney': total_amount}
        self.fluent = fluent
        self.date = date

    def get_profolio(self):
        pro = list(self.profolio.keys())
        pro.remove('freemoney')
        return pro

    def buy(self, stock, amount):
        if self.profolio['freemoney'] < amount:
            log(str(self.date) + ' -- Sorry, you don\'t have enoung money')
        else:
            if stock in self.profolio.keys():
                self.profolio[stock] += amount
                self.profolio['freemoney'] -= amount
            else:
                self.profolio[stock] = amount
                self.profolio['freemoney'] -= amount

    def sell(self, stock, amount):
        if stock not in self.profolio.keys():
            log(str(self.date) + ' -- Sorry, you don\'t have ' + stock)
        else:
            if self.profolio[stock] < amount:
                self.sell_all([stock])
            else:
                self.profolio[stock] -= amount
                self.profolio['freemoney'] += amount
                if self.profolio[stock] == 0:
                    self.profolio.pop(stock)

    def profolio_report(self):
        log(str(self.date) + ' -- my profolio: ' + str(self.profolio) +
              ' -- total: ' + str(np.mean(list(self.profolio.values()))))

    def adjust_price(self, date, rets):
        self.date = date
        for code in self.profolio.keys():
            if code != 'freemoney':
                self.profolio[code] = self.profolio[code] * ((rets[code])+1)

    def sell_all(self, stocks):
        for stock in stocks:
            if stock in self.profolio.keys():
                self.sell(stock, self.profolio[stock])
            else:
                log(str(self.date) + ' -- Sorry, you don\'t have this ' + stock)


class euqal_profolio(my_profolio):

    def __init__(self, date, total_amount, fluent) -> None:
        super().__init__(date, total_amount, fluent)

    def add(self, stocks):
        for stock in stocks:
            self.profolio[stock] = 0

    def add_n_sell(self, buys, sells):
        self.sell_all(sells)
        self.add(buys)
        self.rebalance()

    def rebalance(self):
        each = int(self.fluent*np.sum(list(self.profolio.values())) /
                   (len(self.profolio)-1))
        for s in self.profolio.keys():
            if s == 'freemoney':
                pass
            else:
                if self.profolio[s] > each:
                    self.sell(s, self.profolio[s] - each)
        for s in self.profolio.keys():
            if s == 'freemoney':
                pass
            else:
                if self.profolio[s] < each:
                    self.buy(s, each - self.profolio[s])
