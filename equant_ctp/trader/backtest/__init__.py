# -*- coding: utf-8 -*-
"""
@author: Zed
@file: __init__.py
@time: 2024/7/31 12:08
@describe:自定义描述
"""
from .data_type import Order, OrderTick, Position, PositionManage, SymbolInfo, FeeInfo, Asset, OrderError, OrderStatus
from ..md_api.data_type import Tick, Kline
from .match_order import match_order


# info = {
#
#         "userid": "30804460",  # 089131
#         "password": "mmbmd2020",  # 350888
#         "brokerid": '9080',
#         "auth_code":"9GYECRSBCAC8M2H0",
#         "appid": "client_fastquant_1.0.0",
#         "td_address": "tcp://61.186.254.135:42205",
#         "product_info": "v6.6.1_p1cp_tradeapi",
#         "md_address": "tcp://61.186.254.135:42213"
#
#         # tcp://122.51.136.165:20002 #7*24
#
#     }

def calculate_execution(orders, quantity):
    """
    根据下单数量计算逐笔成交价格和数量，用于市价成交

    :param orders: List of [price, quantity] pairs representing the order book (asks or bids)
    :param quantity: The quantity to be executed
    :return: List of [price, quantity] pairs representing the executed orders
    """
    price_quantity_list = []
    remaining_quantity = quantity

    executed_quantity = 0
    for price, available_quantity in orders:
        if remaining_quantity <= 0:
            break
        # 确定本次成交的数量
        _executed_quantity = min(remaining_quantity, available_quantity)
        price_quantity_list.append([price, _executed_quantity])

        # 减少剩余需要成交的数量
        remaining_quantity -= _executed_quantity
        executed_quantity += _executed_quantity

    avg_price = sum([qty / executed_quantity * price for price, qty in price_quantity_list])
    return executed_quantity, avg_price, price_quantity_list


def calculate_execution_limit(orders, quantity, order_price, direction='bids', is_first=True):
    """
    计算在给定价格下可以执行的总数量。

    :param is_first: 只有第一次未挂单产生的交易相当于市价成交，只有成功挂单后才是限价成交，两者计算撮合成交的价格不一样
    :param direction: order属于bids（卖方，则quantity方向是买单）还是asks（买方，则quantity方向是卖单）
    :param orders: 挂单列表，每个元素是一个列表，包含价格和数量，例如 [[price0, quantity0], [price1, quantity1], ...]
    :param quantity: 需要成交的总数量
    :param order_price: 限价单的价格
    :return: 可以在给定价格下执行的总数量
    """

    executed_quantity = 0
    price_quantity_list = []
    if direction == 'asks':
        for price, qty in orders:
            # 对于买单，订单价格应 <= 限价单价格；对于卖单，订单价格应 >= 限价单价格
            if price <= order_price:
                if executed_quantity + qty >= quantity:
                    if is_first:
                        price_quantity_list.append([price, qty])
                    else:
                        price_quantity_list.append([order_price, qty])
                    return quantity
                executed_quantity += qty
                if is_first:
                    price_quantity_list.append([price, qty])
                else:
                    price_quantity_list.append([order_price, qty])
    else:
        for price, qty in orders:
            # 对于买单，订单价格应 <= 限价单价格；对于卖单，订单价格应 >= 限价单价格
            if price >= order_price:
                if executed_quantity + qty >= quantity:
                    if is_first:
                        price_quantity_list.append([price, qty])
                    else:
                        price_quantity_list.append([order_price, qty])

                    return quantity
                executed_quantity += qty
                if is_first:
                    price_quantity_list.append([price, qty])
                else:
                    price_quantity_list.append([order_price, qty])
    avg_price = sum([qty / executed_quantity * price for price, qty in price_quantity_list])
    return executed_quantity, avg_price, price_quantity_list


class Account:
    def __init__(self, userid, password):
        self.userid = userid
        self.password = password
        self.position = {}
        self.asset = {}
        self.ret_list = {}  # 累计收益率
        self.backdrop = {}  # 累计回撤


class OrderMatch:
    # 根据买卖单进行交易撮合
    def __init__(self, order_result_callback, trade_result_callback, position_manage: PositionManage, asset: Asset,
                 match_mode='fast',
                 symbol_info_dict: dict = None, yd_close_dict: dict = None):
        self.position_manage = position_manage
        self.asset = asset
        self._wait_march_order_dict = {}  # 待撮合的订单列表，key为标的名，value为订单信息Order类
        self._order_result_callback = order_result_callback  # 订单回调
        self._trade_result_callback = trade_result_callback
        self.match_mode = match_mode  # 1. fast:当前这笔订单通过当前已获取行情进行撮合 2. slow:当前这笔订单通过下一笔待生成的行情进行撮合,保存该笔订单信息，直接跳过检查和撮合阶段即可
        self.symbol_info_dict = symbol_info_dict
        self.symbol_fee_info_dict = {}
        self.yd_close_dict = yd_close_dict  # his模式下必须添加yd_close

    def wait_match_order_by_live(self):
        # 待撮合的订单
        #     这个地方很重要，如果是即时撮合模式，用户在下单用的行情即用户当前所接收的行情作为撮合数据；
        #   如果是延迟撮合，则更加符合现实逻辑，则等待下一笔行情到来时触发撮合，这直接影响用户交易策略编写的方式

        pass

    def wait_match_order_by_his(self):
        # 待撮合的订单
        #     这个地方很重要，如果是即时撮合模式，用户在下单用的行情即用户当前所接收的行情作为撮合数据；
        #   如果是延迟撮合，则更加符合现实逻辑，则等待下一笔行情到来时触发撮合，这直接影响用户交易策略编写的方式

        pass

    def callback_order_live(self, tick: Tick):
        # 基于tick数据的撮合
        # order = self._wait_march_order_dict[tick.symbol]

        if tick.symbol not in self._wait_march_order_dict:
            return
        for order_id, order in self._wait_march_order_dict[tick.symbol].items():

            order.is_first = False
            # if order.direction.split('_')[]
            # 根据方向确定price, asks, bids
            asks = tick.asks
            bids = tick.bids
            price = 0  # 有price选择用基于close的撮合模式，否则用tick撮合
            symbol_info = self.symbol_info_dict[tick.symbol]
            fee_info = self.symbol_info_dict[tick.symbol]
            quantity = order.quantity - order.filled
            # self.order_check(order, quantity, self.asset, self.position_manage, fee_info, order.lever, price, asks, bids,
            #                  symbol_info,
            #                  tick.yd_close, cal_method='tick')
            order, position, asset, price_quantity_list = match_order(order, quantity, self.asset, self.position_manage,
                                                                      fee_info, order.lever, price,
                                                                      asks, bids,
                                                                      symbol_info,
                                                                      cal_method='tick', _timestamp=tick.timestamp)
            finish_quantity = order.quantity - order.filled
            if finish_quantity == quantity:
                return

            if order.quantity == order.filled:
                # self._order_result_callback(order)
                del self._wait_march_order_dict[tick.symbol][order.order_id]

                self._order_result_callback(order.order_id, order.symbol, order, tick.timestamp)
                self._trade_result_callback(order.order_id, order.symbol, price_quantity_list, tick.timestamp)

            else:
                self._wait_march_order_dict[tick.symbol][order.order_id] = order
                self._order_result_callback(order.order_id, order.symbol, order, tick.timestamp)

    #         # 后续收尾工作：
    #     # 1.逐笔信息price_quantity_list推送至 逐笔回调函数
    #     # 2.市价单剩余未成交直接撤单
    #     # 3.根据这次交易情况，判断是否完成，是否为第一次挂单且为限价，更新order状态并更新进wait_for_limit_order中
    def callback_order_trade_end(self, timestamp):
        # ps:特指早盘收盘为结算时间，其中郑商所没有早盘集合竞价
        # 且8:59:00确定早盘集合竞价，>=此时间才可以进行撮合交易，<=此时间可以撤单挂单
        # 交易日结束，订单将进行删除，返还冻结资金和冻结仓位
        #
        # self._wait_march_order_dict：所有订单将
        for symbol, order_dict in self._wait_march_order_dict.items():
            for order_id, order in order_dict.items():
                order.order_status = OrderStatus.CANCELED
                self._order_result_callback(order.order_id, order.symbol, order, timestamp)
        self._wait_march_order_dict = {}

    def callback_order_his(self, kline: Kline):
        # 基于到期k线数据的撮合
        order_dict = self._wait_march_order_dict.get(kline.symbol)
        if not order_dict:
            return

        for order_id, order in order_dict.items():
            order.is_first = False
            # if order.direction.split('_')[]
            # 根据方向确定price, asks, bids
            asks = []
            bids = []
            price = kline.close  # 有price选择用基于close的撮合模式，否则用tick撮合
            symbol_info = self.symbol_info_dict[kline.symbol]
            fee_info = self.symbol_info_dict[kline.symbol]
            quantity = order.quantity - order.filled  # 待撮合量

            order, position, asset, price_quantity_list = match_order(order, quantity, self.asset, self.position_manage,
                                                                      fee_info, order.lever, price,
                                                                      asks, bids,
                                                                      symbol_info,
                                                                      cal_method='tick', _timestamp=kline.timestamp)
            finish_quantity = order.quantity - order.filled
            if finish_quantity == quantity:
                return

            if order.quantity == order.filled:
                # self._order_result_callback(order)
                # 订单交易完毕，删除该订单表，可以在此处做保存
                del self._wait_march_order_dict[kline.symbol][order.order_id]
                self._order_result_callback(order.order_id, order.symbol, order, kline.timestamp)
                self._trade_result_callback(order.order_id, order.symbol, price_quantity_list, kline.timestamp)

            else:
                self._wait_march_order_dict[kline.symbol][order.order_id] = order
                self._order_result_callback(order.order_id, order.symbol, order, kline.timestamp)

    #         # 后续收尾工作：
    #     # 1.逐笔信息price_quantity_list推送至 逐笔回调函数
    #     # 2.市价单剩余未成交直接撤单
    #     # 3.根据这次交易情况，判断是否完成，是否为第一次挂单且为限价，更新order状态并更新进wait_for_limit_order中

    #     order: Order, quantity, asset: Asset, position_manage: PositionManage, fee_info: FeeInfo,
    #                     lever_info,
    #                     price=0, asks=None, bids=None, symbol_info: SymbolInfo = None, cal_method='tick', _timestamp=0

    def order_check(self, order: Order, quantity, asset: Asset, position_manage: PositionManage, fee_info: FeeInfo,
                    lever_info,
                    price=0, asks=None, bids=None, symbol_info: SymbolInfo = None, yd_close=None, cal_method='tick',
                    _timestamp=0, _datetime='2023-05-08 09:35:15.156'):
        # 撮合检查：接收下单信息，仓位，资产，交易日历，交易时间信息，手续费信息，保证金规则等信息，判断这笔交易所否能够预期成交
        #
        # error_id, order_tick: OrderTick, error_msg, datetime, timestamp):
        if type(quantity) != int or quantity < 0:
            return None, OrderError(-1005, order,
                                    error_msg=f'下单数量错误:下单数量{quantity}异常',
                                    datetime=_datetime, timestamp=_timestamp)

        if order.symbol not in self.symbol_info_dict:
            return None, OrderError(-1001, order, error_msg=f'合约名称错误:合约{order.symbol}不存在',
                                    datetime=_datetime, timestamp=_timestamp)

        if order.order_type == 'LIMIT':
            # 价格不是按照最小tick跳动1

            if cal_method == 'kline':
                set_price = price
            else:
                if asks:
                    set_price = asks[0][0]
                else:
                    set_price = bids[0][0]

            if (order.price - set_price) % symbol_info.price_tick == 0:
                pass
                # print("挂单价格是正确的")
            else:
                return None, OrderError(-1001, order,
                                        error_msg=f'挂单价格错误:挂单价格{order.price}不满足最小tick变动:{symbol_info.price_tick},当前参考价格:{set_price}',
                                        datetime=_datetime, timestamp=_timestamp)
            if not (1 - symbol_info.limit_price_rate[1]) * yd_close <= order.price <= (
                    1 + symbol_info.limit_price_rate[0]) * yd_close:
                return None, OrderError(-1004, order,
                                        error_msg=f'挂单价格错误:挂单价格{order.price}超出限价区间:{(1 - symbol_info.limit_price_rate[1]) * yd_close}-{(1 + symbol_info.limit_price_rate[0]) * yd_close}',
                                        datetime=_datetime, timestamp=_timestamp)

        order_time = _datetime.split(' ')[1].split('.')[0].replace(':', '')  # 2023-05-08 09:35:15.156

        order_time = int(order_time)
        for t in symbol_info.trade_time:
            if not (t[0] < order_time < t[1]):
                return None, OrderError(-1003, order,
                                        error_msg=f'交易时间错误:合约{order.symbol}不在交易时段:{_datetime}',
                                        datetime=_datetime, timestamp=_timestamp)
        """
        检查开仓花费
        """
        direction0, direction1 = order.direction.split('_')
        if order.order_type == 'LIMIT':

            value = order.price * quantity * symbol_info.trade_unite
        else:
            # 市价计算
            if cal_method == 'kline':
                value = price * quantity * symbol_info.trade_unite
            else:
                if direction1 == 'LONG':

                    pass
                    # executed_quantity, avg_price, price_quantity_list = calculate_execution(quantity, bids)
                else:
                    pass
                    # executed_quantity, avg_price, price_quantity_list = calculate_execution(quantity, asks)
                # value = 0
                # for price, qty in executed_orders:
                #     value += price + qty
                #
                #     print(f"价格: {price}, 数量: {qty}")

                value = price * quantity * symbol_info.trade_unite

        if not lever_info:
            lever_info = 1 / symbol_info.margin_rate

        margin = value / lever_info
        fee = fee_info.fee_base + fee_info.fee_rate * value

        if direction0 == 'OPEN':
            total_cost = margin + fee
            if asset.available < total_cost:
                return None, OrderError(-1002, order,
                                        error_msg=f'可用资金错误:可用资金{asset.available}<开仓花费{total_cost}',
                                        datetime=_datetime, timestamp=_timestamp)

        if order.symbol in self.position_manage:
            if direction1 != self.position_manage[order.symbol].direction:
                return None, OrderError(-1008, order,
                                        error_msg=f'开仓方向错误:下单平仓方向{direction1}！=持仓方向{self.position_manage[order.symbol].direction}',
                                        datetime=_datetime, timestamp=_timestamp)
            if direction0 == 'OPEN':
                pass

            else:
                # 可用仓位错误，没有足够的仓位平仓9
                position = self.position_manage[order.symbol]
                if quantity > (position.quantity - position.quantity_frozen):
                    return None, OrderError(-1009, order,
                                            error_msg=f'平仓错误:可用仓位错误，{order.symbol}没有足够的仓位({position.quantity - position.quantity_frozen})平仓({quantity})',
                                            datetime=_datetime, timestamp=_timestamp)

                if order.order_type == 'LIMIT':
                    pass
                else:
                    pass
        else:
            if direction0 == 'CLOSE':
                return None, OrderError(-1007, order, error_msg=f'平仓错误:不存在该品种仓位:{order.symbol}',
                                        datetime=_datetime, timestamp=_timestamp)
            else:
                pass

        # 可用资金不足2           √
        # 非交易时间3             √
        # 超出涨跌停限价4          √
        # 数量错误5               √
        #

        # 持仓情况下：
        #   交易方向错误：不支持双向持仓6    √
        # 平仓：
        #   不存在该仓位7              √
        #   方向错误，错位平仓long仓位short平仓8        √
        #   可用仓位错误，没有足够的仓位平仓9             √

        # 如果是slow，则直接保存信息并跳过（wait_for_slow_order）

        order, position, asset, price_quantity_list = match_order(order, quantity, asset, position_manage, fee_info,
                                                                  lever_info, price, asks, bids,
                                                                  symbol_info, cal_method=cal_method,
                                                                  _timestamp=_timestamp)
        # 撮合完后，     # 后续收尾工作：
        #     # 1.逐笔信息price_quantity_list推送至 逐笔回调函数
        #     # 2.市价单不加入wait_for_limit,且订单处于完成状态
        #     # 3.根据这次交易情况，判断是否完成，是否为第一次挂单且为限价，更新order状态并更新进wait_for_limit_order中

    def cancel_order(self, symbol, order_id):
        # 输入symbol，无order_id下，自动将全部id都撤销，输入symbol，有order_id下，撤销该笔
        pass

    def stop_win(self):
        # 止盈单
        pass

    def stop_loss(self):
        # 止损单
        pass


class RestApi:
    def __init__(self):
        pass

    def callback_trade_start(self):
        # 事件触发函数:交易日开始
        pass

    def callback_trade_end(self):
        # 事件触发函数:交易日结束
        pass

    def trade_start(self):
        pass

    def create_order(self):
        pass

    def cancel_order(self):
        pass

    def get_asset(self):
        # 请求资产更新并返回结果
        pass

    def get_position(self):
        # 请求仓位更新并返回结果
        pass

    def get_symbol_info(self):
        # 获取合约信息
        pass
