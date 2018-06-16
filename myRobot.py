__author__ = 'Daemon1993'


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
    # print(json.dumps(balance_info))
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
            cancel_order_action(order['id'],this_states)


# 获取订单列表第一个订单



def get_order_list_first(this_symbol, this_states):
    order_list = fcoin.list_orders(symbol=this_symbol, states=this_states)
    if 'data' in order_list and len(order_list['data']):
        order_item = order_list['data'][0]
        print(order_item)
        if order_item:
            order_price = float(order_item['price'])

            if this_states == submitted:
                print('发现未成交订单，尝试先取消委托订单')
                cancel_order_action(order_item['id'],this_states)
            elif this_states == filled:
                now_price = get_ticker(symbol,last_price)
                print('最新订单 成交价格{0} '.format(now_price))
                if order_item['side'] == 'buy':
                    print('尝试卖出')
                    if order_price-now_price<=20:
                        print('现价{0} 上一笔买入价{1} 差价20美元以内 直接卖出 '.format(now_price,order_price))
                        sell_action(symbol, now_price-1)
                    else:
                        print('现价 买入价 差距超过20美元 等待挂单5S ')
                        sell_order_id=sell_action(symbol, order_price-20)
                        time.sleep(5)
                        order_item=fcoin.get_order(sell_order_id)
                        print(json.dumps(order_item))
                        status=order_item['data']['state']
                        print('挂单5S 完了 获取订单状态 是否卖出成功 {0} {1}'.format(sell_order_id,status))
                        if submitted == status:

                            cancel_order_action(sell_order_id,this_states)
                            buy1_p=get_ticker(symbol,last_buy1)
                            print('订单未成功 获取买一价格 直接卖出 {0}'.format(buy1_p))
                            sell_action(symbol, buy1_p)
                        # print('价格小于买入  不卖')
                elif order_item['side'] == 'sell':
                    # 这里只判断卖出价格高于买入价格
                    print('尝试买入')
                    smartbuy(symbol)

    else:
        if this_states == submitted:
            print('没有发现未成交订单 开始获取已成交订单')
            get_order_list_first(this_symbol, filled)
        elif this_states == filled:
            print('没有发现已成交的 直接开始买入')
            smartbuy(symbol)


# 查询订单
def check_order_state(this_order_id):
    check_info = fcoin.get_order(this_order_id)
    return check_info['data']


#自动判断买入条件
def smartbuy(symbol):
    result=fcoin.get_market_ticker(symbol)
    buy1=result['data']['ticker'][2]
    sell1=result['data']['ticker'][4]

    #当买的价格和卖的价格相差10刀 就不买了
    size1=sell1-buy1
    print('买一 {0} 卖一 {1}'.format(buy1,sell1))
    if size1>20:
        print('买卖相差 {0} 放弃'.format(size1))
    else:
        buy_action(symbol, sell1)


    pass

# 买操作
def buy_action(this_symbol, this_price):

    money=get_balance_action(base_action)
    sum=getCountFromSumAndPrice(money,this_price)
    if sum<=0:
        print('sum is <=0')
        return

    buy_result=''
    while(buy_result ==''):
        try:
            buy_result = fcoin.buy(this_symbol, this_price, sum)
        except Exception as e:
            print(e)
            time.sleep(1)

    try:
        print(buy_result)
        buy_order_id = buy_result['data']
        if buy_order_id:
            print('买单', this_price, '价格成功委托', '订单ID', buy_order_id)
    except Exception as e:
        print(e)



    # 输出订单信息
    # print(fcoin.get_order(buy_order_id))
    return buy_order_id


# 卖操作
def sell_action(this_symbol, this_price):
    sum=get_balance_action('btc')
    sum1=float(sum)
    print(sum1)
    sum1=sum1-0.0001
    sum=float('%.4f'%sum1)
    print('this_symbol {0} price {1} sum {2} '.format(this_symbol,this_price,sum))

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
def cancel_order_action(this_order_id,states):

    if states == 'pending_cancel':
        print('订单取消中...服务器缓慢 sleep 3S')
        time.sleep(3)
        return

    print('cancle {0}'.format(this_order_id))
    time.sleep(1)
    #异步的 调用后睡2S后行动
    cancel_info = fcoin.cancel_order(this_order_id)
    time.sleep(2)
    # if cancel_info['status'] == 0:
    #     print('成功撤销订单', this_order_id)


# 获取行情
def get_ticker(this_symbol,type):
    ticker = fcoin.get_market_ticker(this_symbol)
    #当前最新成交
    now_price = ticker['data']['ticker'][type]

    print('get_ticker type{0}'.format(now_price))

    return now_price


# 授权
api_key = api_key
api_secret = api_secret
fcoin.auth(api_key, api_secret)

# 交易类型
symbol = 'btcusdt'

# 已成交
filled = 'filled'
# 未成交
submitted = 'submitted'


#买1 卖1 最新成交
last_buy1=2
last_sell1=4
last_price=0

base_money=get_balance_action('usdt')
# print(base_money)
base_action='usdt'

def getCountFromSumAndPrice(money,price):
    money=float(money)
    money=float('%.2f'%money)
    sum=money/price

    sum=float(sum)-0.0001
    sum=float('%.4f'%sum)

    print('getCountbyBase base {0} price{1} sum{2}',money,price,sum)
    return sum

def robot():
    try:
        get_order_list_first(symbol, submitted)
    except Exception as e:
        print('robot erro {0}'.format(e))


# 定时器
def timer():
    while True:
        robot()
        time.sleep(2)


# 守护进程
if __name__ == '__main__':
    t = threading.Thread(target=timer())
    t.start()
    t.join()
