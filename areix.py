import areix_io as aio
from areix_io.utils import create_report_folder, SideType

from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score
import pandas as pd
import numpy as np
import math

from candlestick import det_candlestick_pattern

PRED_DAYS = 2 
PCT_CHANGE = 0.04
MACD_RATIO = 48
'''
Data pre processing step
'''
def bollinger_band(data, n_lookback, n_std):
    hlc3 = (data['high'] + data['low'] + data['close']) / 3
    mean, std = hlc3.rolling(n_lookback).mean(), hlc3.rolling(n_lookback).std()
    upper = mean + n_std*std
    lower = mean - n_std*std
    return upper, lower

def update_df(df):
    # upper, lower = bollinger_band(df, 20, 2)

    # df['ma10'] = df.close.rolling(10).mean()
    # df['ma20'] = df.close.rolling(20).mean()
    # df['ma50'] = df.close.rolling(50).mean()
    # df['ma100'] = df.close.rolling(100).mean()

    # df['x_ma10'] = (df.close - df.ma10) / df.close
    # df['x_ma20'] = (df.close - df.ma20) / df.close
    # df['x_ma50'] = (df.close - df.ma50) / df.close
    # df['x_ma100'] = (df.close - df.ma100) / df.close

    # df['x_delta_10'] = (df.ma10 - df.ma20) / df.close
    # df['x_delta_20'] = (df.ma20 - df.ma50) / df.close
    # df['x_delta_50'] = (df.ma50 - df.ma100) / df.close

    # df['x_mom'] = df.close.pct_change(periods=2)
    # df['x_bb_upper'] = (upper - df.close) / df.close
    # df['x_bb_lower'] = (lower - df.close) / df.close
    # df['x_bb_width'] = (upper - lower) / df.close

    df['ma12'] = df.close.rolling(12*MACD_RATIO).mean()
    df['ma26'] = df.close.rolling(26*MACD_RATIO).mean()
    df['dif'] = df.ma12 - df.ma26
    df['trend'] = [np.nan if np.isnan(dif) else 'UPWARD' if (dif > 0) else 'DOWNWARD' for dif in df['dif']]

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
    num_pre_train = 26*MACD_RATIO

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

        # self.clf = KNeighborsClassifier(7)
        
        # tmp = df.dropna().astype(float)
        # X, y = get_clean_Xy(tmp[:self.num_pre_train])
        # self.clf.fit(X, y)

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
        
        prepre_data = hist_data[bar_number-3]
        pre_data = hist_data[bar_number-2]

        predict = det_candlestick_pattern(prepre_data, pre_data, bar_data)

        # open, high, low, close = bar_data.open, bar_data.high, bar_data.low, bar_data.close
        # X = get_X(bar_data)
        # forecast = self.clf.predict([X])[0]
        # self.y_pred.append(forecast)

        # self.ctx.cplot(forecast,'Forcast')
        # self.ctx.cplot(self.y[tick],'Groundtruth')
        # # self.info(f"focasing result: {forecast}")

        close = bar_data.close
        upper, lower = close * (1 + np.r_[1, -1]*PCT_CHANGE)

        cash = self.ctx.available_cash

        # if forecast == 1 and not self.ctx.get_position(self.code):
        if predict == 'BULL' and not self.ctx.get_position(self.code):
            amount = cash if (cash < 55800) else 55800
            o1 = self.order_amount(code=self.code,amount=amount,side=SideType.BUY, asset_type='Crypto')
            self.info(f"BUY order {o1['id']} created #{o1['quantity']} @ {close:2f}")
            osl = self.sell(code=self.code,quantity=o1['quantity'], stop_price=lower, asset_type='Crypto')
            self.info(f"STOPLOSS order {osl['id']} created #{osl['quantity']} @ {lower:2f}")
            # os2 = self.sell(code=self.code,quantity=o1['quantity'], price=upper, asset_type='Crypto')
            # self.info(f"STOPGAIN order {os2['id']} created #{os2['quantity']} @ {upper:2f}")
            
        # elif forecast == -1 and self.ctx.get_position(self.code):
        elif predict == 'BEAR' and self.ctx.get_position(self.code):
            quantity = self.ctx.get_position(self.code)['quantity']
            o2 = self.sell(code=self.code, quantity=quantity, price=close, ioc=True, asset_type='Crypto')
            self.info(f"SELL order {o2['id']} created #{o2['quantity']} @ {close:2f}")