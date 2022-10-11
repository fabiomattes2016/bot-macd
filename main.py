from config import (
    api_key_prod,
    secret_key_prod,
    api_key_test,
    secret_key_test,
    pair,
    amount,
    target,
    stop
)
from signals import Signals
from binance import Client
import pandas as pd
import time
from ta import momentum, trend
import warnings
import os
import requests
import json
import uuid
from datetime import datetime


warnings.filterwarnings("ignore")
link = "https://bot-macd-default-rtdb.firebaseio.com"
timestamp = datetime.now()
client = Client(api_key=api_key_test, api_secret=secret_key_test, testnet=True)


def get_minute_data(symbol, interval, lookback):
    frame = pd.DataFrame(client.get_historical_klines(
        symbol, interval, lookback + ' min ago UTC'))
    frame = frame.iloc[:, :6]
    frame.columns = ['Time', 'Open', 'High',
                     'Low', 'Close', 'Volume']  # type: ignore
    frame = frame.set_index('Time')
    frame.index = pd.to_datetime(frame.index, unit='ms')
    frame = frame.astype(float)

    return frame


df = get_minute_data(pair, '1m', '100')


def apply_technicals(df):
    df['%K'] = momentum.stoch(
        df.High, df.Low, df.Close, window=14, smooth_window=3)
    df['%D'] = df['%K'].rolling(3).mean()
    df['rsi'] = momentum.rsi(df.Close, window=14)
    df['macd'] = trend.macd_diff(df.Close)
    df.dropna(inplace=True)


apply_technicals(df)

inst = Signals(df, 25)

inst.decide()


def strategy(pair, qty, open_position=False):
    buyprice: float = 0.0
    df = get_minute_data(pair, '1m', '100')
    apply_technicals(df)
    inst = Signals(df, 25)
    inst.decide()

    data = {
        "price": float(df.Close.iloc[-1])
    }

    requests.patch(
        f"{link}/currentPrice/1ca584fc-80a3-45d0-b9ec-5ca0da8fc570/.json", data=json.dumps(data))

    os.system('cls')
    print(f'Current Close -> ' + str(df.Close.iloc[-1]))

    if df.Buy.iloc[-1]:
        order = client.create_order(
            symbol=pair, side='BUY', type='MARKET', quantity=qty)
        buyprice = float(order['fills'][0]['price'])

        data = {
            "buyprice": buyprice,
            "targetPrice": buyprice * target,
            "stopPrice": buyprice * stop,
            "pair": pair,
            "quantity": qty,
            "timestamp": timestamp.strftime("%d/%m/%Y %H:%M:%S"),
            "key": str(uuid.uuid4())
        }

        requests.post(f"{link}/compras/.json", data=json.dumps(data))

        open_position = True
        print('ORDEM DE COMPRA LANÇADA')

    while open_position:
        time.sleep(0.5)
        df = get_minute_data(pair, '1m', '2')

        data = {
            "price": float(df.Close.iloc[-1])
        }

        requests.patch(
            f"{link}/currentPrice/1ca584fc-80a3-45d0-b9ec-5ca0da8fc570/.json", data=json.dumps(data))

        os.system('cls')
        print(f'Current Close  -> ' + str(df.Close.iloc[-1]))
        print(f'Current Target -> ' + str(buyprice * target))
        print(f'Current Stop   -> ' + str(buyprice * stop))

        if df.Close[-1] <= buyprice * stop or df.Close[-1] >= target * buyprice:
            order = client.create_order(
                symbol=pair, side='SELL', type='MARKET', quantity=qty)

            data = {
                "buyPrice": float(df.Close.iloc[-1]),
                "targetPrice": buyprice * target,
                "stopPrice": buyprice * stop,
                "pair": pair,
                "quantity": qty,
                "timestamp": timestamp.strftime("%d/%m/%Y %H:%M:%S"),
                "key": str(uuid.uuid4())
            }

            requests.post(f"{link}/vendas/.json", data=json.dumps(data))

            print('ORDEM DE VENDA LANÇADA')
            break


while True:
    strategy(pair, amount)
    time.sleep(0.5)
