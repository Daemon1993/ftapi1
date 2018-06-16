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
import config
import math
import gevent

# 初始化
fcoin = Fcoin()

# 授权
api_key = api_key
api_secret = api_secret
fcoin.auth(api_key, api_secret)


def roundFun(value,n):
    # print(value)

    return math.floor(value*math.pow(10,n))/math.pow(10,n)



# 查询账户余额
def get_balance_action(balance_info,this_symbol):
    balance=''
    for data in balance_info['data']:
        if this_symbol==data['currency']:
            balance=data
            break
    # print(balance)
    return float(balance['available'])





def robot():
    print('\n---------------')
    balance_info=fcoin.get_balance()

    sellCoinBalance=get_balance_action(balance_info,config.sellCoin)

    buyCoinBalance=get_balance_action(balance_info,config.buyCoin)

    print('当前账号有 {0}  {1}'.format(config.sellCoin,str(sellCoinBalance)))
    print('当前账号有 {0}  {1}'.format(config.buyCoin,buyCoinBalance))

    #取消订单
    order_list = fcoin.list_orders(symbol=config.symbol, states='submitted')
    if 'data' in order_list and len(order_list['data']):
        order_item = order_list['data'][0]
        cancel_order_action(order_item['id'])




    ticker = fcoin.get_market_ticker(config.symbol)
    buy1=ticker['data']['ticker'][config.ticker_last_buy1]
    sell1=ticker['data']['ticker'][config.ticker_last_sell1]

    #最少买入个数
    minAmount = 0.0001

    buyCount=roundFun(buyCoinBalance/buy1,4)

    isBuy=(buyCount>=minAmount)
    isSell=(sellCoinBalance>=minAmount)

    print('当前买入价格 {0} 卖单价格{1}  isBuy {2}  isSell {3}'.format(buy1,sell1,isBuy,isSell))

    taskList=[]
    size=sell1-buy1

    if isBuy:
        if size>10:
            print('size >10 buy cancle')
        else:
            taskList.append(gevent.spawn(buyAction,config.symbol,buy1,buyCount))


    if isSell:
        sellCount=roundFun(sellCoinBalance,4)
        taskList.append(gevent.spawn(sellAction,config.symbol,sell1,sellCount))

    # print(taskList)
    gevent.joinall(taskList)


#买
def buyAction(symbol, price, buyCount):
    print('购买价格 {0} 数量 {1}'.format(price,buyCount))
    buy_result = fcoin.buy(symbol, price, buyCount)

    buy_order_id = buy_result['data']
    if buy_order_id:
        print('买单成功')

#卖
def sellAction(symbol, price, sellCount):
    print('卖出价格 {0} 数量 {1}'.format(price,sellCount))
    sell_result = fcoin.sell(symbol, price, sellCount)
    sell_order_id = sell_result['data']
    if sell_order_id:
        print('卖单成功')


# 撤销订单
def cancel_order_action(this_order_id):
    print('cancel_order_action')
    cancel_info = fcoin.cancel_order(this_order_id)
    time.sleep(1)

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
