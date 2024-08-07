# -*- coding: utf-8 -*-
"""
@author: Zed
@file: match_order.py
@time: 2024/8/6 13:53
@describe:自定义描述
"""
from .data_type import Order, OrderTick, Position, PositionManage, SymbolInfo, FeeInfo, Asset, OrderError, OrderStatus
from ..md_api.data_type import Tick, Kline


# match_order(self, order: Order, quantity, asset: Asset, position_manage: PositionManage, fee_info: FeeInfo,
#                     lever,
#                     price=0, asks=None, bids=None, symbol_info: SymbolInfo = None, cal_method='tick', _timestamp=0)

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


def match_order(order: Order, quantity, asset: Asset, position_manage: PositionManage, fee_info: FeeInfo,
                lever,
                price=0, asks=None, bids=None, symbol_info: SymbolInfo = None, cal_method='tick', _timestamp=0):
    """

    :param order: 订单表
    :param quantity: 下单数量
    :param asset: 资产信息
    :param position_manage:仓位管理对象
    :param fee_info: 费率信息
    :param lever: 杠杆信息
    :param price: 最新成交价
    :param asks: 挂卖单
    :param bids: 挂买单
    :param symbol_info:标的信息
    :param cal_method: 撮合方式（基于xxx结构的）
    :param _timestamp: 当前时间戳
    :return:
    """
    # 根据订单表成交情况：
    # 1.计算逐笔
    # 2.计算对订单表的影响
    # 3.计算对仓位的影响
    # 4.计算对资产的影响

    # 1.计算逐笔:逐笔接收挂单信息和下单参数，根据撮合逻辑计算出成交均价，成交数量，逐笔信息回调给TradeRtn
    # 1.5根据这次撮合结果，统计成交均价，成交数量，根据开平仓计算消耗保证金，手续费
    # 2.对订单表的影响
    #     开仓
    #       做多
    #           挂单价格，挂单数量，下单方式，成交均价，成交数量，冻结保证金，冻结手续费，累计手续费
    #       做空
    #     平仓
    #       做多
    #           挂单价格，挂单数量，下单方式，成交均价，成交数量，冻结仓位数量，冻结手续费
    #       做空
    #
    #
    # 3.对仓位的影响
    #     开仓
    #         做多
    #             0.若未存在该仓位
    #                创建该仓位（仓位管理员）
    #                 1.结合旧的成交数量和成交均价，重新计算新的成交均价，持仓数量，今日开仓成交均价，今日开仓数量
    #                 2.累计手续费，持仓保证金，可用仓位数量，更新时间戳
    #         做空
    #               同上
    #     平仓
    #         做多
    #            计算持仓数量，今日开仓数量，累计手续费，持仓保证金，更新时间戳，冻结仓位数量，可用仓位数量
    #         做空
    #            同上
    # 根据计算结果，更新仓位
    # 仓位更新（基于订单）
    # 仓位更新（基于行情）
    #
    # 4.计算对资产的影响
    #   开仓
    #       做多
    #           计算对余额，冻结保证金，锁定保证金，冻结手续费，今日手续费的影响
    #       做空
    #   平仓
    #          计算对余额，冻结保证金，锁定保证金，冻结手续费，今日手续费的影响
    #
    #
    # 根据计算结果，更新资产
    # 资产更新（基于仓位）

    #
    direction0, direction1 = order.direction.split('_')
    if direction0 == 'OPEN':
        # 这里冻结挂单数量

        if order.order_type == 'LIMIT':
            if cal_method == 'kline':
                avg_price = price
                executed_quantity = quantity
                price_quantity_list = [[price, quantity]]
            else:
                if direction1 == 'LONG':
                    executed_quantity, avg_price, price_quantity_list = calculate_execution_limit(asks,
                                                                                                  quantity,
                                                                                                  order.price,
                                                                                                  direction='asks',
                                                                                                  is_first=order.is_first)
                else:
                    executed_quantity, avg_price, price_quantity_list = calculate_execution_limit(bids,
                                                                                                  quantity,
                                                                                                  order.price,
                                                                                                  direction='bids',
                                                                                                  is_first=order.is_first)
        else:
            if direction1 == 'LONG':
                executed_quantity, avg_price, price_quantity_list = calculate_execution(quantity, asks)
            else:
                executed_quantity, avg_price, price_quantity_list = calculate_execution(quantity, bids)
    else:
        # 这里冻结保证金

        if order.order_type == 'LIMIT':
            if cal_method == 'kline':
                avg_price = price
                executed_quantity = quantity
                price_quantity_list = [[price, quantity]]
            else:
                if direction1 == 'LONG':
                    executed_quantity, avg_price, price_quantity_list = calculate_execution_limit(bids,
                                                                                                  quantity,
                                                                                                  order.price,
                                                                                                  direction='bids',
                                                                                                  is_first=order.is_first)
                else:
                    executed_quantity, avg_price, price_quantity_list = calculate_execution_limit(asks,
                                                                                                  quantity,
                                                                                                  order.price,
                                                                                                  direction='asks',
                                                                                                  is_first=order.is_first)
        else:
            if direction1 == 'LONG':
                executed_quantity, avg_price, price_quantity_list = calculate_execution(quantity, asks)
            else:
                executed_quantity, avg_price, price_quantity_list = calculate_execution(quantity, bids)

    if executed_quantity == 0:
        status = OrderStatus.UNFILLED
    elif executed_quantity < quantity:
        status = OrderStatus.PARTIALLY_FILLED
    else:
        status = OrderStatus.FILLED
    # 1.5根据这次撮合结果，统计成交均价，成交数量，根据开平仓计算消耗保证金，手续费
    if not lever:
        lever = 1 / symbol_info.margin_rate

    position = position_manage[order.symbol]

    order_value = executed_quantity * avg_price * symbol_info.trade_unite
    fee = order_value * fee_info.fee_rate
    if direction0 == 'OPEN':

        change_margin = order_value / lever
        change_value = order_value
    else:

        change_margin = position.margin * executed_quantity / position.quantity
        change_value = position.value_init * executed_quantity / position.quantity

    # 2.对订单表的影响
    #     开仓
    #       做多
    #           挂单价格，挂单数量，下单方式，——————成交均价，成交数量，冻结保证金（挂单价格*剩余数量*每手成交单位/lever），冻结手续费(挂单价格*挂单数量*fee_rate)，累计手续费
    #       做空

    #     平仓
    #       做多
    #           挂单价格，挂单数量，下单方式，——————成交均价，成交数量，冻结仓位数量，累计手续费
    #       做空
    order.fee += fee
    if direction0 == 'OPEN':
        old_value = order.filled * order.avg_price
        new_value = old_value + order_value
        new_avg_price = order_value / new_value * avg_price + old_value / new_value * order.avg_price
        order.avg_price = new_avg_price
        # 计算累计成交均价，累计成交数量，
        order.filled += executed_quantity
        # 计算冻结保证金
        if order.order_type == 'LIMIT':
            order.frozen_quantity = order.quantity - executed_quantity  # 剩余未完成即冻结数量
            order.frozen_margin = order.price * order.frozen_quantity * symbol_info.trade_unite / lever
            order.frozen_fee = order.frozen_margin * lever * fee_info.fee_rate

    else:
        # 平仓计算冻结仓位，影响持仓可用仓位计算
        old_value = order.filled * order.avg_price
        new_value = old_value + order_value
        new_avg_price = order_value / new_value * avg_price + old_value / new_value * order.avg_price
        order.avg_price = new_avg_price
        # 计算累计成交均价，累计成交数量，
        order.filled += executed_quantity
        if order.order_type == 'LIMIT':
            order.frozen_quantity = order.quantity - executed_quantity  # 剩余未完成即冻结数量

    # 3.对仓位的影响
    #     开仓
    #         做多
    #             0.若未存在该仓位
    #                创建该仓位（仓位管理员）
    #                 1.结合旧的成交数量和成交均价，重新计算新的成交均价，持仓数量，今日开仓成交均价，今日开仓数量
    #                 2.累计手续费，持仓保证金，更新时间戳
    #         做空
    #               同上
    #     平仓
    #         做多
    #            计算持仓数量，今日开仓数量，累计手续费，持仓保证金，更新时间戳，冻结仓位数量，可用仓位数量
    #         做空
    #            同上
    # 根据计算结果，更新仓位
    # 仓位更新（基于订单）
    # 仓位更新（基于行情）
    #     if direction0 == 'OPEN':
    #
    #         change_margin = order_value / lever
    #     else:
    #
    #         change_margin = position.margin * executed_quantity / position.quantity

    if direction0 == 'OPEN':

        if order.symbol not in position_manage:
            # 实例化一个新的position
            position = Position(order.symbol, order.symbol_name, 0, 0, 0, 0, 0,
                                0, 0, 0, 0, 0, lever, direction1, _timestamp, _timestamp,
                                0, 0, 0, 0, symbol_info.trade_unite, order.user_id)

        new_value = position.value_init + order_value
        new_avg_price = order_value / new_value * avg_price + position.value_init / new_value * position.avg_price
        avg_price_today = position.avg_price_td

        value_today = avg_price_today * position.quantity_td
        new_value_today = value_today + order_value
        new_avg_price_today = value_today / new_value_today * avg_price_today + order_value / new_value_today * avg_price

        position.avg_price = new_avg_price
        position.avg_price_td = new_avg_price_today
        position.quantity += executed_quantity
        position.quantity_td += executed_quantity
        position.available = position.quantity - position.quantity_frozen
        position.margin += change_margin
        position.value_init += change_value
        position.fee += fee
        position.update_time = _timestamp
    else:
        #   计算持仓数量，今日开仓数量，累计手续费，持仓保证金，更新时间戳，冻结仓位数量(通过待撮合订单列表统计计算)，可用仓位数量
        position.margin -= change_margin
        position.value_init -= change_value
        position.quantity -= executed_quantity
        if order.order_type == 'LIMIT':
            position.quantity_frozen -= executed_quantity
        position.quantity_td -= executed_quantity
        position.available = position.quantity - position.quantity_frozen
        position.fee += fee
        position.update_time = _timestamp
    position.update_position_by_market(avg_price)

    if direction0 == 'OPEN':
        #     def update_asset_by_position(self, balance_free,frozen_margin,frozen_fee, margin, update_time):
        #         self.balance_free = balance_free
        #         self.margin = margin
        #         self.update_time = update_time
        if order.order_type == 'LIMIT':
            asset.frozen_margin -= change_margin
            asset.frozen_fee -= fee
        # asset.balance_free -= (change_margin + fee)
        #
        # asset.margin += change_margin
        # asset.update_time = _timestamp
        # balance_free, margin, update_time
        asset.update_asset_by_position(asset.balance_free - (change_margin + fee), asset.margin + change_margin,
                                       _timestamp)
        # asset.balance_free -= (change_margin + fee)
    else:
        # asset.balance_free += (change_margin - fee)
        # asset.margin -= change_margin
        # asset.update_time = _timestamp
        asset.update_asset_by_position(asset.balance_free + change_margin + fee, asset.margin - change_margin,
                                       _timestamp)

    # 4.计算对资产的影响
    #   开仓
    #       做多
    #           计算对余额，冻结保证金，锁定保证金，冻结手续费，今日手续费的影响
    #       做空
    #   平仓
    #          计算对余额，冻结保证金，锁定保证金，冻结手续费，今日手续费的影响
    #
    #
    order.is_first = False

    # 后续收尾工作：
    # 1.逐笔信息price_quantity_list推送至 逐笔回调函数
    # 2.市价单剩余未成交直接撤单
    # 3.根据这次交易情况，判断是否完成，是否为第一次挂单且为限价，更新order状态并更新进wait_for_limit_order中
    return order, position, asset, price_quantity_list



