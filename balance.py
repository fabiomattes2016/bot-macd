from binance import Client
import warnings
import time
import os
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client as SupaClient


load_dotenv()

binance_api_key: str = ""
binance_secret_key: str = ""

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

while True:
    timestamp = datetime.now()
    btc = client.get_asset_balance(asset='BTC')
    usdt = client.get_asset_balance(asset='USDT')

    supabase.table("saldos").insert({
        "btc": float(btc['free']),
        "usdt": float(usdt['free']),
        "timestamp": timestamp.strftime("%d/%m/%Y %H:%M:%S")
    }).execute()

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
    time.sleep(86400)
