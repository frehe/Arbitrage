#!/usr/bin/python
import krakenex
from pykrakenapi import KrakenAPI

api_key = ''
api_secret = ''
whitelistedWithdrawAdress = ''

BTC_whitelistedWithdrawAdress = ''
LTC_whitelistedWithdrawAdress = ''
ETH_whitelistedWithdrawAdress = ''
BCH_whitelistedWithdrawAdress = ''

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
		#highest_bid = lowest_ask = 0

	result = [highest_bid, lowest_ask]
	return result


#######################################################################################


def buyTakerTrade(b_size, b_product):
	if (b_product == 'LTC-BTC'):
		prod_id = 'LTCXBT'
		buy_order = k.add_standard_order(prod_id, type = 'buy', ordertype = 'market', volume = b_size, price=None, price2=None, leverage=None, oflags=None, starttm=0, expiretm=0, userref=None, validate=True, close_ordertype=None, close_price=None, close_price2=None, otp=None, trading_agreement='agree')
		return buy_order
	else:
		sys.exit('Error generating buy trade on Kraken')

def sellTakerTrade(s_size, s_product):
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


def checkFunds(currency):
	"Obtain balance on Kraken for a given currency"
	print("Checking funds on Kraken: " + currency)
	accounts_table = k.get_account_balance(otp=None)
	currency_indices = list(accounts_table.index)
	if currency == 'EUR':
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


#######################################################################################

def main():
	result = buyTakerTrade(0.1, "LTCXBT")
	print('Result: ' + str(result))



if __name__ == "__main__":
	main()
