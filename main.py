TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2NDMyMDUxMTQsImlhdCI6MTYxMjEwMTA1NCwic3ViIjoiZjQzZyAzNWc1dzRoNXc0aCB3NDVoNXc0aHc0NWhqNXdqamh3NTRnIHc0NSBnNXc0ICJ9.CLavu4bIpl64So0F0nYl6g3NfmXqopLfS_UC-9wOgrA'
START_DATE = '2020-03-01'
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
    stats['model_name'] = 'MACD Trend prediction & Candlestick pattern trading'
    stats['algorithm'] = ['MACD', 'Candlestick pattern']
    # stats['model_measures'] = ['f1-score','accuracy']
    # ytrue = mytest.ctx.strategy.y_true[:-PRED_DAYS]
    # ypred = mytest.ctx.strategy.y_pred[:-PRED_DAYS]
    # # print(len(ytrue),len(ypred), ytrue, ypred)
    # stats['f1-score'] = f1_score(ytrue, ypred,average='weighted')
    # stats['accuracy'] = accuracy_score(ytrue, ypred)
    print(stats)

    mytest.contest_output()