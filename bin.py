from email import message
import imp
import os
import asyncio
from binance.client import Client, AsyncClient
from binance import ThreadedWebsocketManager, BinanceSocketManager
import pandas as pd
from time import sleep

api_key = "4axJUrVKe1bKD3vagLtuC5PBGLBXdBRoXQStiZWWJYL4lQx9WVApsvnsa7eZhlbq"
api_secret = "Uy4eDemOcbnRVIg3psQJFm2W2mWebBjnmqB3imzyFx89xcgU0PDEGWr6me1V80Mv"

test_api_key = "SseHCTBQ6LDv8i2K9BB0QbhJV6MjDvEuuvASw6UR9LSKLvdOBNOFswnQsAHCbaLk"
test_api_secret = "Ijt7QZn3ELekCdxdois7rzBU4xGHzDbbWYzqlq0raSdBj6kl1mpdAR7HnWmc0cUy"

client = Client(api_key, api_secret, testnet=False)

print(client.get_asset_balance('BTC'))

symbols = ['BTCUSDT']
# symbols = ['ADAGBP', 'APEGBP', 'AVAZGBP', 'BNBGBP', 'BTCGBP', 'CAKEGBP', 'CHZGBP', 'DOGEGBP', 'DOTGBP', 'ENJGBP', 'ETHGBP', 'GMTGBP', 'LINKGBP', 
        #    'LTCGBP', 'MATICGBP', 'RUNEGBP', 'SHIBGBP', 'SOLGBP', 'VETGBP', 'XRPGBP']

posframe = pd.DataFrame(symbols)
posframe.columns = ['Currency']
posframe['position'] = 0
posframe['quantity'] = 0
posframe.to_csv('positioncheck', index=False)
posframe = pd.read_csv('positioncheck')
print(posframe)

def gethourlydata(symbol):
    frame = pd.DataFrame(client.get_historical_klines(symbol, "1h", "25 hours ago UTC"))
    frame = frame[[0,4]]
    frame.columns = ['Time', 'Close']
    frame['Close'] = frame['Close'].astype(float)
    frame['Time'] = pd.to_datetime(frame['Time'], unit='ms')
    return frame

temp = gethourlydata('BTCUSDT')

def applytechnicals(df):
    df['FastSMA'] = df['Close'].rolling(2).mean()
    df['SlowSMA'] = df['Close'].rolling(25).mean()
    return df

print(applytechnicals(temp))

def changepos(curr, order, buy=True):
    if buy:
        posframe.loc[posframe.Currency == curr, 'position'] = 1
        posframe.loc[posframe.Currency == curr, 'quantity'] = float(order['executedQty'])
    else:
        posframe.loc[posframe.Currency == curr, 'position'] = 0
        posframe.loc[posframe.Currency == curr, 'quantity'] = 0
    
    return posframe

def trader(investment=15):
    for coin in posframe[posframe['position'] == 1]['Currency']:
        df = gethourlydata(coin)
        applytechnicals(df)
        lastrow = df.iloc[-1]
        if lastrow['SlowSMA'] > lastrow['FastSMA']:
            order = client.create_order(symbol=coin, side='SELL', type='MARKET', quantity=posframe[posframe['Currency'] == coin]['quantity'][0])
            print(order)
            changepos(coin, order, buy=False)
        else:
            print(f'Selling Condition for {coin} not fulfilled')
            
    
    for coin in posframe[posframe['position'] == 0]['Currency']:
        df = gethourlydata(coin)
        applytechnicals(df)
        lastrow = df.iloc[-1]
        if lastrow['FastSMA'] > lastrow['SlowSMA']:
            order = client.create_order(symbol=coin, side='BUY', type='MARKET', quoteOrderQty=investment)
            print(order)  
            changepos(coin, order, buy=True)
             
        else:
            print(f'Buying Condition for {coin} not fulfilled')
       
while True:
    trader() 










# TEST_NET = True

# # Buy or sell ETHUSDT when BTC reaches a particular value
# def buy_and_sell_ETH_at_BTC():
#     while True:
#         # error check to make sure WebSocket is working
#         if btc_price['error']:
#             # stop and restart socket (cleanup)
#             twm.stop()
#             sleep(2)
#             twm.start()
#             btc_price['error'] = False
#         else:
#             if 1000 < btc_price['BTCUSDT'] < 40000:   # bitcoin price
#                 try:
#                     print("Buying when BTCUSDTprice:",btc_price['BTCUSDT'])
#                     order = client.order_market_buy(symbol='ETHUSDT', quantity=1)
#                     pprint.pprint(order)
#                     break
#                 except Exception as e:
#                     print(e)
#                     break
#             else:
#                 try:
#                     print("Selling when BTCUSDT price:",btc_price['BTCUSDT'])
#                     order = client.order_market_sell(symbol='ETHUSDT', quantity=1)
#                     pprint.pprint(order)
#                     break
#                 except Exception as e:
#                     print(e)
#                     break
#             sleep(0.1)
            
# def btc_values_received(msg):
#     ''' Process the btc values received in the last 24 hrs '''
    
#     pprint.pprint(msg)
    
#     if msg['e'] != 'error':
#         print(msg['e'])
#         btc_price['BTCUSDT'] = float(msg['c'])
#     else:
#         btc_price['error'] = True
        
# def main():
#     pprint.pprint(client.get_account())
#     print(client.get_asset_balance(asset='BNB'))
#     eth_price = client.get_symbol_ticker(symbol="ETHUSDT")
#     print(eth_price)
#     twm.start()
#     twm.start_symbol_ticker_socket(callback=btc_values_received, symbol='BTCUSDT')
#     # wait here to receive some btc value initially through websocket callback
#     while not btc_price['BTCUSDT']:
#         sleep(0.1)
#     # call buy ETH function with a while loop to keep a track on btc price
#     buy_and_sell_ETH_at_BTC()
#     # twm.join() # to stop main thread exit.
#     twm.stop()
    
# if __name__ == "__main__":
#     if TEST_NET:
#         api_key = "4axJUrVKe1bKD3vagLtuC5PBGLBXdBRoXQStiZWWJYL4lQx9WVApsvnsa7eZhlbq"
#         api_secret = "Uy4eDemOcbnRVIg3psQJFm2W2mWebBjnmqB3imzyFx89xcgU0PDEGWr6me1V80Mv"
#         client = Client(api_key, api_secret, testnet=True)
#         print(client.get_account_status())
#         print("Using Binance TestNet server")
#     # Add btc price and instantiate ThreadedWebsocketManager()
#     btc_price = {'BTCUSDT': None, 'error': False}
#     twm = ThreadedWebsocketManager()
#     main()
#     print("TEST")
