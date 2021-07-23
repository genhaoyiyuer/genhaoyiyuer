# 克隆自聚宽文章：https://www.joinquant.com/post/33590
# 标题：根据之前的ETF轮动策略，我把ETF列表改成了主题类ETF
# 作者：拿个扁但去挑土

# 克隆自聚宽文章：https://www.joinquant.com/post/32582
# 标题：无杠杆回撤更小的etf轮动-Clone-代码调整
# 作者：老船长不用桨

# 克隆自聚宽文章：https://www.joinquant.com/post/24321
# 标题：无杠杆，稳定盈利的etf轮动，06年开始3000%收益
# 作者：热爱大自然

# 克隆自聚宽文章：https://www.joinquant.com/post/24321
# 标题：无杠杆，稳定盈利的etf轮动，06年开始3000%收益
# 作者：热爱大自然

# 克隆自聚宽文章：https://www.joinquant.com/post/22857
# 标题：无杠杆，回撤更小的etf轮动
# 作者：智习

from jqdata import *
from enum import Enum
import talib
'''
原理：在8个种类的ETF中，持仓三个，ETF池相应的指数分别是
        '159915.XSHE' #创业板、
        '159949.XSHE' #创业板50
        '510300.XSHG' #沪深300
        '510500.XSHG' #中证500
        '510880.XSHG' #红利ETF
        '159905.XSHE' #深红利
        '510180.XSHG' #上证180
        '510050.XSHG' #上证50
持仓原则：
    1、对泸深指数的成交量进行统计，如果连续6（lag）天成交量小于7（lag0)天成交量的，空仓处理（购买货币基金511880 银华日利或国债 511010 ）
    2、13个交易日内（lag1）涨幅大于1的，并且“均线差值”大于0的才进行考虑。
    3、对符合考虑条件的ETF的涨幅进行排序，买涨幅最高的三个。
'''


def initialize(context):
    init_variables()
    set_params()
    set_backtest()
    run_daily(GenSignal, time='9:45')
    run_daily(ExecSell, time='13:00')
    run_daily(ExecBuy, time='14:40')
    run_daily(Output, time='15:00')

def after_code_changed(context):
    init_variables()
    set_params()

#1 设置参数
def set_params():
    # 设置基准收益
    set_benchmark('000300.XSHG')

    #是否动态改变大盘热度参考指标
    g.use_dynamic_target_market = False
    # 目标市场，大盘情绪监控
    #g.target_market = '000300.XSHG'
    g.target_market = '399001.XSHE'

    #闲时买入的标的
    g.empty_keep_stock = '511880.XSHG'
    #g.empty_keep_stock = '601318.XSHG'

    g.lag = 6  #大盘成交量连续跌破均线的天数，发出空仓信号
    g.lag0 = 7  #大盘成交量监控周期

    g.lag1 = 13  #比价均线周期
    g.lag2 = 13  #价格涨幅计算周期

    g.max_count = 3  #最多持仓标的数
    g.fac1 = 1 # 周期涨幅%
    g.fac2 = 0 # 均线差值%

    g.ETFList = {
            '399001.XSHE':'511880.XSHG',#银华锐进
            '399395.XSHE': '150197.XSHE',#有色B
            '399905.XSHE':'159902.XSHE',#中小板指
            '399975.XSHE':'150201.XSHE',#券商B
            '399975.XSHE': '512880.XSHG',#证券ETF
            '399632.XSHE': '159901.XSHE',  #深100etf
            '162605.XSHE':'162605.XSHE',#景顺鼎益
            '000016.XSHG': '510050.XSHG',#上证50
            '000010.XSHG': '510180.XSHG',  #上证180
            '000015.XSHG': '510880.XSHG',  #红利ETF
            '399324.XSHE': '159905.XSHE',  #深红利
            '399006.XSHE': '159915.XSHE',  #创业板
            '159949.XSHE': '159949.XSHE',  #创业板50
            '512760.XSHG': '512760.XSHG', #芯片
            '159994.XSHE':'159994.XSHE', #5G
            '159930.XSHE':'159930.XSHE', #能源
            '588000.XSHG':'588000.XSHG', #科创50
            '512720.XSHG':'512720.XSHG',#计算机
            '512810.XSHG':'512810.XSHG', #军工行业
            '159993.XSHE':'159993.XSHE',#龙头券商
            '159805.XSHE':'159805.XSHE',#传媒ETF
            '159825.XSHE':'159825.XSHE',#农业ETF
            '159929.XSHE':'159929.XSHE',#医药ETF
            '513990.XSHG':'513990.XSHG',  #港股宗超ETF
            '515790.XSHG':'515790.XSHG',  #光伏ETF
            '510410.XSHG':'510410.XSHG',#资源
            '159967.XSHE':'159967.XSHE',#创成长
            '515700.XSHG':'515700.XSHG',#新能车
            '510230.XSHG':'510230.XSHG',#金融
            '510410.XSHG':'510410.XSHG',#资源
         
            
            #'399006.XSHE':'150153.XSHE',#创业板B
            '000300.XSHG': '510300.XSHG',#沪深300
            '000905.XSHG': '510500.XSHG',  #中证500   
          
            }

    stocks_info = '\n股票池:\n'
    for security in g.ETFList.values():
        s_info = get_security_info(security)
        stocks_info += '【%s】%s 上市间间:%s\n' % (s_info.code, s_info.display_name,
                s_info.start_date)
    log.info(stocks_info)

def init_variables():
    g.emotion_rate = 0  #市场热度
    g.buy = []  #购买股票列表
    g.df = pd.DataFrame()
    return

#设置回测条件
def set_backtest():
    set_option('avoid_future_data', True)
    set_option('use_real_price', True)  #用真实价格交易
    log.set_level('order', 'error')
    # 将滑点设置为0
    set_slippage(FixedSlippage(0))
    # 设置手续费
    set_order_cost(OrderCost(open_tax=0, close_tax=0.001, \
            open_commission=0.0005, close_commission=0.0005,\
            close_today_commission=0, min_commission=5), type='stock')


# 信号定义
class Signal(Enum):
    Buy = 1
    Sell = 2


# 根据运行时数据，获取当日信号
def GenSignal(context):
    g.signal = get_signal(context)


def ExecSell(context):
    # 只处理卖出信号
    if Signal.Sell != g.signal:
        return

    # 是否持仓闲时标的
    beholdfree = False
    # 持仓
    for code in list(context.portfolio.positions.keys()):
        if (code == g.empty_keep_stock):
            beholdfree = True
            continue
        log.info('正在卖出 %s' % code)
        order_target_value(code, 0)

    if not beholdfree:
        log.info('买入闲时标的')
        order_target_value(g.empty_keep_stock,
                context.portfolio.available_cash)

def ExecBuy(context):
    if Signal.Buy != g.signal:
        return

    # 持仓
    holds = list(context.portfolio.positions.keys())
    holds.sort()
    if g.empty_keep_stock in holds:
        log.info("卖出闲时标的")
        order_target_value(g.empty_keep_stock, 0)
        holds = list()

    g.buy.sort()
    ratio = len(g.buy)
    cash = context.portfolio.total_value / ratio

    # 遍历持仓，记录平仓和调仓的操作
    close_op = dict()
    trans_op = dict()

    i = 0
    while i < len(holds):
        code = holds[i]
        if code not in g.buy:
            # 不在买入列表就平仓
            close_op[code] = 0
            holds.remove(code)
        else:
            # 在买入列表中判断调仓
            pos = context.portfolio.positions[code]
            if pos.value / cash > 1.5:
                trans_op[code] = cash
            i += 1

    # 遍历买入列表，记录新买入的标的
    open_op = dict()
    for code in g.buy:
        if code not in holds:
            open_op[code] = cash
            holds.append(code)

    # 执行操作，先平，再调，最后买入
    for op in close_op.items():
        code = op[0]
        value = op[1]
        log.info('正在平仓 %s' % code)
        order_target_value(code, value)

    for op in trans_op.items():
        code = op[0]
        value = op[1]
        log.info('正在调仓 %s' % code)
        order_target_value(code, value)

    for op in open_op.items():
        code = op[0]
        value = op[1]
        log.info('正在买入 %s' % code)
        order_target_value(code, value)

def Output(context):
    # 每日输出
    holds = list(context.portfolio.positions.keys())
    current_returns = 100 * context.portfolio.returns
    log.info("当前收益：%.2f%%，当前持仓%s" % (current_returns, holds))

#获取信号
def get_signal(context):
    i = 0  # 计数器初始化
    # 创建保持计算结果的DataFrame
    g.df = pd.DataFrame()
    g.buy = []
    for etfitem in g.ETFList.items():
        # 以指数计算交易信号，以基金进行交易
        idx = etfitem[0]
        security = etfitem[1]
        # 获取股票的收盘价
        close_data = attribute_history(idx, g.lag1, '1d', ['close'], df=False)
        # 获取股票现价
        current_data = get_current_data()
        current_price = current_data[idx].last_price
        # 获取股票的阶段收盘价涨幅
        cp_increase = (current_price / close_data['close'][g.lag1 - g.lag2] -
                1) * 100
        # 取得平均价格
        ma_n1 = close_data['close'].mean()
        # 计算前一收盘价与均值差值
        pre_price = (current_price / ma_n1 - 1) * 100
        g.df.loc[i, '指数代码'] = idx
        g.df.loc[i, '股票代码'] = security
        g.df.loc[i, '股票名称'] = get_security_info(security).display_name
        g.df.loc[i, '周期涨幅%'] = cp_increase
        g.df.loc[i, '均线差值%'] = pre_price
        i += 1

    # 对计算结果表格进行从大到小排序
    g.df = g.df.fillna(-100)
    g.df.sort_values(by='周期涨幅%', ascending=False, inplace=True)  # 按照涨幅排序
    g.df.reset_index(drop=True, inplace=True)  # 重新设置索引

    # 风控 大盘情绪 并计算市场热度
    risky_signal = EmotionMonitor(context)

    # 输出每日的信息
    info_msg = '\n行情统计,%s 热度%.2f%%: 风控信号:%d\n%s' % (
            g.target_market, g.emotion_rate, risky_signal, g.df)

    log.info(info_msg)
    #send_message(info_msg)

    if risky_signal < 0:
        # 大盘情绪不好发出空仓信号
        log.info('交易信号:大盘成交量持续%d天低均线，空仓' % -risky_signal)
        g.buy = []
        return Signal.Sell

    # 保留符合条件的标的;
    con1 = g.df['周期涨幅%'].map(lambda x: x >= g.fac1)
    con2 = g.df['均线差值%'].map(lambda x: x >= g.fac2)
    # 周期涨幅大于0.1 并且 均线差值大于 0
    g.df = g.df[con1 & con2]

    list_count = g.df.shape[0]
    if 0 == list_count:
        #均不符合买入条件
        log.info('交易信号:空仓')
        g.buy = []
        return Signal.Sell

    # 最多持仓数调整
    if list_count > g.max_count:
        list_count = g.max_count

    for i in range(list_count):
        g.buy.append(str(g.df.iloc[i, 1]))

    log.info('交易信号:持有 %s' % (g.buy))
    return Signal.Buy


# 大盘行情监控函数
def EmotionMonitor(context):
    # 动态改变大盘情绪的目标代码
    if g.use_dynamic_target_market:
        # 不用最高的来处理
        g.target_market = str(g.df.iloc[-1, 0])

    # 周期
    cycle = 30
    ah_df = attribute_history(g.target_market, cycle + g.lag0, '1d',
            ('volume'))
    volume = ah_df['volume'].values
    v_ma_lag0 = talib.MA(volume, g.lag0)
    # 对齐数据
    v_ma_lag0 = v_ma_lag0[g.lag0:]
    volume = volume[g.lag0:]

    vol = volume / v_ma_lag0 - 1
    # 计算市场热度
    g.emotion_rate = round(vol[-1] * 100, 2)
    for i in range(cycle):
        if vol[-1] >= 0:
            if vol[-1 - i] < 0:
                return i if (i >= 3) else 0
        else:
            if vol[-1 - i] >= 0:
                # 过去cycle日内，至少连续lag天，vol小于0
                return -i if (i >= g.lag) else 0
    return 1
