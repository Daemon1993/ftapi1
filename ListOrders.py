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


order_list = fcoin.list_orders(symbol=symbol, states=filled)
print(json.dumps(order_list))
sum=0
for order in order_list['data']:
    print('订单ID', order['id'], '挂单价格', order['price'], '挂单数量', order['amount'], '方向', order['side'],order['state'])
    sum+=float(order['executed_value'])
print(sum)