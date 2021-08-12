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
        fig.show()

    def plot_long_short(self):
        fig = px.line(self.trader.longshort)
        fig.show()

    def plot(self):
        fig = plotly.subplots.make_subplots(rows=1, cols=2)

        for column in self.trader.networth.columns:
            fig.append_trace(go.Scatter(
                x=self.trader.networth.index, y=self.trader.networth[column], name='benign'), 1, 1)
        for column in self.trader.longshort.columns:
            fig.append_trace(go.Scatter(
                x=self.trader.longshort.index, y=self.trader.longshort[column], name='benign'), 1, 2)

        fig.show()
