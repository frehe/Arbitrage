#!/usr/bin/python
import poloniex
import sys, json
import arbitrage_trader
import numpy as np
from random import randint

api_key = ''
api_secret = ''

polo = poloniex.Poloniex(api_key, api_secret)

#######################################################################################


def priceCheck(pair):
	"Returns an array of bid and ask for a given currency pair"
	print("Checking prices on Poloniex for " + pair)
	if pair == 'LTC-BTC':
		highest_bid = float(polo.returnTicker()['BTC_LTC']['highestBid'])
		lowest_ask = float(polo.returnTicker()['BTC_LTC']['lowestAsk'])
	else:
		sys.exit('Could not get Poloniex price data for ' + pair)

	result = [highest_bid, lowest_ask]
	return result


#######################################################################################


def buyTrade(b_rate, b_size, b_product):
	if (arbitrage_trader.backtesting == True):
		with open('Kraken_fake_account.json', 'r') as fp:
			data = json.load(fp)
			buyCur = b_product[:3]
			baseCur = b_product[4:]
			new_buy_cur_val = data[buyCur] + b_size
			new_base_cur_val = data[baseCur] - b_size * b_price - arbitrage_trader.buyFee * b_size * b_price
			time.sleep(randint(2,40))
		with open('Kraken_fake_account.json', 'w') as fp:
			data[buyCur] = new_buy_cur_val
			data[baseCur] = new_base_cur_val
			json.dump(data, fp)
	else:
		if (b_product == 'LTC-BTC'):
			prod_id = 'BTC_LTC'
			buy_order_number = polo.buy(prod_id, b_rate, b_size)
			return buy_order_number
		else:
			sys.exit('Error generating buy trade on Poloniex')

def sellTrade(s_rate, s_size, s_product):
	if (arbitrage_trader.backtesting == True):
		with open('Kraken_fake_account.json', 'r') as fp:
			data = json.load(fp)
			buyCur = b_product[:3]
			baseCur = b_product[4:]
			new_buy_cur_val = data[buyCur] + s_size
			new_base_cur_val = data[baseCur] - s_size * s_price - arbitrage_trader.buyFee * s_size * s_price
			time.sleep(randint(2,40))
		with open('Kraken_fake_account.json', 'w') as fp:
			data[buyCur] = new_buy_cur_val
			data[baseCur] = new_base_cur_val
			json.dump(data, fp)
	else:
		if(s_product == 'LTC-BTC'):
			prod_id = 'BTC_LTC'
			sell_order_number = polo.sell(prod_id, s_rate, s_size)
			return sell_order_number
		else:
			sys.exit('Error generating sell trade on Poloniex')

def cancelOrders(product_identifier):
	order_id = polo.returnOpenOrders(currencyPair)
	return polo.cancel(product_identifier, order_id)

def getOrderInfo(order_id):
 	print('nothing')
 	return 0

def withdrawToAdress(adr, to_exchange, cur, amount):
	"Double check every withdrawal to be sure and then withdraw"

	print('Withdrawing ' + str(amount) + cur + ' to ' + to_exchange + ' at ' + adr)

	if (arbitrage_trader.backtesting == True):
		# Remove fake funds from GDAX
		with open('Poloniex_fake_account.json', 'r') as fp:
			data = json.load(fp)
			new_cur_val = data[cur] - amount
		with open('Poloniex_fake_account.json', 'w') as fp:
			data[cur] = new_cur_val
			json.dump(data, fp)
		# Send fake funds to to_exchange
		with open(to_exchange + '_fake_account.json', 'r') as fp:
			data = json.load(fp)
			new_cur_val = data[cur] + amount - arbitrage_trader.buyCurrencyTransferFee
		with open(to_exchange + '_fake_account.json', 'w') as fp:
			data[cur] = new_cur_val
			json.dump(data, fp)
	else:
		result =  polo.withdraw(currency = cur, amount = str(amount), address = adr, paymentId=False)
		print(result)

#######################################################################################


def checkFunds(currency):
	"Obtain balance on Poloniex for a given currency"
	print("Checking funds on Poloniex: " + currency)

	if (arbitrage_trader.backtesting == True):
		with open('Poloniex_fake_account.json', 'r') as fp:
			return float(json.load(fp)[currency])
	else:
		accounts_table = polo.returnBalances()
		balance = float(accounts_table[currency])
		return balance


#######################################################################################

def main():
	#result = buyTakerTrade(0.1, "LTCXBT")
	#print('Result: ' + str(result))
	#print('okay')
	#print('Funds LTC: ' + str(checkFunds('LTC')))
	#withdrawToAdress('LMVW3R4FFrM4Bgyg9UqaxK5gkQdVYb28QK', 'LTC', 0.0011)
	pass


if __name__ == "__main__":
	main()
