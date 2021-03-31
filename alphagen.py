#Reference: http://www.diva-portal.org/smash/get/diva2:1114719/FULLTEXT01.pdf

TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2NDMyMDUxMTQsImlhdCI6MTYxMjEwMTA1NCwic3ViIjoiZjQzZyAzNWc1dzRoNXc0aCB3NDVoNXc0aHc0NWhqNXdqamh3NTRnIHc0NSBnNXc0ICJ9.CLavu4bIpl64So0F0nYl6g3NfmXqopLfS_UC-9wOgrA'
START_DATE = '2020-09-01'
END_DATE = '2021-03-12'
INTERVAL = '30m'
COMMISION = 0.001

import areix_io as aio
from areix_io.utils import create_report_folder, SideType
from areix import *
import pandas as pd
import numpy as np

if __name__ == '__main__':
    aio.set_token(TOKEN) # Only need to run once

    base = create_report_folder()

    start_date = START_DATE
    end_date = END_DATE

    sdf = aio.CryptoDataFeed(
        symbols=['XRP/USDT', 'BTC/USDT'], 
        start_date=start_date, 
        end_date=end_date,  
        interval=INTERVAL, 
        order_ascending=True, 
        store_path=base
    )
    feed, idx = sdf.fetch_data()
    benchmark = feed.pop('BTC/USDT')

    mytest = aio.BackTest(
        feed, 
        MLStrategy, 
        commission_rate=COMMISION, 
        min_commission=0, 
        trade_at='close', 
        benchmark=benchmark, 
        cash=55800, 
        tradedays=idx, 
        store_path=base
    )

    mytest.start()

    prefix = ''
    stats = mytest.ctx.statistic.stats(pprint=True, annualization=252, risk_free=0.0442)
    '''
    Model evaluation step
    '''
    stats['model_name'] = 'Parabolic SAR Trend prediction & Reversal Candlestick Pattern Recognition & RSI'
    stats['algorithm'] = ['Parabolic SAR', 'Reversal Candlestick Pattern', 'RSI', 'Bollinger Band']
    print(stats)

    mytest.contest_output()