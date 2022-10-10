from config import api_key_prod, secret_key_prod, api_key_test, secret_key_test
from binance import Client
import warnings
import time
import os
from datetime import datetime
import requests
import json
import uuid


warnings.filterwarnings("ignore")
client = Client(api_key=api_key_test, api_secret=secret_key_test, testnet=True)

link = "https://bot-macd-default-rtdb.firebaseio.com/"

while True:
    timestamp = datetime.now()
    btc = client.get_asset_balance(asset='BTC')
    usdt = client.get_asset_balance(asset='USDT')

    data = {
        "btc": btc['free'],
        "usdt": usdt['free'],
        "timestamp": timestamp.strftime("%d/%m/%Y %H:%M:%S")
    }

    requests.patch(
        f"{link}/saldos/70686aee-0a32-4bb4-8a6f-2268a23cff68/.json", data=json.dumps(data))

    os.system('cls')
    print('-------------------------------------------')
    print('Actual Balances')
    print('-------------------------------------------')
    print(f'BTC  -> ' + str(btc['free']))
    print(f'USDT -> ' + str(usdt['free']))
    print('-------------------------------------------')
    print('Total in Orders')
    print('-------------------------------------------')
    print(f'BTC  -> ' + str(btc['locked']))
    print(f'USDT -> ' + str(usdt['locked']))
    print('-------------------------------------------')
    time.sleep(120)