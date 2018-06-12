# coding=utf-8
# from fcoin import Fcoin
# if python3 use fcoin3
import json
from fcoin3 import Fcoin
import threading
import time
from config import api_key
from config import api_secret

# 初始化
fcoin = Fcoin()


# 查询账户余额
def get_balance_action(this_symbol):
    balance_info = fcoin.get_balance()
    print(json.dumps(balance_info))
    if this_symbol == 'btc':
        balance = balance_info['data'][2]
        label = 'BTC'
    elif this_symbol == 'eth':
        balance = balance_info['data'][4]
        label = 'ETH'
    elif this_symbol == 'usdt':
        balance = balance_info['data'][8]
        label = 'USDT'
    elif this_symbol == 'ft':
        balance = balance_info['data'][9]
        label = 'FT'
    elif this_symbol == 'zip':
        balance = balance_info['data'][10]
        label = 'ZIP'

    print(label, '账户余额', balance['balance'], '可用', balance['available'], '冻结', balance['frozen'])
    return balance['available']


# 获取订单列表
def get_order_list(this_symbol, this_states):
    order_list = fcoin.list_orders(symbol=this_symbol, states=this_states)
    if this_states == filled:
        print('已成交订单列表：')
    elif this_states == submitted:
        print('未成交订单列表：')
    for order in order_list['data']:
        print('订单ID', order['id'], '挂单价格', order['price'], '挂单数量', order['amount'], '方向', order['side'])
        if this_states == submitted:
            print('开始取消订单')
            cancel_order_action(order['id'])


# 获取订单列表第一个订单
def get_order_list_first(this_symbol, this_states):
    order_list = fcoin.list_orders(symbol=this_symbol, states=this_states)
    if 'data' in order_list and len(order_list['data']):
        order_item = order_list['data'][0]

        if order_item:
            order_price = float(order_item['price'])
            if this_states == submitted:
                print('发现未成交订单，尝试先取消委托订单')
                cancel_order_action(order_item['id'])
            elif this_states == filled:
                now_price = get_ticker(symbol)
                if order_item['side'] == 'buy':
                    print('尝试卖出')
                    if now_price >= order_price:
                        print('现价大于等于上一笔买入价，尝试卖出')
                        sell_action(symbol, now_price, amount)
                    else:
                        result=fcoin.get_market_ticker(symbol)
                        old_price=now_price
                        size=old_price-now_price
                        print('size {0}'.format(size))
                        if size>10:
                            print('size 太大 不卖 buyprice{0} sellprice{1}'.format(old_price,now_price))
                        else:
                            now_price=result['data']['ticker'][2]
                            print('现价小于上一笔买入价，不操作 取最近买单卖出 价格{0}'.format(now_price))
                            sell_action(symbol, now_price, amount)

                elif order_item['side'] == 'sell':
                    # 这里只判断卖出价格高于买入价格
                    print('尝试买入')
                    if now_price <= order_price or True:
                        print('现价小于等于上一笔卖出价，尝试买入')
                        buy_action(symbol, now_price, amount)
                    else:
                        print('现价大于上一笔卖出价，不操作')
    else:
        if this_states == submitted:
            print('没有发现未成交订单')
            get_order_list_first(this_symbol, filled)
        elif this_states == filled:
            now_price = get_ticker(symbol)
            print('初次现价买入')
            buy_action(symbol, now_price, amount)


# 查询订单
def check_order_state(this_order_id):
    check_info = fcoin.get_order(this_order_id)
    return check_info['data']


# 买操作
def buy_action(this_symbol, this_price, this_amount):
    eth_money=get_balance_action(base_action)
    sum=getCountbyBase(eth_money,this_price)

    buy_result=''
    while(buy_result ==''):
        try:
            buy_result = fcoin.buy(this_symbol, this_price, sum)
        except Exception as e:
            print(e)
            time.sleep(1)

    print(buy_result)
    buy_order_id = buy_result['data']
    if buy_order_id:
        print('买单', this_price, '价格成功委托', '订单ID', buy_order_id)

    # 输出订单信息
    # print(fcoin.get_order(buy_order_id))
    return buy_order_id


# 卖操作
def sell_action(this_symbol, this_price, this_amount):
    sum=get_balance_action('btc')
    sum=float(sum)-0.0001
    sum=float('%.4f'%sum)
    print('this_symbol{0} price {1} sum {2}'.format(this_symbol,this_price,sum))

    sell_result=''
    while(sell_result ==''):
        try:
            sell_result = fcoin.sell(this_symbol, this_price, sum)
        except Exception as e:
            print(e)
            time.sleep(1)

    sell_order_id = sell_result['data']
    if sell_order_id:
        print('卖单', this_price, '价格成功委托', '订单ID', sell_order_id)

    # 输出订单信息
    # print(fcoin.get_order(sell_order_id))
    return sell_order_id


# 撤销订单
def cancel_order_action(this_order_id):
    print('sleep 10 S ')
    time.sleep(10)
    cancel_info = fcoin.cancel_order(this_order_id)
    # if cancel_info['status'] == 0:
    #     print('成功撤销订单', this_order_id)


# 获取行情
def get_ticker(this_symbol):
    ticker = fcoin.get_market_ticker(symbol)
    now_price = ticker['data']['ticker'][0]
    print('最新成交价', now_price)

    return now_price


# 授权
api_key = api_key
api_secret = api_secret
fcoin.auth(api_key, api_secret)

# 交易类型
symbol = 'btcusdt'
# 金额 无用了
amount = 35000
# 已成交
filled = 'filled'
# 未成交
submitted = 'submitted'

base_money=get_balance_action('usdt')
# print(base_money)
base_action='usdt'

def getCountbyBase(money,price):
    money=float(money)
    money=float('%.2f'%money)
    sum=money/price

    sum=float(sum)-0.0001
    sum=float('%.4f'%sum)

    print('getCountbyBase base {0} price{1} sum{2}',money,price,sum)
    return sum

def robot():
    # 账户余额
    # get_balance_action('eth')
    # get_balance_action('usdt')
    # 获取委托订单列表
    get_order_list_first(symbol, submitted)


# 定时器
def timer():
    while True:
        robot()
        time.sleep(3)


# 守护进程
if __name__ == '__main__':
    t = threading.Thread(target=timer())
    t.start()
    t.join()
