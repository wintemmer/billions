import pandas as pd
import plotly
import plotly.express as px
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go


class theploter:
    def __init__(self, trader):
        self.trader = trader

    def plot_networth(self):
        fig = px.line(self.trader.networth)
        fig.update_layout(title=self.get_name())
        fig.show()

    def plot_long_short(self):
        fig = px.line(self.trader.longshort)
        fig.update_layout(title=self.get_name())
        fig.show()

    def plot(self):
        if type(self.trader.longshort) == int:
            self.plot_networth()
        else:
            fig = plotly.subplots.make_subplots(rows=1, cols=2)

            for column in self.trader.networth.columns:
                fig.append_trace(go.Scatter(
                    x=self.trader.networth.index, y=self.trader.networth[column], name=column), 1, 1)
            for column in self.trader.longshort.columns:
                fig.append_trace(go.Scatter(
                    x=self.trader.longshort.index, y=self.trader.longshort[column], name=column), 1, 2)
            fig.update_layout(title=self.get_name())
            fig.show()

    def get_name(self):
        if type(self.trader.peride) == str:
            if self.trader.peride == 'D':
                return self.trader.name + ' -- ' + 'daily backtest'
            if self.trader.peride[0] == 'M':
                return self.trader.name + ' -- ' + 'monthly backtest'
        if type(self.trader.peride) == int:
            return self.trader.name + ' -- ' + str(self.trader.peride) + ' days backtest'
