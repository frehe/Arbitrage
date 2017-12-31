import poloniex

api_key = ''
api_secret = ''

#p = poloniex_background.poloniex(api_key,api_secret)

polo = poloniex.Poloniex(api_key, api_secret)

#print(p.returnOrderBook('BTC_LTC'))


#print(polo.returnTicker()['BTC_ETH'])


#######################################################################################


def priceCheck(pair):
	"Returns an array of bid and ask for a given currency pair"
	print("Checking prices on Poloniex for " + pair)
	if pair == 'LTC-BTC':
		highest_bid = float(polo.returnTicker()['BTC_LTC']['highestBid'])
		lowest_ask = float(polo.returnTicker()['BTC_LTC']['lowestAsk'])
	else:
		sys.exit('Could not get Poloniex price data for ' + pair)
		#highest_bid = lowest_ask = 0
	
	result = [highest_bid, lowest_ask]
	return result


#######################################################################################


def buyTrade(b_rate, b_size, b_product):
	buy_order_number = polo.buy(b_product, b_rate, b_size)
	return buy_order
def sellTrade(s_rate, s_size, s_product):
 	sell_order = polo.sell(s_product, s_rate, s_size)
 	return sell_order
def cancelOrders(product_identifier):
	order_id = polo.returnOpenOrders(currencyPair)
	return polo.cancel(product_identifier, order_id)
def getOrderInfo(order_id):
 	print('nothing')
 	return 0


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
