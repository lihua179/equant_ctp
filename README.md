# equant_ctp
易宽ctp，用于解决期货实盘，模拟盘，回测，行情运维以及本地存储等量化问题


解耦：将每个模块尽可能单独拆解，拥有更高效的代码拓展性
接口一致：实盘模拟盘回测所有交易接口，行情接口，保持一致，同时允许不同的数据结构作为行情数据源，兼顾开发效率和拓展空间
市场拓展：将股票，数字货币等不同交易市场接口进行统一，相同策略代码，不同配置参数，低成本跨市场回测交易
工具包：为行情数据进行任意频率的拟合，提供统计，特征加工等因子生成工具，成为创建α策略的充分条件
可视化：基于订单流，行情的可视化，高效精准复盘
