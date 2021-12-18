from AlgoAPI import AlgoAPIUtil, AlgoAPI_Backtest
from datetime import datetime, timedelta
from talib import RSI
import numpy as np


class AlgoEvent:
    def __init__(self):
        self.timer = datetime(1970,1,1)
        self.rsi_period = 14
        self.rsi_overbought = 70
        self.rsi_oversold = 30
        self.position = 0
        self.last_tradeID = ""
        self.instrument = "USDJPY"
        
    def start(self, mEvt):
        self.evt = AlgoAPI_Backtest.AlgoEvtHandler(self, mEvt)
        self.evt.start()
        
    def on_marketdatafeed(self, md, ab):
        # execute stratey every 24 hours
        if md.timestamp >= self.timer+timedelta(hours=24):
            # get last 14 closing price
            res = self.evt.getHistoricalBar({"instrument":self.instrument}, self.rsi_period+1, "D")
            arr = [res[t]['c'] for t in res]
            
            # calculate the current RSI value
            RSI_cur = RSI(np.array(arr), self.rsi_period)[-1]
            
            # print out RSI value to console
            self.evt.consoleLog("RSI_cur = ", RSI_cur)
            
            # open an order if we have no outstanding position
            if self.position==0:
                
                # open a sell order if it is overbought
                if RSI_cur>self.rsi_overbought:
                    self.open_order(-1)
                    
                # open a buy order if it is oversold
                elif RSI_cur<self.rsi_oversold:
                    self.open_order(1)
            
            # check condition to close an order
            else:
                
                # close a position if we have previously open a buy order and RSI now reverse above 50 
                if self.position>0 and RSI_cur>50:
                    self.close_order()
                
                # close a position if we have previously open a sell order and RSI now reverse below 50 
                elif self.position<0 and RSI_cur<50:
                    self.close_order()
            
            # update timer
            self.timer = md.timestamp


    def open_order(self, buysell):
        order = AlgoAPIUtil.OrderObject()
        order.instrument = self.instrument
        order.openclose = 'open'
        order.buysell = buysell    #1=buy, -1=sell
        order.ordertype = 0  #0=market, 1=limit
        order.volume = 0.01
        self.evt.sendOrder(order)
        
    def close_order(self):
        order = AlgoAPIUtil.OrderObject()
        order.openclose = 'close'
        order.tradeID = self.last_tradeID
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
        # when system confirm an order, update last_tradeID and position
        if of.status=="success":
            self.position += of.fill_volume*of.buysell
            if self.position==0:
                self.last_tradeID = ""
            else:
                self.last_tradeID = of.tradeID
            
    def on_dailyPLfeed(self, pl):
        pass

    def on_openPositionfeed(self, op, oo, uo):
        pass
