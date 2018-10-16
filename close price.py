#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
from io import StringIO
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def crawl_price(date):
    r = requests.post('http://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' + str(date).split(' ')[0].replace('-','') + '&type=ALL')
    ret = pd.read_csv(StringIO("\n".join([i.translate({ord(c): None for c in ' '}) 
                                        for i in r.text.split('\n') 
                                        if len(i.split('",')) == 17 and i[0] != '='])), header=0)
    ret = ret.set_index('證券代號')
    ret['成交金額'] = ret['成交金額'].str.replace(',','')
    ret['成交股數'] = ret['成交股數'].str.replace(',','')
    return ret


import datetime
import time
data = {}
n_days = 4
date = datetime.datetime.now()
fail_count = 0
allow_continuous_fail_count = 5
while len(data) < n_days:
    print('parsing', date)
    # 使用 crawPrice 爬資料
    try:
        # 抓資料
        data[date] = crawl_price(date)
        print('success!')
        fail_count = 0
    except:
        # 假日爬不到
        print('fail! check the date is holiday')
        fail_count += 1
        if fail_count == allow_continuous_fail_count:
            raise
            break
    
    # 減一天
    date -= datetime.timedelta(days=1)
    time.sleep(5)


# In[2]:


print(data)


# In[5]:


close = pd.DataFrame({k:d['收盤價'] for k,d in data.items()}).transpose()
close.index = pd.to_datetime(close.index)
close

open = pd.DataFrame({k:d['開盤價'] for k,d in data.items()}).transpose()
open.index = pd.to_datetime(open.index)
high = pd.DataFrame({k:d['最高價'] for k,d in data.items()}).transpose()
high.index = pd.to_datetime(high.index)
low = pd.DataFrame({k:d['最低價'] for k,d in data.items()}).transpose()
low.index = pd.to_datetime(low.index)
volume = pd.DataFrame({k:d['成交股數'] for k,d in data.items()}).transpose()
volume.index = pd.to_datetime(volume.index)

tsmc = {
    'close':close['2330']['2018'].dropna().astype(float),
    'open':open['2330']['2018'].dropna().astype(float),
    'high':high['2330']['2018'].dropna().astype(float),
    'low':low['2330']['2018'].dropna().astype(float),
    'volume': volume['2330']['2018'].dropna().astype(float),
}
tsmc['close'].plot()

#plt.show()

import talib
from talib import abstract
from talib.abstract import *


def talib2df(talib_output):
    if type(talib_output) == list:
        ret = pd.DataFrame(talib_output).transpose()
    else:
        ret = pd.Series(talib_output)
        ret.index = tsmc['close'].index
    return ret;

talib2df(talib.abstract.STOCH(tsmc)).plot()
tsmc['close'].plot(secondary_y=True)

plt.show()
