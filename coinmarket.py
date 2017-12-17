from pymarketcap import Pymarketcap
import ccxt
from decimal import Decimal
import traceback
class coinmarkets(object):
    def __init__(self):
        self.coinmarketcap = Pymarketcap()
        self.bittrex = ccxt.bittrex()
        #self.poloniex = ccxt.poloniex()
        self.quadrigacx = ccxt.quadrigacx()
        self.quadrigacx.userAgent = self.quadrigacx.userAgents['chrome'];
        self.exchanges = {'Bittrex':self.bittrex,'Quadrigacx':self.quadrigacx,'coinmarketcap':self.coinmarketcap}
        self.loadMarkets()
        self.btc = {'name':'BTC','Cmc':{'last': '0', 'current':'0','color':'black','1h':'0','24h':'0','7d':'0'},
                    'Bittrex':{'last':'0','currentBTC':'0','lastBTC':'0','current':'0','color':'black','bid':'0','ask':'0','high':'0','low':'0','vol':'0','sell':'0','buy':'0','change':'0'},
                    'Quadrigacx':{'last':'0','currentBTC':'0','lastBTC':'0', 'current':'0','color':'black','bid':'0','ask':'0','high':'0','low':'0','vol':'0','sell':'0','buy':'0','change':'0'}}
        self.eth = {'name':'ETH','Cmc': {'last':'0', 'current':'0','color':'black','1h':'0','24h':'0','7d':'0'},
                    'Bittrex': {'last':'0','currentBTC':'0','lastBTC':'0', 'current':'0','color':'black','bid':'0','ask':'0','high':'0','low':'0','vol':'0','sell':'0','buy':'0','change':'0'},
                    'Quadrigacx': {'last':'0','currentBTC':'0','lastBTC':'0', 'current':'0','color':'black','bid':'0','ask':'0','high':'0','low':'0','vol':'0','sell':'0','buy':'0','change':'0'}}
        self.zec = {'name':'ZEC','Cmc': {'last':'0', 'current':'0','color':'black','1h':'0','24h':'0','7d':'0'},
                    'Bittrex': {'last':'0','currentBTC':'0','lastBTC':'0', 'current':'0','color':'black','bid':'0','ask':'0','high':'0','low':'0','vol':'0','sell':'0','buy':'0','change':'0'}}
        self.ltc = {'name':'LTC','Cmc': {'last': '0', 'current': '0','color':'black','1h':'0','24h':'0','7d':'0'},
                    'Bittrex': {'last':'0','currentBTC':'0','lastBTC':'0', 'current':'0','color':'black','bid':'0','ask':'0','high':'0','low':'0','vol':'0','sell':'0','buy':'0','change':'0'},
                    'Quadrigacx': {'last':'0','currentBTC':'0','lastBTC':'0', 'current':'0','color':'black','bid':'0','ask':'0','high':'0','low':'0','vol':'0','sell':'0','buy':'0','change':'0'}}
        self.coins = [self.btc,self.eth,self.zec,self.ltc]
    def loadMarkets(self):
        self.bittrex.loadMarkets()
        self.quadrigacx.loadMarkets()


    def updateCoinHelper(self,args, exchange):
        print("updatecoinhelper")
        if (args[0] == 'BTC'):
            # index = next(index for (index, d) in enumerate(data) if d['market'] == str(args[0] + "-USDT"))
            if(exchange == self.quadrigacx):
                pair = 'BTC/CAD'
                data = exchange.fetch_ticker(pair)
                sell = '0'
                buy =  '0'
                vol = data['quoteVolume']
            else:
                pair = 'BTC/USDT'
                data = exchange.fetch_ticker(pair)
                sell = data['info']['OpenSellOrders']
                buy = data['info']['OpenBuyOrders']
            currentPrice = int(data['last'])
            currentPriceBTC = "1k"
            bid = int(data['bid'])
            ask = int(data['ask'])
            high = int(data['high'])
            low = int(data['low'])
            vol = data['quoteVolume']
        else:
            # index = next(index for (index, d) in enumerate(data) if d['market'] == str(args[0] + "-BTC"))
            pair = args[0] + '/BTC'
            if(exchange == self.quadrigacx):
                dataCAD = exchange.fetch_ticker(args[0] + '/CAD')
                currentPrice = round(Decimal(float(dataCAD['last'])), 2)
                sell = '0'
                buy =  '0'
                try:
                    currentPriceBTC = round(Decimal(float(exchange.fetch_ticker(pair)['last'] * 1000)), 1)
                except:
                    pass
                    traceback.print_exc()
                    currentPriceBTC = '0'
                bid = float(dataCAD['bid'])
                ask = float(dataCAD['ask'])
                high = round(Decimal(float(dataCAD['high'])),2)
                low = round(Decimal(float(dataCAD['low'])),2)
                vol = dataCAD['quoteVolume']
            else:
                dataUSDT = exchange.fetch_ticker(args[0] + '/USDT')['last']
                data = exchange.fetch_ticker(pair)
                currentPrice = round(Decimal(float(dataUSDT)),2)
                currentPriceBTC = round(Decimal(float(data['last'] * 1000)),1)
                sell = data['info']['OpenSellOrders']
                buy = data['info']['OpenBuyOrders']
                bid = float(data['bid']* 1000)
                ask = float(data['ask']* 1000)
                high = round(Decimal(float(data['high'] * 1000)),1)
                low = round(Decimal(float(data['low'] * 1000)),1)
                vol = data['quoteVolume']

        for coin in self.coins:
            if coin['name'] == args[0]:
                coin[args[1]]['last'] = str(coin[args[1]]['current'])
                coin[args[1]]['current'] = str(currentPrice)
                coin[args[1]]['lastBTC'] = str(coin[args[1]]['currentBTC'])
                coin[args[1]]['currentBTC'] = str(currentPriceBTC)
                coin[args[1]]['bid'] = str(bid)
                coin[args[1]]['ask'] = str(ask)
                coin[args[1]]['high'] = str(high)
                coin[args[1]]['low'] = str(low)
                coin[args[1]]['vol'] = str(vol)
                coin[args[1]]['buy'] = str(buy)
                coin[args[1]]['sell'] = str(sell)
                if float(coin[args[1]]['current']) < float(coin[args[1]]['last']):
                    coin[args[1]]['color'] = "red"
                else:
                    coin[args[1]]['color'] = "black"

    def updatecoin(self, args):
        if len(args) < 2:
            market = self.coinmarketcap.ticker(args[0], convert='USD')
            for coin in self.coins:
                if coin['name'] == args[0]:
                    coin['Cmc']['last'] = str(coin['Cmc']['current'])
                    coin['Cmc']['current'] = str(market['price_usd'])
                    if float(coin['Cmc']['current']) < float(coin['Cmc']['last']):
                        coin['Cmc']['color'] = "red"
                    else:
                        coin['Cmc']['color'] = "black"

                    coin['Cmc']['1h'] = str(market['percent_change_1h']) + "%"
                    coin['Cmc']['24h'] = str(market['percent_change_24h']) + "%"
                    coin['Cmc']['7d'] = str(market['percent_change_7d']) + "%"
        else:
            # data = self.coinmarketcap.exchange(args[1])
            exchange = self.exchanges[args[1]]
            self.updateCoinHelper(args, exchange)


