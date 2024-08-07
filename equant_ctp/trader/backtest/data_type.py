# -*- coding: utf-8 -*-
"""
@author: Zed
@file: data_type.py
@time: 2024/7/31 12:12
@describe:自定义描述
"""


# OrderStatus
#  0 全部成交
#  1 部分成交，订单还在交易所撮合队列中
#  3 未成交，订单还在交易所撮合队列中
#  5 已撤销
#  a 未知-订单已提交交易所，未从交易所收到确认信息


# OnRtnOrder报单回报（订单表状态）
class OrderStatus:
    UNKNOWN = "Unknown"  # 未知-订单已提交交易所，未从交易所收到确认信息
    SUBMITTED = "Submitted"
    PARTIALLY_FILLED = "PartiallyFilled"  # 1 部分成交，订单还在交易所撮合队列中
    FILLED = "Filled"  # 0 全部成交
    UNFILLED = "UnFilled"  # 3 未成交，订单还在交易所撮合队列中
    CANCELED = "Canceled"  # 5已撤销
    PARTIALLY_CANCELED = "PartiallyCanceled"
    REJECTED = "Rejected"
    SUSPENDED = "Suspended"


# 成交回报
# 使用的函数是OnRtnTrade。
# 函数返回报单成交回报，每笔成交都会调用一次成交回报。成交回报中只包含合约，成交数量，价格等信息。
# 成交回报只包含该笔成交相关的信息，并不包含该笔成交之后投资者的持仓，资金等信息。函数
# ReqQryTradingAccount 用于查询投资者最新的资金状况。如保证金，手续费，持仓盈利，可用资金等。


def handle_order_status(order_status):
    if order_status == OrderStatus.SUBMITTED:
        print("订单已提交，等待成交。")
    elif order_status == OrderStatus.PARTIALLY_FILLED:
        print("订单部分成交，继续等待剩余部分成交。")
    elif order_status == OrderStatus.FILLED:
        print("订单全部成交。")
    elif order_status == OrderStatus.CANCELED:
        print("订单已撤销。")
    elif order_status == OrderStatus.PARTIALLY_CANCELED:
        print("订单部分成交，剩余部分已撤销。")
    elif order_status == OrderStatus.REJECTED:
        print("订单被拒绝，请检查订单参数。")
    elif order_status == OrderStatus.SUSPENDED:
        print("订单被挂起，请联系经纪商或交易所。")
    else:
        print("订单状态未知。")


class FeeInfo:
    def __init__(self, fee_base, fee_rate):
        self.fee_base = fee_base  # 基础手续费
        self.fee_rate = fee_rate  # 手续费率

    @property
    def data(self):
        return {'fee_base': self.fee_base,
                'fee_rate': self.fee_rate,
                }

    def __str__(self):
        return str(self.data)


class SymbolInfo:
    def __init__(self, limit_price_rate, trade_time, trade_unite, margin_rate, price_tick, t_n):
        # 品种信息：
        #   涨跌停幅度，交易时间段，交易单位（1手xxx份价格单位），保证金率（杠杆），价格最小变动， t+n
        self.limit_price_rate = limit_price_rate
        self.trade_time = trade_time
        self.trade_unite = trade_unite
        self.margin_rate = margin_rate
        self.price_tick = price_tick
        self.t_n = t_n

    @property
    def data(self):
        return {'limit_price_rate': self.limit_price_rate,
                'trade_time': self.trade_time,
                'trade_unite': self.trade_unite,
                'margin_rate': self.margin_rate,
                'price_tick': self.price_tick,
                't_n': self.t_n,
                }

    def __str__(self):
        return str(self.data)


class Order:
    # 产生的一笔累计型订单的数据结构：统一输入订单信息，成交订单信息
    def __init__(self, order_id, symbol, symbol_name, price, avg_price, quantity, direction, order_type, filled, value,
                 frozen_margin, frozen_quantity,
                 order_status, lever,
                 fee, frozen_fee, ret_rate, ret_value,
                 create_datetime, update_datetime,
                 create_timestamp,
                 update_timestamp, is_first, tag='', user_id=''):
        self.user_id = user_id
        self.order_id = order_id
        self.symbol = symbol
        self.symbol_name = symbol_name
        self.price = price  # 挂单价格
        self.avg_price = avg_price
        self.quantity = quantity
        self.filled = filled
        self.value = value
        self.frozen_margin = frozen_margin
        self.frozen_quantity = frozen_quantity
        self.direction = direction
        self.order_type = order_type
        self.order_status = order_status
        self.lever = lever
        self.fee = fee
        self.frozen_fee = frozen_fee
        self.ret_rate = ret_rate
        self.ret_value = ret_value
        self.create_datetime = create_datetime
        self.update_datetime = update_datetime
        self.create_timestamp = create_timestamp
        self.update_timestamp = update_timestamp
        self.is_first = is_first
        self.tag = tag

    @property
    def data(self) -> dict:
        return {'order_id': self.order_id, 'symbol': self.symbol, 'symbol_name': self.symbol_name, 'price': self.price,
                'avg_price': self.avg_price,
                'quantity': self.quantity, 'filled': self.filled, 'value': self.value,
                'frozen_margin': self.frozen_margin,
                'frozen_quantity': self.frozen_quantity, 'direction': self.direction, 'order_type': self.order_type,
                'order_status': self.order_status, 'lever': self.lever, 'fee': self.fee, 'frozen_fee': self.frozen_fee,
                'ret_rate': self.ret_rate, 'ret_value': self.ret_value,
                'create_datetime': self.create_datetime, 'update_datetime': self.update_datetime,
                'create_timestamp': self.create_timestamp, 'update_timestamp': self.update_timestamp,
                'tag': self.tag, 'user_id': self.user_id}

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return str(self.data)


class OrderTick:
    # 单笔成交订单tick
    def __init__(self, order_id, symbol, symbol_name, price, quantity, direction, order_type, value, lever,
                 fee,
                 datetime,
                 timestamp,
                 tag,
                 user_id

                 ):
        self.order_id = order_id
        self.symbol = symbol
        self.symbol_name = symbol_name
        self.price = price
        self.quantity = quantity
        self.value = value
        self.direction = direction
        self.order_type = order_type
        self.lever = lever
        self.fee = fee
        self.datetime = datetime
        self.timestamp = timestamp
        self.tag = tag
        self.user_id = user_id

    @property
    def data(self) -> dict:
        return {'order_id': self.order_id, 'symbol': self.symbol, 'symbol_name': self.symbol_name,
                'avg_price': self.price,
                'quantity': self.quantity, 'value': self.value,
                'direction': self.direction, 'order_type': self.order_type,
                'datetime': self.datetime, 'lever': self.lever, 'fee': self.fee,
                'timestamp': self.timestamp,
                'tag': self.tag, 'user_id': self.user_id}

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return str(self.data)


class OrderError:
    def __init__(self, error_id, order: Order, error_msg, datetime, timestamp):
        self.order_id = order.order_id
        self.error_id = error_id
        self.error_msg = error_msg
        self.order_tick = order
        self.datetime = datetime
        self.timestamp = timestamp

    def __str__(self):
        return {'error_id': self.error_id,
                'error_msg': self.error_msg,
                'order_id': self.order_id,
                'order_tick': self.order_tick,
                'datetime': self.datetime,
                'timestamp': self.timestamp,
                }

    def __repr__(self):
        return str(self)


class Position:
    def __init__(self, symbol, symbol_name, avg_price, avg_price_td, quantity, quantity_frozen, quantity_td, available,
                 quantity_yd, value,
                 value_init,
                 margin, lever,
                 direction,
                 create_time, update_time, fee, ret_rate, ret_value, float_ret_value, trade_unite, user_id):
        self.symbol = symbol
        self.symbol_name = symbol_name
        self.avg_price = avg_price
        self.avg_price_td = avg_price_td
        self.quantity = quantity
        self.quantity_frozen = quantity_frozen
        self.quantity_td = quantity_td
        self.quantity_yd = quantity_yd
        self.available = available
        self.value = value
        self.value_init = value_init
        self.margin = margin
        self.lever = lever
        self.direction = direction
        self.create_time = create_time
        self.update_time = update_time
        self.fee = fee
        self.ret_rate = ret_rate  # 中国期货不包括手续费计算，数字货币包括手续费计算
        self.ret_value = ret_value
        self.float_ret_value = float_ret_value  # 今日浮盈
        self.trade_unite = trade_unite
        self.user_id = user_id
        self.DIRECTION = {'LONG': 1, 'SHORT': -1}

    def update_position_by_order(self, avg_price, avg_price_td, quantity, quantity_frozen, available, margin,
                                 value_init, fee,
                                 update_time):
        # 订单更新影响成交均价，持仓数量，冻结数量，保证金，持仓初始价值，累计手续费
        self.avg_price = avg_price
        self.avg_price_td = avg_price_td
        self.quantity = quantity
        self.quantity_frozen = quantity_frozen
        self.available = available
        self.margin = margin
        self.value_init = value_init
        self.fee = fee
        self.update_time = update_time

    def update_position_by_trade_end(self, close):
        # 以收盘价作为下个交易日的今仓成交均价
        self.avg_price_td = close
        self.quantity_frozen = 0
        self.quantity_yd = self.quantity
        self.available = self.quantity

    def update_position_by_market(self, close):
        # 根据最新的行情更新仓位的收益表现
        self.value = close * self.quantity * self.trade_unite
        base_quantity = self.DIRECTION.get(self.direction) * self.trade_unite * self.quantity_td
        self.ret_value = (close - self.avg_price) * base_quantity
        self.ret_rate = self.ret_value / self.margin
        self.float_ret_value = (close - self.avg_price_td) * base_quantity

    def trade_end_callback(self, close):
        self.avg_price_td = close

    @property
    def data(self) -> dict:
        return {'symbol': self.symbol, 'symbol_name': self.symbol_name, 'avg_price': self.avg_price,
                'avg_price_td': self.avg_price_td,
                'quantity': self.quantity, 'available': self.available, 'quantity_frozen': self.quantity_frozen,
                'direction': self.direction,
                'margin': self.margin,
                'value_init': self.value_init, 'value': self.value, 'ret_rate': self.ret_rate,
                'lever': self.lever, 'fee': self.fee, 'ret_value': self.ret_value,
                'create_time': self.create_time, 'update_time': self.update_time,
                'float_ret_value': self.float_ret_value, 'user_id': self.user_id
                }

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return str(self.data)


class PositionManage:
    # 仓位经纪人
    def __init__(self):
        self.symbol_dict = {}
        self.symbol_margin_value_dict = {}  # 持仓保证金字典
        self.symbol_position_value_dict = {}  # 持仓价值字典
        self.symbol_float_ret_value_dict = {}  # 持仓浮动收益字典

    @property
    def symbols(self):
        return list(self.symbol_dict.keys())

    def __setitem__(self, key, value):
        self.symbol_dict[key] = value

    def __getitem__(self, item) -> Position:
        return self.symbol_dict.get(item)

    def __contains__(self, item):
        return True if item in self.symbol_dict else False

    def update_position_dict(self, symbol):
        self.symbol_margin_value_dict[symbol] = self.symbol_dict[symbol].margin
        self.symbol_position_value_dict[symbol] = self.symbol_dict[symbol].value
        self.symbol_float_ret_value_dict[symbol] = self.symbol_dict[symbol].float_ret_value


    def get_sum_margin(self):
        return sum(list(self.symbol_margin_value_dict.values()))

    def get_sum_value(self):
        return sum(list(self.symbol_position_value_dict.values()))

    def get_sum_float_value(self):
        return sum(list(self.symbol_float_ret_value_dict.values()))
    # 回测框架的position对象用polars实现


class Asset:
    def __init__(self, total_init, balance_free, margin, float_ret_value, frozen_margin, fee, frozen_fee,
                 value, ret_value,
                 ret_rate,
                 user_id, update_time):
        self.total_init = total_init
        self.balance_free = balance_free  # 实值余额可用部分
        self.frozen_margin = frozen_margin  # 限价挂单冻结资金
        self.frozen_fee = frozen_fee  # 限价挂单冻结手续费
        self.balance = self.balance_free + self.frozen_margin + self.frozen_fee  # 实值余额（包含了冻结保证金frozen_margin）  实值余额balance,手续费fee，冻结手续费
        self.balance_virtual = self.balance + float_ret_value  # 虚值余额=实值余额balance+ 今日浮盈 float_ret_value
        self.float_ret_value = float_ret_value
        self.margin = margin  # 锁定保证金=仓位初始保证金之和
        self.available = self.balance_free + (float_ret_value if float_ret_value < 0 else 0)  # 可用保证金
        self.fee = fee  # 今日交易累计手续费

        self.value = value  # 持仓市值
        self.total = self.balance_virtual + self.margin + self.frozen_margin + self.frozen_fee
        self.ret_rate = ret_rate
        self.ret_value = ret_value
        self.user_id = user_id
        self.update_time = update_time

    def trade_end_callback(self):
        # 收盘进行结算行为
        self.balance = self.balance_virtual + self.frozen_margin + self.frozen_fee
        self.balance_free = self.balance
        self.balance_virtual = self.balance
        self.float_ret_value = 0
        self.available = self.balance
        self.fee = 0
        self.frozen_margin = 0
        self.frozen_fee = 0
        self.total = self.balance_virtual + self.margin
        self.total_init = self.total
        self.ret_rate = 0
        self.ret_value = 0

    def update_asset_by_position(self, balance_free, margin, update_time):
        self.balance_free = balance_free
        self.balance = self.balance_free + self.frozen_margin + self.frozen_fee
        self.margin = margin
        self.update_time = update_time

    def update_asset_by_market(self, value, float_ret_value, update_time):
        self.value = value
        self.balance_virtual = self.balance + float_ret_value  # =实值可用balance+ 今日浮盈 float_ret_value
        self.float_ret_value = float_ret_value
        self.available = self.balance_free + (float_ret_value if float_ret_value < 0 else 0)
        self.total = self.balance_virtual + self.margin + self.frozen_margin + self.frozen_fee
        # 更新仓位同时也更新资产，当available < 0时，意味着没有足够的资金划转到保证金，此时发出爆仓信号，强制平仓
        self.ret_value = self.total - self.total_init
        self.ret_rate = self.ret_value / self.total_init

        self.update_time = update_time
        if self.available < 0:
            return '强制爆仓'

    # def update_asset_by_order(self, value, balance, margin, float_ret_value, frozen_margin, fee, frozen_fee,
    #                           update_time):
    #     self.value = value
    #     self.balance = balance
    #     self.balance_virtual = balance + float_ret_value  # =实值可用balance+ 今日浮盈 float_ret_value
    #     self.float_ret_value = float_ret_value
    #     self.margin = margin  # 锁定保证金=初始保证金之和
    #     self.available = (balance - frozen_margin - frozen_fee) + (float_ret_value if float_ret_value < 0 else 0)
    #     self.fee = fee  # 今日交易累计手续费
    #     self.frozen_margin = frozen_margin  # 限价挂单冻结资金
    #     self.frozen_fee = frozen_fee  # 限价挂单冻结手续费
    #     self.total = self.balance_virtual + self.margin + self.frozen_margin + self.frozen_fee
    #     # 更新仓位同时也更新资产，当available < 0时，意味着没有足够的资金划转到保证金，此时发出爆仓信号，强制平仓
    #     self.update_time = update_time
    #     if self.available < 0:
    #         return '强制爆仓'

    # def update_

    @property
    def data(self) -> dict:
        return {'total': self.total, 'available': self.available, 'balance_virtual': self.balance_virtual,
                'margin': self.margin, 'float_ret_value': self.float_ret_value,
                'balance': self.balance,
                'total_init': self.total_init,
                'fee': self.fee, 'frozen_margin': self.frozen_margin, 'frozen_fee': self.frozen_fee,
                'value': self.value, 'ret_rate': self.ret_rate, 'ret_value': self.ret_value,
                'update_time': self.update_time, 'user_id': self.user_id
                }

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return str(self.data)
