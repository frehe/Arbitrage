#!/usr/bin/python
import gdax
import json
import base64, hashlib, hmac, time, sys

api_key = ''
api_passphrase = ''
api_secret = ''

auth_client = gdax.AuthenticatedClient(api_key, api_secret, api_passphrase)

#######################################################################################


def priceCheck(pair):
	"Returns an array of bid and ask for a given currency pair"
	print("Checking prices on GDAX for " + pair)
	if pair == 'LTC-EUR':
		highest_bid = float(auth_client.get_product_ticker(product_id='LTC-EUR')['bid'])
		lowest_ask = float(auth_client.get_product_ticker(product_id='LTC-EUR')['ask'])
	elif pair == 'LTC-BTC':
		highest_bid = float(auth_client.get_product_ticker(product_id='LTC-BTC')['bid'])
		lowest_ask = float(auth_client.get_product_ticker(product_id='LTC-BTC')['ask'])
	else:
		sys.exit('Could not get gdax price data for gdax')

	result = [highest_bid, lowest_ask]
	return result


#######################################################################################


def performTrade(pair,buy_sell,type):
	"Perform a trade on gdax"
	return 11


#######################################################################################


def checkFunds(currency):
	"Obtain balance on gdax for a given currency"

	print("Checking funds on GDAX: " + currency)

	all_accounts = auth_client.get_accounts()
	# There are (currently) 5 currencies on GDAX wallets:
	for current_account in all_accounts:
		if (current_account['currency'] == currency):
			return float(current_account['balance'])

	sys.exit('Error trying to obtain current funds ' + currency + ' on GDAX')


#######################################################################################

def getQuoteIncrement(tradingPair):
	products = auth_client.get_products()
	for current_pair in products:
		if (current_pair['id'] == tradingPair):
			return float(current_pair['quote_increment'])

	sys.exit('Unable to fetch quote increment data for ' + tradingPair)

#######################################################################################


def buyLimitTrade(b_price, b_size, b_product):
	if (b_product == 'LTC-BTC'):
		return auth_client.buy(price = b_price, size = b_size, product_id = b_product, type = 'limit', post_only = True)
	else:
		sys.exit('Error generating limit sell trade on GDAX')

def sellLimitTrade(s_price, s_size, s_product):
	if (s_product == 'LTC-BTC'):
		return auth_client.sell(price = s_price, size = s_size, product_id = s_product, type = 'limit', post_only = True)
	else:
		sys.exit('Error generating limit sell trade on GDAX')

def cancelOrders(product_identifier):
	return auth_client.cancel_all(product = product_identifier)

def getOrderInfo(order_id):
	return auth_client.get_order(order_id)

def withdrawToCoinbase(cur, amount):
	pass

def withdrawToAdress(adr, cur, amount):
	"Double check every withdrawal to be sure and then withdraw"

	print('Withdrawing ' + str(amount) + cur + ' to ' + adr)

	result = auth_client.crypto_withdraw(amount = str(amount), currency = cur, crypto_address = adr)
	print(str(result))


#######################################################################################



def main():
	#prices = priceCheck('LTC-EUR')
	#print(prices)

	#print(sellLimitTrade(0.2, 0.01, 'LTC-BTC'))
	#iddd = buyLimitTrade(0.0001, 0.01, 'LTC-BTC')['id']
	#print(getOrderInfo(iddd))
	#print(cancelOrders('LTC-BTC'))
	#print(checkFunds('LTC'))
	#print(str(getQuoteIncrement('LTC-BTC') * 100))
	pass

if __name__ == "__main__":
	main()
