import areix_io as aio
from areix_io.utils import create_report_folder, SideType

import pandas as pd
import numpy as np
import math

from candlestick import det_candlestick_pattern

PRED_DAYS = 2 
PCT_CHANGE = 0.04
INTERVAL_TO_DAY = 48
'''
Data pre processing step
'''
def bollinger_band(data, n_lookback, n_std):
    hlc3 = (data['high'] + data['low'] + data['close']) / 3
    mean, std = hlc3.rolling(n_lookback).mean(), hlc3.rolling(n_lookback).std()
    upper = mean + n_std*std
    lower = mean - n_std*std
    return upper, lower

def find_rsi_UD(df):
    U = []
    D = []
    for i in range(0, len(df.index)):
        dif = df['close'].iloc[i] - df['close'].iloc[i-1]
        if (i == 0 or dif == 0):
            U.append(0)
            D.append(0)
        elif (dif > 0):
            U.append(dif)
            D.append(0)
        else:
            U.append(0)
            D.append(abs(dif))
    return U, D

def parabolic_sar(df):
    alpha = 0.2
    sar = []
    trend = []
    for i in range(0, len(df.index)):
        if (i == 0):
            sar.append(df['high'].iloc[i])
            trend.append('DOWNWARD')
            continue
       
        if (trend[i-1] == 'DOWNWARD'):
            sar.append(sar[i-1] - alpha*(sar[i-1] - df['high'].iloc[i-1]))
            trend.append('DOWNWARD')
        elif (trend[i-1] == 'UPWARD'):
            sar.append(sar[i-1] + alpha*(df['low'].iloc[i-1] - sar[i-1]))
            trend.append('UPWARD')

        if (df['close'].iloc[i] > sar[i]):
            sar[i] = df['low'].iloc[i]
            trend[i] = 'UPWARD'
            if (alpha < 0.2):
                alpha += 0.02
        elif (df['close'].iloc[i] < sar[i]):
            sar[i] = df['high'].iloc[i]
            trend[i] = 'DOWNWARD'
            if (alpha < 0.2):
                alpha += 0.02
    return sar, trend

def update_df(df):

    # construct bollinger_band
    upper, lower = bollinger_band(df, 20, 2)
    df['bb_upper'] = upper
    df['bb_lower'] = lower

    # calculate RSI value
    U, D = find_rsi_UD(df)
    df['U'] = U
    df['D'] = D
    df['U_ma14'] = df.U.rolling(14).mean()
    df['D_ma14'] = df.D.rolling(14).mean()
    df['rsi'] = df.U_ma14 / (df.U_ma14 + df.D_ma14)

    # find Parabolic SAR value and Predict Trend
    sar, trend = parabolic_sar(df)
    df['sar'] = sar
    df['trend'] = trend

    # construct candlestick element
    df['bodyBottom'] = [x if (x > y) else y for x, y in zip(df['open'],df['close'])]
    df['bodyTop'] = [y if (x > y) else x for x, y in zip(df['open'],df['close'])]
    df['shadowBottom'] = abs(df.low - df.bodyBottom)
    df['shadowTop'] = abs(df.high - df.bodyTop)

    return df

def get_X(data):
    return data.filter(like='x').values

def get_y(data):
    # use price change in the future 2 days as training label
    y = data.close.pct_change(PRED_DAYS).shift(-PRED_DAYS)  
    y[y.between(-PCT_CHANGE, PCT_CHANGE)] = 0             
    y[y > 0] = 1
    y[y < 0] = -1
    return y


def get_clean_Xy(df):
    X = get_X(df)
    y = get_y(df).values
    isnan = np.isnan(y)
    X = X[~isnan]
    y = y[~isnan]
    return X, y

class MLStrategy(aio.Strategy):
    num_pre_train = 30*INTERVAL_TO_DAY

    def initialize(self):
        '''
        Model training step
        '''

        self.info('initialize')
        self.code = 'XRP/USDT'
        df = self.ctx.feed[self.code]
        self.ctx.feed[self.code] = update_df(df)

        self.y = get_y(df[self.num_pre_train-1:])
        self.y_true = self.y.values

        self.y_pred = []
    
    def before_trade(self, order):
        return True

    def on_order_ok(self, order):
        self.info(f"{order['side'].name} order {order['id']} ({order['order_type'].name}) executed #{order['quantity']} {order['code']} @ ${order['price']:2f}; Commission: ${order['commission']}; Available Cash: ${self.ctx.available_cash}; Position: #{self.ctx.get_quantity(order['code'])}; Gross P&L : ${order['pnl']}; Net P&L : ${order['pnl_net']}")


        if not order['is_open']:
            self.info(f"Trade closed, pnl: {order['pnl']}========")


    def on_market_start(self):
        # self.info('on_market_start')
        pass

    def on_market_close(self):
        # self.info('on_market_close')
        pass

    def on_order_timeout(self, order):
        self.info(f'on_order_timeout. Order: {order}')
        pass

    def finish(self):
        self.info('finish')

    def on_bar(self, tick):
        '''
        Model scoring and decisioning step
        '''
        bar_data = self.ctx.bar_data[self.code]
        hist_data = self.ctx.hist_data[self.code]

        bar_number = len(hist_data)

        if bar_number < self.num_pre_train:
            return 
        
        # get data from last 2 interval
        prepre_data = hist_data[bar_number-3]
        pre_data = hist_data[bar_number-2]

        # get predict result by recognizing reversal candlestick pattern
        predict = det_candlestick_pattern(prepre_data, pre_data, bar_data)

        close = bar_data.close
        upper, lower = close * (1 + np.r_[1, -1]*PCT_CHANGE)
        bb_upper = bar_data.bb_upper
        bb_lower = bar_data.bb_lower
        rsi = bar_data.rsi
        cash = self.ctx.available_cash


        # call buy order if 
        # there is a Bullish reversal pattern or
        # RSI value larger than or equal to 0.65   
        if (((predict == 'BULL')
        or (rsi >= 0.65)) 
        and not self.ctx.get_position(self.code)):
            amount = cash if (cash < 55800) else 55800
            o1 = self.order_amount(code=self.code,amount=amount,side=SideType.BUY, asset_type='Crypto')
            self.info(f"BUY order {o1['id']} created #{o1['quantity']} @ {close:2f}")
            osl = self.sell(code=self.code,quantity=o1['quantity'], stop_price=lower, asset_type='Crypto')
            self.info(f"STOPLOSS order {osl['id']} created #{osl['quantity']} @ {lower:2f}")

        # call sell order if
        # there is a Bearish reversal pattern or
        # price have touched the bollinger band or
        # RSI value smaller than or equal to 0.35   
        elif (((predict == 'BEAR')
        or (close > bb_upper or close < bb_lower) 
        or (rsi <= 0.35)) 
        and self.ctx.get_position(self.code)):
            quantity = self.ctx.get_position(self.code)['quantity']
            o2 = self.sell(code=self.code, quantity=quantity, price=close, ioc=True, asset_type='Crypto')
            self.info(f"SELL order {o2['id']} created #{o2['quantity']} @ {close:2f}")