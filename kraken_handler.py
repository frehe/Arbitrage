#!/usr/bin/python
import krakenex
from pykrakenapi import KrakenAPI
import sys, json
import arbitrage_trader
import numpy as np
from random import randint

api_key = ''
api_secret = ''

api = krakenex.API(key = api_key, secret = api_secret)
k = KrakenAPI(api)

#######################################################################################


def priceCheck(pair):
	"Returns an array of bid and ask for a given currency pair"
	print("Checking prices on Kraken for " + pair)
	if pair == 'LTC-EUR':
		highest_bid = float(k.get_ticker_information("LTCEUR")['b'][0][0])
		lowest_ask = float(k.get_ticker_information("LTCEUR")['a'][0][0])
	elif pair == 'LTC-BTC':
		highest_bid = float(k.get_ticker_information("LTCXBT")['b'][0][0])
		lowest_ask = float(k.get_ticker_information("LTCXBT")['a'][0][0])
	else:
		sys.exit('Could not get kraken price data for ' + pair)

	result = [highest_bid, lowest_ask]
	return result


#######################################################################################


def buyTakerTrade(b_price, b_size, b_product):
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
			prod_id = 'LTCXBT'
			buy_order = k.add_standard_order(prod_id, type = 'buy', ordertype = 'market', volume = b_size, price=None, price2=None, leverage=None, oflags=None, starttm=0, expiretm=0, userref=None, validate=True, close_ordertype=None, close_price=None, close_price2=None, otp=None, trading_agreement='agree')
			return buy_order
		else:
			sys.exit('Error generating buy trade on Kraken')

def sellTakerTrade(s_price, s_size, s_product):
	if (arbitrage_trader.backtesting == True):
		with open('Kraken_fake_account.json', 'r') as fp:
			data = json.load(fp)
			buyCur = b_product[:3]
			baseCur = b_product[4:]
			new_buy_cur_val = data[buyCur] - s_size
			new_base_cur_val = data[baseCur] + s_size * s_price - arbitrage_trader.buyFee * s_size * s_price
			time.sleep(randint(2,40))
		with open('Kraken_fake_account.json', 'w') as fp:
			data[buyCur] = new_buy_cur_val
			data[baseCur] = new_base_cur_val
			json.dump(data, fp)
	else:
		if (s_product == 'LTC-BTC'):
			prod_id = 'LTCXBT'
			sell_order = k.add_standard_order(prod_id, type = 'sell', ordertype = 'market', volume = s_size, price=None, price2=None, leverage=None, oflags=None, starttm=0, expiretm=0, userref=None, validate=True, close_ordertype=None, close_price=None, close_price2=None, otp=None, trading_agreement='agree')
			return sell_order
		else:
			sys.exit('Error generating sell trade on Kraken')

def cancelOrders(product_identifier):
 	print('nothing')

def getOrderInfo(order_id):
 	print('nothing')

def withdrawToAdress(adr, to_exchange, cur, amount):
	"Double check every withdrawal to be sure and then withdraw"

	print('Withdrawing ' + str(amount) + cur + ' to ' + to_exchange + ' at ' + adr)

	if (arbitrage_trader.backtesting == True):
		# Remove fake funds from GDAX
		with open('Kraken_fake_account.json', 'r') as fp:
			data = json.load(fp)
			new_cur_val = data[cur] - amount
		with open('Kraken_fake_account.json', 'w') as fp:
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
		result = api.query_private('Withdraw', data = {'asset': cur, 'key': to_exchange, 'amount': str(amount)})
		print(result)

#######################################################################################


def checkFunds(currency):
	"Obtain balance on Kraken for a given currency"
	print("Checking funds on Kraken: " + currency)

	if (arbitrage_trader.backtesting == True):
		with open('Kraken_fake_account.json', 'r') as fp:
			return float(json.load(fp)[currency])
	else:
		accounts_table = k.get_account_balance(otp=None)
		currency_indices = list(accounts_table.index)

		currency_kr = ''
		if currency == 'EUR':
			currency_kr = 'ZEUR'
		elif currency == 'ETH':
			currency_kr = 'XETH'
		elif currency == 'BTC':
			currency_kr = 'XXBT'
		elif currency == 'LTC':
			currency_kr = 'XLTC'
		elif currency == 'BCH':
			currency_kr = 'XBCH'
		'''
		if currency == 'EUR':
			currency_kr = 'ZEUR'
			# Make sure that the order of display in kraken's returned data (i.e. EUR stands at index 3) is consistent. If not, abort.
			if currency_indices[3] == 'ZEUR':
				balance = float(accounts_table['vol'][3])
				return balance
			else:
				sys.exit('Error trying to obtain current funds (EUR) on kraken')
		elif currency == 'ETH':
			if currency_indices[0] == 'XETH':
				balance = float(accounts_table['vol'][0])
				return balance
			else:
				sys.exit('Error trying to obtain current funds (ETH) on kraken')
		elif currency == 'BTC':
			if currency_indices[2] == 'XXBT':
				balance = float(accounts_table['vol'][2])
				return balance
			else:
				sys.exit('Error trying to obtain current funds (BTC) on kraken')
		elif currency == 'LTC':
			if currency_indices[1] == 'XLTC':
				balance = float(accounts_table['vol'][1])
				return balance
			else:
				sys.exit('Error trying to obtain current funds (LTC) on kraken')
		else:
			sys.exit('Could not get current funds on kraken')
		'''
		for i in range(0, len(currency_indices), 1):
			if (currency_indices[i] == currency_kr):
				balance = float(accounts_table['vol'][i])
				return balance
		sys.exit('Could not get current funds on kraken')

#######################################################################################
'''
def main():
	#result = buyTakerTrade(0.1, "LTCXBT")
	#print('Result: ' + str(result))
	print('LTC funds: ' + str(checkFunds('LTC')))
	#withdrawToAdress('GDAX', 'LTC', 0.0011)


if __name__ == "__main__":
	main()
'''
