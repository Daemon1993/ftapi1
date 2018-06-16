__author__ = 'Daemon1993'

import json
from fcoin3 import Fcoin
import threading
import time
from config import api_key
from config import api_secret

# 交易类型
symbol = 'btcusdt'
filled = 'filled'

# 初始化
fcoin = Fcoin()
# 授权
api_key = api_key
api_secret = api_secret
fcoin.auth(api_key, api_secret)


order_list = fcoin.list_orders(symbol=symbol, states=filled,limit=100)
print(json.dumps(order_list))
sum=0
for order in order_list['data']:
    print(order['side'], order['price'], order['state'])
    sum+=float(order['executed_value'])
print(sum)