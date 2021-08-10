import numpy as np

class my_profolio:

    def __init__(self, amount) -> None:
        self.profolio = {'freemoney': amount}

    def buy(self, stock, amount):
        if self.profolio['freemoney'] < amount:
            print('Sorry, you don\'t have enoung money')
        if stock in self.profolio.keys:
            self.profolio[stock] += amount
            self.profolio['freemoney'] -= amount
        else:
            self.profolio[stock] = amount
            self.profolio['freemoney'] -= amount

    def sell(self, stock, amount):
        if stock not in self.profolio.keys or self.profolio[stock] < amount:
            print('Sorry, you don\'t have enoungh ' + stock)
        else:
            self.profolio[stock] -= amount
            self.profolio['freemoney'] += amount
        if self.profolio[stock] == 0:
            self.profolio.pop(stock)

    def profolio_report(self):
        print('my profolio: ' + self.profolio + ' -- total: ' + np.mean(self.profolio))


class euqal_profolio(my_profolio):

    def __init__(self, amount) -> None:
        super().__init__(amount)

    def buy(self, stock, amount):
        return super().buy(stock, amount)

    def sell(self, stock, amount):
        return super().sell(stock, amount)

    def profolio_report(self):
        return super().profolio_report()

    def add(self, stock):
        self.profolio[stock] = 0
        self.rebalance()

    def sell_all(self, stock):
        if stock in self.profolio.keys:
            self.sell(stock, self.profolio[stock])
        else:
            print('Sorry, you don\'t have this ' + stock)
        self.rebalance()

    def rebalance(self):
        each = self.profolio.values/(len(self.profolio)-1)
        for s in self.profolio.keys:
            if s == 'freemoney':
                pass
            else:
                if self.profolio[s] < each:
                    self.buy(s, each - self.profolio[s])
                else:
                    self.sell(s, self.profolio[s] - each)
