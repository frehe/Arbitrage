#!/usr/bin/python
import gdax
import json
import base64, hashlib, hmac, time, math
import gdax_handler
import kraken_handler


'''
################################# EXPLANATIONS #################################
buyExchange : Exchange where an altcoin, e.g. LTC, is bought, and a base currency, e.g. BTC, is sold
sellExchange : Exchange where an altcoin is sold to obtain a base currency, e.g. sell LTC for BTC
baseCurrency : The base currency. Generally BTC
buyCurrency : The altcoin/token - e.g. LTC,BCH,ETH
################################################################################
'''

#######################################################################################


def getAllPrices(baseCur, buyCur, buyExchange, sellExchange):
	"Obtain all relevant buy and sell prices on the given exchanges"

	buy_rate = 0
	# Taker orders will execute on lowest ask <- buy rate
	if (buyExchange == 'Kraken'):
		kraken_prices = kraken_handler.priceCheck(buyCur + '-' + baseCur)
		buy_rate = kraken_prices[1]
	elif (buyExchange == 'Poloniex'):
		poloniex_prices = poloniex_handler.priceCheck(buyCur + '-' + baseCur)
		buy_rate = poloniex_prices[1]
	else:
		sys.exit('Could not recognize buyExchange')

	# Maker sell will execute on lowest ask
	############################# TODO
	############################# Set sell_rate to highest bid + smallest increase
	############################# Will increase likelihood of a fast maker sell
	############################# Disadvantage: Worse price

	sell_rate = 0
	if (sellExchange == 'GDAX'):
		gdax_prices = gdax_handler.priceCheck(buyCur + '-' + baseCur)
		sell_rate = gdax_prices[1]
	else:
		sys.exit('Could not recognize sellExchange')

	# For testing purposes
	#buy_rate = sell_rate * 0.995

	return [buy_rate, sell_rate]


#######################################################################################


def performArbitrageTrade(baseCur, buyCur, buy_amount, sell_amount, buyPrice, sellPrice, buyExchange, sellExchange):
	"The actual trading procedure"

	# Buy trade
	buy_message = ''
	buy_id = 0
	if (buyExchange == 'Kraken'):
		buy_message = kraken_handler.buyTakerTrade(buy_amount, buyCur + '-' + baseCur)
		buy_id = buy_message['txid'][0]
	elif (buyExchange == 'Poloniex'):
		buy_message = poloniex_handler.buyTrade(buyPrice, buy_amount, buyCur + '-' + baseCur):
		###################TODO: Add expression for buy_id
	else:
		sys.exit('Could not recognize buyExchange during trade')

	# Sell trade
	sell_message = ''
	sell_id = 0
	if (sellExchange == 'GDAX'):
		sell_message = gdax_handler.sellLimitTrade(sellPrice, sell_amount, buyCur + '-' + baseCur)
		sell_id = sell_message['id']
	else:
		sys.exit('Could not recognize sellExchange during trade')

	return [buy_id, sell_id] # Success


#######################################################################################


def checkBackOnOrders(buy_id, sell_id):
	"Checks whether the generated trades have been settled"


	pass


#######################################################################################


def checkProfitability(baseCur, buyCur, buyFee, sellFee, baseCurTransferFee, buyCurTransferFee, buyExchange, sellExchange):
	"Determine whether the current arbitrage gap is profitable under all given fees etc."

	'''
	# Obtain currency balances
	baseCurrencyAmount = 0
	if (buyExchange == 'Kraken'):
		baseCurrencyAmount = kraken_handler.checkFunds(baseCur)
	elif (buyExchange == 'Poloniex'):
		baseCurrencyAmount = poloniex_handler.checkFunds(baseCur)
	else
		sys.exit('Could not recognize buyExchange')

	buyCurrencyAmount = gdax_handler.checkFunds(buyCur)
	'''

	# For testing purposes
	baseCurrencyAmount = 5
	buyCurrencyAmount = 300

	print('Have ' + str(baseCurrencyAmount) + baseCur + ' on ' + buyExchange)
	print('Have ' + str(buyCurrencyAmount) + buyCur + ' on ' + sellExchange)

	#############################
	# Fetch current price data

	[buy_rate, sell_rate] = getAllPrices(baseCur, buyCur, buyExchange, sellExchange)

	print('Sell rate: ' + str(sell_rate) + ' on ' + sellExchange)
	print('Buy rate: ' + str(buy_rate) + ' on ' + buyExchange)

	#############################


	'''
	By inspection of the problem, it follows that on both sides, the same profit margin should be aimed for.
	Mathematical analysis leads to the expression (rate1 * (LTC_amount)^2) - (LTC_amount * withdraw_fee_GDAX) = (BTC_amount)^2 / rate2) - (BTC_amount * withdraw_fee_Kraken) if LTC is at GDAX and BTC at Kraken and rate1 at Kraken and rate2 at GDAX. -> Plus transfer fee considerations!
	Thus, rate1 < rate2 must also be provided.
	In that case, it becomes an easy task.
	Take LTC Amount and calculate BTC amount necessary. If that BTC amount is below or equal to the current Kraken balance, take that amount
	If not, take BTC amount and calculate how much LTC should be sold. It must be that this amount is less than the LTC balance. Take that amount.
	'''
	if (baseCurrencyAmount < 0.0016) | (buyCurrencyAmount < 0.1):
		print('Not enough funds in account. Thresholds are set to avoid trading with too small amounts, as this is never profitable.')
		return 0
	elif buy_rate < sell_rate:
		print('Exchange rates are favorable. Good!')
		# Assume there is enough base currency at the buyExchange (Kraken). Then calculate how much of it is needed.
		baseCurNeeded = ((buyCurTransferFee * buy_rate) / (2 * (1 - buyFee))) + math.sqrt(((buyCurTransferFee * buy_rate) / (2 * (1 - buyFee)))**2 + (sell_rate * buy_rate * buyCurrencyAmount**2 * (1 - sellFee) / (1 - buyFee)) - ((baseCurTransferFee * buyCurrencyAmount * buy_rate) / (1 - buyFee)))
		print('BTC needed at Kraken if all LTC at GDAX were sold: ' + str(baseCurNeeded) + baseCur)
		# Assume there is enough buy currency (LTC) at the sellExchange (GDAX). Then calculate how much of it is needed.
		buyCurNeeded = ((baseCurTransferFee) / (2 * sell_rate * (1 - sellFee))) + math.sqrt((baseCurTransferFee / (2 * sell_rate * (1 - sellFee)))**2 + (((baseCurrencyAmount)**2 * (1 - buyFee)) / (buy_rate * sell_rate * (1 - sellFee))) - (buyCurTransferFee * baseCurrencyAmount / (sell_rate * (1 - sellFee))))
		print('LTC needed at GDAX if all BTC at Kraken were sold: ' + str(buyCurNeeded) + buyCur)

		if baseCurNeeded <= baseCurrencyAmount:
			baseCurrencyAmount = baseCurNeeded
			print('Sell only as much BTC on Kraken as needed')
		elif buyCurNeeded <= buyCurrencyAmount:
			buyCurrencyAmount = buyCurNeeded
			print('Sell only as much LTC on GDAX as needed')

		# How much could be bought an sold under the given conditions?
		couldBeBought = baseCurrencyAmount / buy_rate * (1 - buyFee)
		couldBeSold = buyCurrencyAmount * sell_rate * (1 - sellFee)

		print('Could buy ' + str(couldBeBought) + buyCur + ' on ' + buyExchange)
		print('Could sell ' + buyCur + ' to get ' + str(couldBeSold) + baseCur + ' on ' + sellExchange)

		# After transfer, what remains?
		baseCurAfterTransfer = couldBeSold - baseCurTransferFee
		buyCurAfterTransfer = couldBeBought - buyCurTransferFee

		print('Makes ' + str(baseCurAfterTransfer) + baseCur + ' after transfer')
		print('Makes ' + str(buyCurAfterTransfer) + buyCur + ' after transfer')

		# Is it profitable?
		buyCurProfit = buyCurAfterTransfer/buyCurrencyAmount
		baseCurProfit = baseCurAfterTransfer/baseCurrencyAmount

		print('This is a profit of ' + str(((buyCurProfit - 1) * 100)) + '% in ' + buyCur)
		print('This is a profit of ' + str(((baseCurProfit - 1) * 100)) + '% in ' + baseCur)

		# We want both profits to be definitely positive and at least one of them should be more than 0.1%
		# This is a little redundant since from the above calculations it will follow that profits are symmetric on both exchanges
		if (((buyCurProfit >= 1) & (baseCurProfit >= 1)) & ((buyCurProfit > 1.001) | (baseCurProfit > 1.001))):
			print('Process is profitable!')
			return [buy_rate, sell_rate, baseCurrencyAmount, buyCurrencyAmount, couldBeBought, couldBeSold] # which means 'profitable'
		else:
			print('Process is not profitable enough due to too small of a price gap')
			return [0, 0, 0, 0, 0, 0]

	else:
		print('Exchange rates are not favorable')
		# IMPORTANT: THERE COULD BE SEVERAL REASONS FOR THIS OUTCOME
		# ONE REASON IS THAT THE TRADE IS ASYMMETRIC, I.E. TOO MUCH OF ONE CURRENCY IS
		# BEING TRIED TO BE BOUGHT
		# IF THIS PERSISTS TO BE A PROBLEM, FIX IT WITHIN THIS FUNCTION RESPECTIVELY THE
		# TRADING FUNCTION
		return [0, 0, 0, 0, 0, 0] # which means 'unprofitable' -> do not perform trade!


#######################################################################################



#######################################################################################

'''
def buyBack(sell_message):
	"Try to limit buy back all currency that has been filled only partially"
	product = sell_message['product']
	amount = float(sell_message['filled_size'])
	highestBid = gdax_handler.priceCheck(product)[0]

	buy_message = gdax_handler.buyLimitTrade(highestBid, amount, product)

	while (buy_message['settled'] == False):
		# Wait until the order has been bought back
		print('Trying to buy back sell order...')
		time.sleep(2)

	# Buyback was successful. Start anew.
	return 0
'''

#######################################################################################

'''
def checkBackOnSellOrder(sell_id, sell_message):
	info = gdax_handler.getOrderInfo(sell_id)

	if (info['settled'] == True):
		# Great, the limit order has been filled! Now, take the buy order at buyExchange (Kraken)
		print('Great, the limit sell order has been filled.')
		return 1
	elif ((info['settled'] == False) & (info['filled_size'] == 0)):
		# Order was not filled at all. Cancel everything.
		print('Order was not filled at all. Cancel everything.')

		return 0
	else:
		# Order was only partially filled. Abort.
		'''
		The most elegant solution would be to stop the arbitrage and try to limit buy back
		the buyCurrency that has been sold.
		'''
		return buyBack(sell_message)
'''

#######################################################################################


def tradeArbitrage(baseCurrency, buyCurrency, buyExchange, sellExchange, rates_if_profitable):
	"Place a maker sell order at the sellExchange (GDAX) and a taker buy order at the buyExchange (Kraken)"

	# Obtain the desired buy and sell prices
	# These are given from the profitability check

	desired_buy = rates_if_profitable[0]
	desired_sell = rates_if_profitable[1]
	desired_baseCurrencyAmount = rates_if_profitable[2]
	desired_buyCurrencyAmount = rates_if_profitable[3]
	could_be_bought = rates_if_profitable[4]
	could_be_bought_during_sell = rates_if_profitable[5]


	# Only continue if the rates match with the current prices.
	# Otherwise the program was not fast enough. Start all over

	[current_buy_price, current_sell_price] = getAllPrices(baseCur, buyCur, buyExchange, sellExchange)

	if ((current_buy_price > desired_buy) | (current_sell_price < desired_sell)):
		# If the buy price has risen or the sell rate has dropped it cannot
		# be guaranteed that the trade is still profitable
		# Prices movements in the other directions should be okay :)
		print('Damnit!!! I wasn\'t fast enough to respond to the price difference :(. I will try again immediately...'))
		main()

	# Cancel all orders for the given currency pair (safety)
	if (sellExchange == 'GDAX'):
		print('Canceling all orders on ' + sellExchange + ' for ' + buyCurrency + '-' + baseCurrency)
		gdax_handler.cancelOrders(buyCurrency + '-' + baseCurrency)
	else:
		sys.exit('Could not recognize sellExchange trying to cancel all orders.')

	######### TODO: Cancel for Kraken/Poloniex too. This feature is not absoulutely necessary though, since only Takers are made on Kraken


	# Place limit sell order at sellExchange (GDAX)
	#############################
	# For use of other exchanges, change function here

	# For testing purposes ############################
	desired_sell = 0.2
	desired_buyCurrencyAmount = 0.01
	###################################################

	'''
	if (sellExchange == 'GDAX'):
		sell_message = gdax_handler.sellLimitTrade(desired_sell, desired_buyCurrencyAmount, buyCurrency + '-' + baseCurrency)
	else:
		sys.exit('Could not recognize sellExchange trying to place buy order on ' + sellExchange)

	print('Sell message: ' + str(sell_message))

	#############################

	# If there is a problem with the trade. sell_message will only contain a "message" sub-tag and thus, the program will
	# abort trying to get the sell_id, just as it should (to be sure).
	sell_id = sell_message['id']

	#############################
	# Wait until order is filled or a maximum of max_timer seconds
	timer = 0
	max_timer = 6
	wait_period = 2

	'''

	#############################
	''' Method 2) see below
	while (timer < max_timer):
		time.sleep(wait_period)
		timer += wait_period
		print('Checking back on sell position...')
		#sell_result = checkBackOnSellOrder(sell_id, sell_message)
		sell_result = 0
		if (sell_result == 1):
			# Take buy order at buyExchange (Kraken)
			break

	if (sell_result == 1):
		print('Take buy order @ Kraken')

	# Timer is over. Start anew.
	print('Timer is over. Position could not be sold immediately. Start anew')
	#gdax_handler.cancelOrders(buyCurrency + '-' + baseCurrency)
	#main()
	'''

	'''
	################################ THE TRADE ################################
	What happens now is the actual trade.
	This has been shown to be quite tricky, as we would ideally like to place
	at least one maker trade to avoid too many fees.
	This, however, comes with the risk of a trade not fully going through.
	There are currently two approaches as possibility:
		1) Place both trades simulatenously and just wait for the maker trade
		(which is the sell order on GDAX) to go through. There is a small likelihood
		that this does not happen immediately, or not fully immediately. This
		likelihood is minimized if the lowest possible sell price (1 unit above
		highest bid) is set as the desired sell price.
		2) Place the maker order first and wait for it to be filled within a short
		time. If the trade goes through quickly, proceed as usual.
		However, if the maker trade is not fully filled quickly, this could become
		an issue. This is where this approach gets tricky, as the taker order has
		not been placed at this point
	###########################################################################
	'''

	# Place sell order on sellExchange
	# Place buy order on buyExchange

	trade_result = performArbitrageTrade(baseCur, buyCur, could_be_bought, desired_buyCurrencyAmount, current_buy_price, current_sell_price, buyExchange, sellExchange)

	if (trade_result != [0, 0]):
		# Well done - orders have gone through
		# Now, wait until both orders have been settled
		buy_id = trade_result[0]
		sell_id = trade_result[1]
		
		'''
		#######################################################################################
		#######################################################################################
		#######################################################################################
		#######################################################################################
		LEFT OFF HERE -> checkBackOnOrders(buy_id, sell_id)
		#######################################################################################
		#######################################################################################
		#######################################################################################
		#######################################################################################
		'''

	else:
		sys.exit('Trade was unsuccessful.')


#######################################################################################


def main():

	#############################
	# Parameters for checking profitability - Change these if wanted

	baseCurrency = 'BTC'
	buyCurrency = 'LTC'
	buyFee = 0.0026 # Taker Fee - Kraken - LTC/BTC
	sellFee = 0.00 # Maker Fee - GDAX - LTC/BTC
	baseCurrencyTransferFee = 0 # Withdraw Fee - GDAX - BTC
	buyCurrencyTransferFee = 0.001 # Withdraw Fee - Kraken - LTC
	buyExchange = 'Kraken' # Alternatively 'Poloniex'
	sellExchange = 'GDAX' # DO NOT CHANGE!!!!

	#############################

	rates_if_profitable = checkProfitability(baseCurrency, buyCurrency, buyFee, sellFee, baseCurrencyTransferFee, buyCurrencyTransferFee, buyExchange, sellExchange)

	print(rates_if_profitable)

	if (rates_if_profitable != [0, 0, 0, 0, 0, 0]):
		print('Trading the arbitrage')
		#tradeArbitrage(baseCurrency, buyCurrency, buyExchange, sellExchange, rates_if_profitable)


	'''
	else:
		# Try again in some time interval

		#############################
		# Check again in ...
		check_interval = 300
		# ...seconds
		#############################

		time.sleep(check_interval)
		main()
	'''

if __name__ == "__main__":
	main()
