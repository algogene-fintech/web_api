from AlgoAPI import AlgoAPIUtil, AlgoAPI_Backtest
from datetime import datetime, timedelta
from talib import RSI, ATR
import numpy as np

class AlgoEvent:
    def __init__(self):
        self.timer = datetime(1970,1,1)
        self.timer = datetime(1970,1,1)
        self.RSI_period = 14
        self.ATR_period = 14
        self.instrument = "JPXJPY"
        self.rsi_overbought = 70
        self.rsi_oversold = 30
        self.ATR_multiple = 2

    def start(self, mEvt):
        self.evt = AlgoAPI_Backtest.AlgoEvtHandler(self, mEvt)
        self.evt.start()


    def on_marketdatafeed(self, md, ab):
        # execute stratey every 24 hours
        if md.timestamp >= self.timer+timedelta(hours=24):

            # get last 14 closing price
            res = self.evt.getHistoricalBar({"instrument":self.instrument}, self.RSI_period+1, "D")
            arrClose = np.array([res[t]['c'] for t in res])
            arrHigh = np.array([res[t]['h'] for t in res])
            arrLow = np.array([res[t]['l'] for t in res])
            
            # calculate the current RSI value
            RSI_cur = RSI(arrClose, self.RSI_period)[-1]

            # calculate the current ATR value
            ATR_cur = ATR(arrHigh, arrLow, arrClose, self.ATR_period)[-1]
            
            # print out RSI and ATR value to console
            self.evt.consoleLog("RSI_cur, ATR_cur = ", RSI_cur, ATR_cur)


            # get outstanding position
            pos, osOrder, pendOrder = self.evt.getSystemOrders()

            # open an order if we have no outstanding position
            if pos[self.instrument]["netVolume"]==0:

                # open a sell order if it is overbought
                if RSI_cur>self.rsi_overbought:
                    self.open_order(-1, md.lastPrice, ATR_cur)
                    
                # open a buy order if it is oversold
                elif RSI_cur<self.rsi_oversold:
                    self.open_order(1, md.lastPrice, ATR_cur)

            else:
                # calculate the new ATR trailing stop loss level
                for tradeID in list(osOrder):
                    buysell = osOrder[tradeID]["buysell"]
                    sl = osOrder[tradeID]["stopLossLevel"]
                    
                    if buysell==1:
                        sl = max(sl, md.lastPrice-self.ATR_multiple*ATR_cur)


                    elif buysell==-1:
                        sl = min(sl, md.lastPrice+self.ATR_multiple*ATR_cur)

                    # update to new stop loss level
                    self.evt.update_opened_order(tradeID=tradeID, sl=sl)


            # update timer
            self.timer = md.timestamp


    def open_order(self, buysell, current_price, ATR):

        # set stop loss level to be 2*ATR below current price for buy order
        if buysell==1:
            sl = current_price - self.ATR_multiple*ATR

        # set stop loss level to be 2*ATR above current price for buy order
        else:
            sl = current_price + self.ATR_multiple*ATR

        # create order object
        order = AlgoAPIUtil.OrderObject(
            instrument = self.instrument,
            openclose = 'open',
            buysell = buysell,    #1=buy, -1=sell
            ordertype = 0,        #0=market, 1=limit
            volume = 0.01,
            stopLossLevel = sl
        )

        # send order to server
        self.evt.sendOrder(order)


    def on_bulkdatafeed(self, isSync, bd, ab):
        pass

    def on_newsdatafeed(self, nd):
        pass

    def on_weatherdatafeed(self, wd):
        pass
    
    def on_econsdatafeed(self, ed):
        pass
        
    def on_orderfeed(self, of):
        pass
            
    def on_dailyPLfeed(self, pl):
        pass

    def on_openPositionfeed(self, op, oo, uo):
        pass
