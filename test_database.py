import requests
import json
import uuid
from datetime import datetime


link = "https://bot-macd-default-rtdb.firebaseio.com/"

timestamp = datetime.now()

# POST
data = {
    "buyprice": 20550.00,
    "pair": "BTCBUSD",
    "quantity": 0.001,
    "timestamp": timestamp.strftime("%d/%m/%Y %H:%M:%S"),
    "key": str(uuid.uuid4())
}

requisicao = requests.post(f"{link}/compras/.json", data=json.dumps(data))

print(requisicao)
print("------------------------------------------")
print(requisicao.text)
