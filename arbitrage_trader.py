#!/usr/bin/python
import gdax
import json
import base64, hashlib, hmac, time, math, sys
import gdax_handler
import kraken_handler
import numpy as np
from random import randint

######################
# Due to the difficulty of retreiving historic highest bid / lowest ask historic data
# backtesting must be conducted in real time
# The difference is that one starts with an imaginary amount of currency and
# imaginary exchanges
backtesting = True
######################


#############################
# Parameters - Change these if wanted

baseCurrency = 'BTC'
buyCurrency = 'LTC'
buyFee = 0.0026 # Taker Fee - Kraken - LTC/BTC
sellFee = 0.000 # Maker Fee - GDAX - LTC/BTC
baseCurrencyTransferFee = 0.000 # Withdraw Fee - GDAX - BTC
buyCurrencyTransferFee = 0.001 # Withdraw Fee - Kraken - LTC
buyExchange = 'Kraken' # Alternatively 'Poloniex'
sellExchange = 'GDAX' # DO NOT CHANGE!!!!

#############################

'''
The saved account files 'GDAX_Backtesting_Accounts.npy', 'Kraken_Backtesting_Accounts.npy', 'Poloniex_Backtesting_Accounts.npy'
accumulate data as {'BTC': 0.0, 'LTC': 0.0, 'ETH': 0.0, 'BCH': 0.0, 'EUR': 0.0}
'''
######################

# GDAX
GDAX_BTC_whitelistedWithdrawAddress = ''
GDAX_LTC_whitelistedWithdrawAddress = 'LauE97bMZgRXabd9oG22bDVsVHoSVWNhjj'
GDAX_ETH_whitelistedWithdrawAddress = ''
GDAX_BCH_whitelistedWithdrawAddress = ''

# Kraken
Kraken_BTC_whitelistedWithdrawAddress = '3KJS1E4jRmhgz9Z9mPnb39HSunG12Tfhmy'
Kraken_LTC_whitelistedWithdrawAddress = ''
Kraken_ETH_whitelistedWithdrawAddress = ''
Kraken_BCH_whitelistedWithdrawAddress = ''

# Poloniex
Poloniex_BTC_whitelistedWithdrawAddress = ''
Poloniex_LTC_whitelistedWithdrawAddress = ''
Poloniex_ETH_whitelistedWithdrawAddress = ''
Poloniex_BCH_whitelistedWithdrawAddress = ''

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
		sys.exit('Could not recognize buyExchange in getAllPrices')

	# Maker sell will execute on highest bid + smallest quote increment
	# This is the worst price at which a maker order can be placed
	# Thus, a maker fill is the most likely like this

	sell_rate = 0
	if (sellExchange == 'GDAX'):
		gdax_prices = gdax_handler.priceCheck(buyCur + '-' + baseCur)
		# Highest bid
		sell_rate = gdax_prices[0]
		# Increase by smallest quote increment
		quote_increment = gdax_handler.getQuoteIncrement(buyCur + '-' + baseCur)
		sell_rate = sell_rate + quote_increment
	else:
		sys.exit('Could not recognize sellExchange in getAllPrices')

	# For testing purposes
	# buy_rate = sell_rate * 0.995

	return [buy_rate, sell_rate]


#######################################################################################


def performArbitrageTrade(baseCur, buyCur, buy_amount, sell_amount, buyPrice, sellPrice, buyExchange, sellExchange):
	"The actual trading procedure"

	print('Let \'s start the actual trading procedure')
	# Buy trade
	buy_id = 0
	if (buyExchange == 'Kraken'):
		buy_message = kraken_handler.buyTakerTrade(buyPrice, buy_amount, buyCur + '-' + baseCur)
		print('Buy message: ' + str(buy_message))
		buy_id = buy_message['descr']
		print(buy_id)
	elif (buyExchange == 'Poloniex'):
		buy_message = poloniex_handler.buyTrade(buyPrice, buy_amount, buyCur + '-' + baseCur)
		print('Buy message: ' + str(buy_message))
		buy_id = buy_message
	else:
		sys.exit('Could not recognize buyExchange during trade')

	# Sell trade
	sell_id = 0
	if (sellExchange == 'GDAX'):
		sell_amount = round(sell_amount - float(5e-7), 6)
		sell_message = gdax_handler.sellLimitTrade(sellPrice, sell_amount, buyCur + '-' + baseCur)
		print('Sell message: ' + str(sell_message))
		sell_id = sell_message['id']
	else:
		sys.exit('Could not recognize sellExchange during trade')


	if([buy_id, sell_id] == [0, 0]):
		sys.exit('Cannot perform arbitrage trade')
	else:
		print('Trades generated. Buy ID: ' + str(buy_id) + ', Sell ID: ' + str(sell_id))
		return [buy_id, sell_id] # Success


#######################################################################################


def checkBackOnOrders(buy_id, sell_id, buyExchange, sellExchange):
	"Checks whether the generated trades have been settled"

	print('Checking back on the generated orders with buy_id ' + str(buy_id) + ' and sell_id ' + str(sell_id))


	############ For simplicity it will be assumed that the buy order, which is
	############ a taker order, fills immediately
	'''
	buy_status = 0
	if (buyExchange == 'Kraken'):
		buy_status = kraken_handler.getOrderInfo(buy_id)
	elif (buyExchange == 'Poloniex'):
		buy_status = poloniex_handler.getOrderInfo(buy_id)
	else:
		sys.exit('Could not recognize buyExchange while checking back on generated orders')

	'''
	buy_status = True

	sell_status = gdax_handler.getOrderInfo(sell_id)['settled']

	print('Buy settled (presumably since taker order) on ' + buyExchange + ': ' + str(buy_status) + ', Sell settled on ' + sellExchange + ': ' + str(sell_status))

	return [buy_status, sell_status]


#######################################################################################

def withdraw(from_exchange, to_exchange, currency, amount):
	"Withdraws currency to the specified exchange. Returns 0 on success."

	if (from_exchange == 'GDAX'):
		if (to_exchange == 'Kraken'):
			withdrawAdr = ''
			if (currency == 'BTC'):
				withdrawAdr = Kraken_BTC_whitelistedWithdrawAddress
			elif(currency == 'LTC'):
				withdrawAdr = Kraken_LTC_whitelistedWithdrawAddress
			elif(currency == 'ETH'):
				withdrawAdr = Kraken_ETH_whitelistedWithdrawAddress
			elif(currency == 'BCH'):
				withdrawAdr = Kraken_BCH_whitelistedWithdrawAddress
			else:
				sys.exit('There was a withdrawal error. Currency was not recognized: ' + currency)

			if (withdrawAdr == ''):
				sys.exit('There was a withdrawal error. Withdrawal address was not set.')
			else:
				print('Withdrawing from ' + from_exchange + ': ' + str(amount) + currency + ' to ' + to_exchange + ' at address ' + withdrawAdr)
				gdax_handler.withdrawToAddress(withdrawAdr, to_exchange, currency, amount)

		elif (to_exchange == 'Poloniex'):
			withdrawAdr = ''
			if (currency == 'BTC'):
				withdrawAdr = Poloniex_BTC_whitelistedWithdrawAddress
			elif(currency == 'LTC'):
				withdrawAdr = Poloniex_LTC_whitelistedWithdrawAddress
			elif(currency == 'ETH'):
				withdrawAdr = Poloniex_ETH_whitelistedWithdrawAddress
			elif(currency == 'BCH'):
				withdrawAdr = Poloniex_BCH_whitelistedWithdrawAddress
			else:
				sys.exit('There was a withdrawal error. Currency was not recognized: ' + currency)

			if (withdrawAdr == ''):
				sys.exit('There was a withdrawal error. Withdrawal address was not set.')
			else:
				print('Withdrawing from ' + from_exchange + ': ' + str(amount) + currency + ' to ' + to_exchange + ' at address ' + withdrawAdr)
				gdax_handler.withdrawToAddress(withdrawAdr, to_exchange, currency, amount)
		else:
			sys.exit('There was a withdrawal error. The from_exchange was ' + from_exchange + ', the to_exchange is not valid: ' + to_exchange)

	elif (from_exchange == 'Kraken'):
		if (to_exchange == 'GDAX'):
			withdrawAdr = ''
			if (currency == 'BTC'):
				withdrawAdr = GDAX_BTC_whitelistedWithdrawAddress
			elif(currency == 'LTC'):
				withdrawAdr = GDAX_LTC_whitelistedWithdrawAddress
			elif(currency == 'ETH'):
				withdrawAdr = GDAX_ETH_whitelistedWithdrawAddress
			elif(currency == 'BCH'):
				withdrawAdr = GDAX_BCH_whitelistedWithdrawAddress
			else:
				sys.exit('There was a withdrawal error. Currency was not recognized: ' + currency)

			if (withdrawAdr == ''):
				sys.exit('There was a withdrawal error. Withdrawal address was not set.')
			else:
				print('Withdrawing from ' + from_exchange + ': ' + str(amount) + currency + ' to ' + to_exchange)
				# Kraken Handler takes name of address (in this case 'GDAX' as argument)
				kraken_handler.withdrawToAddress('', to_exchange, currency, amount)
		else:
			sys.exit('There was a withdrawal error. The from_exchange was ' + from_exchange + ', the to_exchange is not valid: ' + to_exchange)

	elif (from_exchange == 'Poloniex'):
		if (to_exchange == 'GDAX'):
			withdrawAdr = ''
			if (currency == 'BTC'):
				withdrawAdr = GDAX_BTC_whitelistedWithdrawAddress
			elif(currency == 'LTC'):
				withdrawAdr = GDAX_LTC_whitelistedWithdrawAddress
			elif(currency == 'ETH'):
				withdrawAdr = GDAX_ETH_whitelistedWithdrawAddress
			elif(currency == 'BCH'):
				withdrawAdr = GDAX_BCH_whitelistedWithdrawAddress
			else:
				sys.exit('There was a withdrawal error. Currency was not recognized: ' + currency)

			if (withdrawAdr == ''):
				sys.exit('There was a withdrawal error. Withdrawal address was not set.')
			else:
				print('Withdrawing from ' + from_exchange + ': ' + str(amount) + currency + ' to ' + to_exchange + ' at address ' + withdrawAdr)
				poloniex_handler.withdrawToAddress(withdrawAdr, to_exchange, currency, amount)
		else:
			sys.exit('There was a withdrawal error. The from_exchange was ' + from_exchange + ', the to_exchange is not valid: ' + to_exchange)
	else:
		sys.exit('There was a withdrawal error. The from_exchange was not recognized')

	return 0


def checkProfitability(baseCur, buyCur, buyFee, sellFee, baseCurTransferFee, buyCurTransferFee, buyExchange, sellExchange):
	"Determine whether the current arbitrage gap is profitable under all given fees etc."


	# Obtain currency balances
	baseCurrencyAmount = 0
	if (buyExchange == 'Kraken'):
		baseCurrencyAmount = kraken_handler.checkFunds(baseCur)
	elif (buyExchange == 'Poloniex'):
		baseCurrencyAmount = poloniex_handler.checkFunds(baseCur)
	else:
		sys.exit('Could not recognize buyExchange')

	buyCurrencyAmount = gdax_handler.checkFunds(buyCur)

	# For testing purposes
	#baseCurrencyAmount = 5
	#buyCurrencyAmount = 300

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
		return [0, 0, 0, 0, 0, 0]
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
		couldBeSold = buyCurrencyAmount * sell_rate * (1 - sellFee) # Amount of base currency to be bought in sell operation on sellExchange

		# Round down, 6 digits
		#couldBeBought = round(couldBeBought - float(5e-7), 6)
		#couldBeSold = round(couldBeSold - float(5e-7), 6)

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

		print('This is a profit of ' + str(((buyCurProfit - 1) * 100)) + '% \in ' + buyCur)
		print('This is a profit of ' + str(((baseCurProfit - 1) * 100)) + '% \in ' + baseCur)

		# We want both profits to be definitely positive and at least one of them should be more than 0.15%
		# This is a little redundant since from the above calculations it will follow that profits are symmetric on both exchanges
		if (((buyCurProfit >= 1) & (baseCurProfit >= 1)) & ((buyCurProfit > 1.0015) | (baseCurProfit > 1.0015))):
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

	[current_buy_price, current_sell_price] = getAllPrices(baseCurrency, buyCurrency, buyExchange, sellExchange)

	# Round down, 6 digits
	#current_buy_price = round(current_buy_price - float(5e-7), 6)
	#current_sell_price = round(current_sell_price - float(5e-7), 6)

	if ((current_buy_price > desired_buy) | (current_sell_price < desired_sell)):
		# If the buy price has risen or the sell rate has dropped it cannot
		# be guaranteed that the trade is still profitable
		# Prices movements in the other directions should be okay :)
		print('Damnit!!! I wasn\'t fast enough to respond to the price difference :(. I will try again immediately...')
		main()

	print('Good. The current rates have, if at all, changed to the good: Buy Rate: ' + str(current_buy_price) + ', Sell Rate: ' + str(current_sell_price))
	# Cancel all orders for the given currency pair (safety)
	if (sellExchange == 'GDAX'):
		print('Canceling all orders on ' + sellExchange + ' for ' + buyCurrency + '-' + baseCurrency)
		gdax_handler.cancelOrders(buyCurrency + '-' + baseCurrency)
	else:
		sys.exit('Could not recognize sellExchange trying to cancel all orders in tradeArbitrage().')

	######### TODO: Cancel for Kraken/Poloniex too. This feature is not absoulutely necessary though, since only Takers are made on Kraken

	# For testing purposes ############################
	# desired_sell = 0.2
	# desired_buyCurrencyAmount = 0.01
	###################################################


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

	trade_result = performArbitrageTrade(baseCurrency, buyCurrency, could_be_bought, desired_buyCurrencyAmount, current_buy_price, current_sell_price, buyExchange, sellExchange)


	if (trade_result == [0, 0]):
		sys.exit('Trade was unsuccessful.')
	else:
		# Well done - orders have gone through
		# Now, wait until both orders have been settled
		print('Well done. Orders have gone through.')
		buy_id = trade_result[0]
		sell_id = trade_result[1]

		##########################
		timer_step = 10
		##########################

		order_status = [False, False]
		while ((order_status[0] == False) | (order_status[1] == False)):
			# Wait until both orders have been settled. This may take some time
			print('Waiting for orders to fill...')
			#print('Buy order filled: ' + order_status[0], ', Sell order filled: ' + order_status[1])
			time.sleep(timer_step)
			order_status = checkBackOnOrders(buy_id, sell_id, buyExchange, sellExchange)

		# Orders have been settled. Transfer back to address

		# Transfer baseCurrency from sellExchange to buyExchange
		print('Transfer ' + str(could_be_bought_during_sell) + baseCurrency + ' from ' + sellExchange + ' to ' + buyExchange)
		sell_exchange_withdrawal_result = 1
		if ((buyExchange == 'Kraken') | (buyExchange == 'Poloniex')):
			sell_exchange_withdrawal_result = withdraw(sellExchange, buyExchange, baseCurrency, could_be_bought_during_sell)
		else:
			sys.exit('Withdrawal error. buyExchange ' + buyExchange + ' not recognized')

		print('Transfer ' + str(could_be_bought) + buyCurrency + ' from ' + buyExchange + ' to ' + sellExchange)
		buy_exchange_withdrawal_result = 1
		if (sellExchange == 'GDAX'):
			buy_exchange_withdrawal_result = withdraw(buyExchange, sellExchange, buyCurrency, could_be_bought)
		else:
			sys.exit('Withdrawal error. sellExchange not recognized')

		if((buy_exchange_withdrawal_result == 0) & (sell_exchange_withdrawal_result == 0)):
			print('Success! Withdrawals have been started!')
		else:
			sys.exit('Error trying to withdraw currencies')


		##################
		# Pause for 10 Minutes and wait for currencies to be transferred
		##################
		pause_for_secs = 600
		print('Sleeping for ' + str(pause_for_secs) + 's...')
		time.sleep(pause_for_secs)
		main()


#######################################################################################


def main():

	rates_if_profitable = checkProfitability(baseCurrency, buyCurrency, buyFee, sellFee, baseCurrencyTransferFee, buyCurrencyTransferFee, buyExchange, sellExchange)

	print('Rates if profitable: ' + str(rates_if_profitable))

	if (rates_if_profitable == [0, 0, 0, 0, 0, 0]):
		# Try again in some time interval

		#############################
		# Check again in ...
		check_interval = 10
		# ...seconds
		#############################
		print('Sleeping for ' + str(check_interval) + 's...')
		time.sleep(check_interval)
		main()
	else:
		print('Trading the arbitrage')
		tradeArbitrage(baseCurrency, buyCurrency, buyExchange, sellExchange, rates_if_profitable)


if __name__ == "__main__":
	main()
