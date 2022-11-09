from signals import Signals
from binance import Client
import pandas as pd
import time
from ta import momentum, trend
import warnings
import os
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client as SupaClient

load_dotenv()

binance_api_key: str = ""
binance_secret_key: str = ""

pair: str = os.environ.get("PAIR")
amount: float = float(os.environ.get("AMOUNT"))
target: float = float(os.environ.get("TARGET"))
stop: float = float(os.environ.get("STOP"))

environment: str = os.environ.get("ENVIRONMENT")

if environment == "development":
    binance_api_key: str = os.environ.get("BINANCE_API_KEY_TEST")
    binance_secret_key: str = os.environ.get("BINANCE_SECRET_KEY_TEST")
else:
    binance_api_key: str = os.environ.get("BINANCE_API_KEY")
    binance_secret_key: str = os.environ.get("BINANCE_SECRET_KEY")


warnings.filterwarnings("ignore")
client = Client(api_key=binance_api_key,
                api_secret=binance_secret_key, testnet=True)

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: SupaClient = create_client(url, key)


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
    timestamp = datetime.now()
    buyprice: float = 0.0
    df = get_minute_data(pair, '1m', '100')
    apply_technicals(df)
    inst = Signals(df, 25)
    inst.decide()

    supabase.table("current_price").update({
        "price": float(df.Close.iloc[-1])
    }).eq("id", "24b8b5f0-8e76-4cbe-9f1e-6841fd03fa3a").execute()

    os.system('cls')
    print(f'Current Close -> ' + str(df.Close.iloc[-1]))

    if df.Buy.iloc[-1]:
        order = client.create_order(
            symbol=pair, side='BUY', type='MARKET', quantity=qty)
        buyprice = float(order['fills'][0]['price'])

        supabase.table("compras").insert({
            "buyPrice": buyprice,
            "targetPrice": buyprice * target,
            "stopPrice": buyprice * stop,
            "pair": pair,
            "quantity": qty,
            "timestamp": timestamp.strftime("%d/%m/%Y %H:%M:%S")
        }).execute()

        open_position = True
        print('ORDEM DE COMPRA LANÇADA')

    while open_position:
        time.sleep(0.5)
        df = get_minute_data(pair, '1m', '2')

        os.system('cls')
        print(f'Current Close  -> ' + str(df.Close.iloc[-1]))
        print(f'Current Target -> ' + str(buyprice * target))
        print(f'Current Stop   -> ' + str(buyprice * stop))

        supabase.table("current_price").update({
            "price": float(df.Close.iloc[-1])
        }).eq("id", "24b8b5f0-8e76-4cbe-9f1e-6841fd03fa3a").execute()

        if df.Close[-1] <= buyprice * stop or df.Close[-1] >= target * buyprice:
            order = client.create_order(
                symbol=pair, side='SELL', type='MARKET', quantity=qty)

            supabase.table("vendas").insert({
                "sellPrice": float(df.Close.iloc[-1]),
                "targetPrice": buyprice * target,
                "stopPrice": buyprice * stop,
                "pair": pair,
                "quantity": qty,
                "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }).execute()

            print('ORDEM DE VENDA LANÇADA')
            break


while True:
    strategy(pair, amount)
    time.sleep(0.5)
