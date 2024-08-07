# -*- coding: utf-8 -*-
"""
@author: Zed
@file: trader.py
@time: 2024/8/5 10:37
@describe:自定义描述
"""


class StrategyBase:

    def __init__(self):
        self.subscribe_dict = {}

    def subscribe(self, *args, **kwargs):
        self.subscribe_dict = {}


class Strategy(StrategyBase):

    def sys_start(self):
        self.subscribe({'1m': self.trade_callback})

    def trade_callback(self):
        pass


if __name__ == '__main__':

    pass
    # strategy=Strategy()
    # strategy.subscribe({'1m':strategy.trade_callback,})
    # equant_backtest(strategy,login_info={},config_xxx=xxx).run()
    # equant_simulate(strategy,login_info={},config_xxx=xxx).run()
    # equant_live(strategy,login_info={},config_xxx=xxx).run()
