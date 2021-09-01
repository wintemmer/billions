# 计算组合风险收益指标
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import plotly
import pandas as pd
import numpy as np


class analysier:
    # ploter
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
            fig.update_layout(title=self.get_name() + ": networth and long/short plot")
            fig.show()

    def get_name(self):
        if type(self.trader.peride) == str:
            if self.trader.peride == 'D':
                return self.trader.name + ' -- daily backtest'
            if self.trader.peride[0] == 'M':
                return self.trader.name + ' -- monthly backtest'
        if type(self.trader.peride) == int:
            return self.trader.name + ' -- ' + str(self.trader.peride) + ' days backtest'

    # summary
    def getReturn(self, nw):
        return (nw - nw.shift()) / nw.shift()

    def summary(self):
        nw = self.trader.networth
        ret = self.getReturn(nw)
        summaries = []
        for column in ret.columns:
            summary = self.tradeSummary(list(ret.index), list(
                ret[column]), column, freq='D')
            summaries.append(summary)
        if type(self.trader.longshort) != int:
            lsnw = self.trader.longshort
            lsret = self.getReturn(lsnw)
            for column in lsret.columns:
                summary = self.tradeSummary(list(lsret.index), list(
                    lsret[column]), column, freq='D')
                summaries.append(summary)
        self.summaries = pd.concat(summaries, axis=1)
        return self.summaries

    def plot_summary(self):
        df = self.summaries
        values = [df.index]
        for column in df.columns:
            values.append(df[column])
        fig = go.Figure(data=[go.Table(
            header=dict(values=[""] + list(df.columns),
                        fill_color='paleturquoise',
                        align='left'),
            cells=dict(values=values,
                       fill_color='lavender',
                       align='left'))
        ])
        fig.update_layout(title=self.get_name() + ": trade summary table")
        fig.show()

        # return summaries

    def tradeSummary(self, date, ret, group, freq='D'):
        df = pd.DataFrame({'date': date, 'ret': ret})
        df.sort_values(by='date', inplace=True)
        df.reset_index(drop=True, inplace=True)
        df.dropna(inplace=True)

        # 计算复利
        df['compound'] = np.cumprod(df['ret'] + 1)

        # 计算最大回撤
        df['max2here'] = df['compound'].expanding(1).max()
        df['dd2here'] = (df['compound'] / df['max2here']) - 1
        # df.to_excel("test.xlsx")

        # 计算最大回测开始和结束时间
        temp = df.sort_values(by='dd2here').iloc[0][['date', 'dd2here']]
        max_dd = temp['dd2here']
        end_dd = temp['date']
        start_dd = df[df['date'] <= end_dd].sort_values(
            by='compound', ascending=False).iloc[0]['date']

        # 计算判断数据频率
        if freq == 'D':
            n = 250
        elif freq == 'W':
            n = 52
        elif freq == 'M':
            n = 12
        else:
            print('请输入正确的时间频率，月：‘M’ 周：‘W’ 日：‘D’')

        rng = len(date)

        # 年化收益率
        annual_ret = pow(df['compound'].iloc[-1], n / rng) - 1

        # 波动率
        volatility = df['ret'].std() * np.sqrt(n)
        sharpe = annual_ret / volatility

        # 计算calmer
        calmar = annual_ret / abs(max_dd)

        return_risk_df = pd.DataFrame()
        return_risk_df["年化收益率"] = [str(round(annual_ret * 100, 2)) + '%']
        return_risk_df["年化波动率"] = [str(round(volatility * 100, 2)) + '%']
        return_risk_df["夏普比率"] = [round(sharpe, 3)]
        return_risk_df["最大回撤"] = [str(round(max_dd * 100, 2)) + '%']
        return_risk_df["calmar"] = [round(calmar, 3)]
        return_risk_df["回撤起始"] = [str(start_dd)[:10]]
        return_risk_df["回撤结束"] = [str(end_dd)[:10]]
        return_risk_df = return_risk_df.T
        return_risk_df.columns = [group]
        return return_risk_df
