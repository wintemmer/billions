import numpy as np
from billions.tools.log import *


class profolio:

    def __init__(self, date, total_amount=1000000) -> None:
        self.profolio = {'freemoney': {
            'amount': total_amount,
            'price': 1,
            'buy_price': 1
        }
        }
        self.date = date

    def get_profolio(self):
        pro = list(self.profolio.keys())
        pro.remove('freemoney')
        return pro

    def buy(self, stock, amount, price):
        if self.profolio['freemoney']['amount'] < amount*price:
            log(str(self.date) + ' -- Sorry, you don\'t have enoung money')
        else:
            if stock in self.profolio.keys():
                self.profolio[stock]['amount'] += amount
                self.profolio[stock]['price'] = price
                self.profolio[stock]['buy_price'] = price
                self.profolio['freemoney']['amount'] -= amount*price
            else:
                self.profolio[stock] = {
                    'amount': amount,
                    'price': price,
                    'buy_price': price
                }
                self.profolio['freemoney']['amount'] -= amount*price

    def sell(self, stock, amount, price):
        if stock not in self.profolio.keys():
            log(str(self.date) + ' -- Sorry, you don\'t have ' + stock)
        else:
            if self.profolio[stock]['amount'] < amount:
                log(str(self.date) + ' -- Sorry, you don\'t have enough ' + stock)
            else:
                self.profolio[stock]['amount'] -= amount
                self.profolio[stock][price] = price
                self.profolio['freemoney']['amount'] += amount*price
                if self.profolio[stock]['amount'] == 0:
                    self.profolio.pop(stock)

    def profolio_report(self):
        log(str(self.date) + ' -- my profolio: ' + str(self.profolio) +
            ' -- total: ' + str(np.mean(list(self.profolio.values()))))

    def adjust_price(self, date, prices):
        self.date = date
        for code in self.profolio.keys():
            if code != 'freemoney':
                self.profolio[code]['price'] = prices[code]

    def sell_all(self, stocks, prices):
        for stock in stocks:
            if stock in self.profolio.keys():
                self.sell(stock, self.profolio[stock]['amount'], prices[stock])
            else:
                log(str(self.date) + ' -- Sorry, you don\'t have enough ' + stock)

    def add(self, stocks, prices):
        for stock in stocks:
            self.profolio[stock] = {
                'amount': 0,
                'price': prices[stock],
                'buy_price': prices[stock]
            }

    def add_n_sell(self, buys, sells, prices):
        self.sell_all(sells, prices)
        self.add(buys, prices)
        if len(self.profolio)>1:
            self.rebalance()

    def rebalance(self):
        each = int(self.get_total() / (len(self.profolio)-1))
        stocks = list(self.profolio.keys())
        for stock in stocks:
            if stock == 'freemoney':
                pass
            else:
                if self.get_money(stock) > each:
                    self.sell(stock, (self.get_money(stock) -
                              each)/self.profolio[stock]['price'], self.profolio[stock]['price'])
        for stock in stocks:
            if stock == 'freemoney':
                pass
            else:
                if self.get_money(stock) < each:
                    self.buy(stock, (each - self.get_money(stock))/self.profolio[stock]['price'],
                             self.profolio[stock]['price'])

    def get_money(self, stock):
        money = self.profolio[stock]['amount'] * self.profolio[stock]['price']
        return money

    def get_total(self):
        moneys = 0
        for stock in self.profolio.keys():
            money = self.get_money(stock)
            moneys += money
        return moneys
