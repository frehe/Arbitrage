import poloniex

api_key = ''
api_secret = ''
whitelistedWithdrawAdress = ''

BTC_whitelistedWithdrawAdress = ''
LTC_whitelistedWithdrawAdress = ''
ETH_whitelistedWithdrawAdress = ''
BCH_whitelistedWithdrawAdress = ''

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
	if (b_product == 'LTC-BTC'):
		prod_id = 'BTC_LTC'
		buy_order_number = polo.buy(prod_id, b_rate, b_size)
		return buy_order
	else:
		sys.exit('Error generating buy trade on Poloniex')

def sellTrade(s_rate, s_size, s_product):
	if (s_product == 'LTC-BTC'):
		prod_id = 'LTC-BTC'
		sell_order = polo.sell(prod_id, s_rate, s_size)
 		return sell_order
	else:
		sys.exit('Error generating sell trade on Poloniex')

def cancelOrders(product_identifier):
	order_id = polo.returnOpenOrders(currencyPair)
	return polo.cancel(product_identifier, order_id)

def getOrderInfo(order_id):
 	print('nothing')
 	return 0

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
	"Obtain balance on Poloniex for a given currency"
	print("Checking funds on Poloniex: " + currency)
	accounts_table = polo.returnBalances()
	balance = float(accounts_table[currency])
	return balance


#######################################################################################

def main():
	#result = buyTakerTrade(0.1, "LTCXBT")
	#print('Result: ' + str(result))
	print('okay')
	print(checkFunds('LTC'))


if __name__ == "__main__":
	main()
