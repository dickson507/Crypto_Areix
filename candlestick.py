import math

def isBullishHarami(trend, pre_open, pre_close, pre_low, pre_high, 
                    cur_open, cur_close):
    if (trend == 'DOWNWARD'):
        if (pre_open > pre_close):
            if (cur_open < cur_close):
                if (pre_close < cur_open):
                    if (pre_open > cur_close):
                        if ((abs(pre_open-pre_close) / abs(pre_low-pre_high)) > 0.6):
                            return True
    return False

def isBullishEngulfing(trend, pre_open, pre_close, 
                    cur_open, cur_close, cur_low, cur_high):
    if (trend == 'DOWNWARD'):
        if (pre_open > pre_close):
            if (cur_open < cur_close):
                if (pre_close > cur_open):
                    if (pre_open < cur_close):
                        if ((abs(cur_open-cur_close) / abs(cur_low-cur_high)) > 0.6):
                            return True
    return False

def isBullishDoji(trend, pre_open, pre_close, pre_low, pre_high, 
                    cur_open, cur_close, cur_low, cur_high):
    if (trend == 'DOWNWARD'):
        if (pre_open > pre_close):
            if (pre_low > cur_low):
                if ((cur_high-cur_close) > (3*abs(cur_open-cur_close))):
                    if ((cur_open-cur_low) < ((cur_high-cur_close)/3)):
                        if ((abs(pre_open-pre_close) / abs(pre_low-pre_high)) > 0.6):
                            return True
    return False

def isHammer(trend, pre_open, pre_close, pre_low, pre_high,
                    cur_open, cur_close, cur_low, cur_high, cur_bodyBottom, cur_bodyTop):
    if (trend == 'DOWNWARD'):
        if (pre_open > pre_close):
            if (pre_low > cur_low):
                if ((cur_bodyBottom-cur_low) > (2*abs(cur_open-cur_close))):
                    if ((cur_open-cur_low) < ((cur_high-cur_close)/3)):
                        if ((abs(pre_open-pre_close) / abs(pre_low-pre_high)) > 0.6):
                            return True
    return False

def isMorningStar(trend, prepre_open, prepre_close, prepre_low, prepre_high,
                    pre_open, pre_close, pre_low, pre_high, 
                    cur_open, cur_close, cur_low, cur_high):
    if (trend == 'DOWNWARD'):
        if (prepre_open > prepre_close):
            if (cur_open < cur_close):
                if ((abs(prepre_open-prepre_close) / abs(prepre_low-prepre_high)) > 0.6):
                    if (pre_open < prepre_close):
                        if (cur_open > pre_close):
                            if ((abs(pre_open-pre_close) / abs(pre_low-pre_high)) < 0.3):
                                if ((pre_open-pre_close) < abs(prepre_open-prepre_close)):
                                    if ((pre_open-pre_close) < abs(cur_open-cur_close)):
                                        if (pre_low < cur_low):
                                            if (pre_low < prepre_low):
                                                if (pre_high < prepre_open):
                                                    if (pre_high < cur_close):
                                                        return True
    return False

def isBearishHarami(trend, pre_open, pre_close, pre_low, pre_high, 
                    cur_open, cur_close):
    if (trend == 'UPWARD'):
        if (pre_open < pre_close):
            if (cur_open > cur_close):
                if (pre_close > cur_open):
                    if (pre_open < cur_close):
                        if ((abs(pre_open-pre_close) / abs(pre_high-pre_low)) > 0.6):
                            return True
    return False

def isBearishEngulfing(trend, pre_open, pre_close, pre_bodyBottom, pre_bodyTop,
                    cur_open, cur_close, cur_low, cur_high, cur_bodyBottom, cur_bodyTop):
    if (trend == 'UPWARD'):
        if (pre_open < pre_close):
            if (cur_open > cur_close):
                if (cur_bodyBottom < pre_bodyBottom):
                    if (cur_bodyTop, pre_bodyTop):
                        if ((abs(cur_open-cur_close) / abs(cur_high-cur_low)) > 0.6):
                            return True
    return False

def isGravestoneDoji(trend, pre_open, pre_close, pre_low, pre_high, 
                    cur_open, cur_close, cur_low, cur_high):
    if (trend == 'UPWARD'):
        if (pre_open < pre_close):
            if (cur_high > pre_high):
                if ((cur_high-cur_close) > (3*abs(cur_open-cur_close))):
                    if ((cur_open-cur_low) < ((cur_high-cur_close)/3)):
                        if ((abs(pre_open-pre_close) / abs(pre_low-pre_high)) > 0.6):
                            return True
    return False

def isHangingMan(trend, pre_open, pre_close, pre_low, pre_high, 
                    cur_high, cur_shadowBottom, cur_shadowTop):
    if (trend == 'UPWARD'):
        if (pre_open < pre_close):
            if (cur_high > pre_high):
                if (cur_shadowBottom > (2*abs(pre_open-pre_close))):
                    if (cur_shadowTop > (0.3*abs(pre_open-pre_close))):
                        if ((abs(pre_open-pre_close) / abs(pre_low-pre_high)) > 0.6):
                            return True
    return False

def isEveningStar(trend, prepre_open, prepre_close, prepre_low, prepre_high,
                    pre_open, pre_close, pre_low, pre_high, 
                    cur_open, cur_close, cur_low, cur_high):
    if (trend == 'UPWARD'):
        if (prepre_open < prepre_close):
            if (cur_open > cur_close):
                if ((abs(prepre_open-prepre_close) / abs(prepre_low-prepre_high)) > 0.6):
                    if (pre_open > prepre_close):
                        if (cur_open < pre_close):
                            if ((abs(pre_open-pre_close) / abs(pre_low-pre_high)) < 0.3):
                                if ((pre_open-pre_close) < abs(prepre_open-prepre_close)):
                                    if ((pre_open-pre_close) < abs(cur_open-cur_close)):
                                        if (pre_high > cur_high):
                                            if (pre_high > prepre_high):
                                                if (pre_low > prepre_open):
                                                    if (pre_low > cur_close):
                                                        return True
    return False