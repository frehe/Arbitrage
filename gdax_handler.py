#!/usr/bin/python
import gdax
import json
import base64, hashlib, hmac, time

api_key = ''
api_passphrase = ''
api_secret = ''

BTC_whitelistedWithdrawAdress = ''
LTC_whitelistedWithdrawAdress = ''
ETH_whitelistedWithdrawAdress = ''
BCH_whitelistedWithdrawAdress = ''

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
	if currency == 'EUR':
		account = auth_client.get_accounts()[0];
		# Make sure that the order of display in gdax's returned json data (i.e. EUR stands at index 0) is consistent. If not, abort.
		if account['currency'] == 'EUR':
			return float(account['balance'])
		else:
			sys.exit('Error trying to obtain current funds (EUR) on gdax')
	elif currency == 'ETH':
		account = auth_client.get_accounts()[1];
		if account['currency'] == 'ETH':
			return float(account['balance'])
		else:
			sys.exit('Error trying to obtain current funds (ETH) on gdax')
	elif currency == 'BTC':
		account = auth_client.get_accounts()[2];
		if account['currency'] == 'BTC':
			return float(account['balance'])
		else:
			sys.exit('Error trying to obtain current funds (BTC) on gdax')
	elif currency == 'LTC':
		account = auth_client.get_accounts()[3];
		if account['currency'] == 'LTC':
			return float(account['balance'])
		else:
			sys.exit('Error trying to obtain current funds (LTC) on gdax')
	elif currency == 'BCH':
		account = auth_client.get_accounts()[4];
		if account['currency'] == 'BCH':
			return float(account['balance'])
		else:
			sys.exit('Error trying to obtain current funds (BCH) on gdax')
	else:
		sys.exit('Could not get current funds on gdax')


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

	if ((adr == BTC_whitelistedWithdrawAdress) & (cur == 'BTC')):
		# BTC Withdrawal
		pass
	elif ((adr == LTC_whitelistedWithdrawAdress) & (cur == 'LTC')):
		# LTC Withdrawal
		pass
	elif ((adr == ETH_whitelistedWithdrawAdress) & (cur == 'ETH')):
		# ETH Withdrawal
		pass
	elif ((adr == BCH_whitelistedWithdrawAdress) & (cur == 'BCH')):
		# BCH Withdrawal
		pass
	pass

#######################################################################################

'''

def main():
	#prices = priceCheck('LTC-EUR')
	#print(prices)

	#print(sellLimitTrade(0.2, 0.01, 'LTC-BTC'))
	#iddd = buyLimitTrade(0.0001, 0.01, 'LTC-BTC')['id']
	#print(getOrderInfo(iddd))
	#print(cancelOrders('LTC-BTC'))


if __name__ == "__main__":
	main()
'''
