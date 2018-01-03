import json


with open('GDAX_fake_account.json', 'w') as fp:
    json.dump({'BTC': 0.0, 'LTC': 0.7, 'ETH': 0.0, 'BCH': 0.0, 'EUR': 0.0}, fp)
with open('GDAX_fake_account.json', 'r') as fp:
    data = json.load(fp)
    print(data)

with open('Kraken_fake_account.json', 'w') as fp:
    json.dump({'BTC': 0.01, 'LTC': 0.0, 'ETH': 0.0, 'BCH': 0.0, 'EUR': 0.0}, fp)
with open('Kraken_fake_account.json', 'r') as fp:
    data = json.load(fp)
    print(data)

with open('Poloniex_fake_account.json', 'w') as fp:
    json.dump({'BTC': 0.0, 'LTC': 0.0, 'ETH': 0.0, 'BCH': 0.0, 'EUR': 0.0}, fp)
with open('Poloniex_fake_account.json', 'r') as fp:
    data = json.load(fp)
    print(data)
