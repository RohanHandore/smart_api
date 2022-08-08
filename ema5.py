import anglebrokingcode as ab
import datetime
import pdb
import pandas as pd
import time
import pandas_ta as ta

# this is whatchlist on which backtested results are great 

watchlist = ['ADANIPORTS-EQ', 'APOLLOTYRE-EQ', 'ASHOKLEY-EQ', 'AXISBANK-EQ', 'BAJFINANCE-EQ', 'BAJAJFINSV-EQ', 'BANDHANBNK-EQ', 'BANKBARODA-EQ', 'BHEL-EQ', 'BPCL-EQ', 'CANFINHOME-EQ', 'CANBK-EQ', 'CHOLAFIN-EQ', 'COFORGE-EQ', 'DLF-EQ', 'ESCORTS-EQ', 'FEDERALBNK-EQ', 'GODREJPROP-EQ', 'GRASIM-EQ', 'HINDALCO-EQ', 'HDFC-EQ', 'ICICIBANK-EQ', 'ICICIPRULI-EQ', 'IDFCFIRSTB-EQ', 'IBULHSGFIN-EQ', 'INDUSINDBK-EQ', 'JSWSTEEL-EQ', 'JINDALSTEL-EQ', 'L&TFH-EQ', 'LICHSGFIN-EQ', 'M&MFIN-EQ', 'MANAPPURAM-EQ', 'MARUTI-EQ', 'MFSL-EQ', 'MUTHOOTFIN-EQ', 'NMDC-EQ', 'PEL-EQ', 'PFC-EQ', 'RBLBANK-EQ', 'RADICO-EQ', 'SRTRANSFIN-EQ', 'SBIN-EQ', 'SAIL-EQ', 'TATAMOTORS-EQ', 'TATASTEEL-EQ', 'UJJIVAN-EQ', 'VEDL-EQ', 'ACC-EQ', 'ASIANPAINT-EQ', 'BAJAJ-AUTO-EQ', 'BOSCHLTD-EQ', 'BRITANNIA-EQ', 'CIPLA-EQ', 'COALINDIA-EQ', 'COLPAL-EQ', 'DABUR-EQ', 'DRREDDY-EQ', 'HCLTECH-EQ', 'HDFCBANK-EQ', 'HEROMOTOCO-EQ', 'HINDUNILVR-EQ', 'HDFC-EQ', 'ITC-EQ', 'IOC-EQ', 'INFY-EQ', 'KOTAKBANK-EQ', 'LT-EQ', 'MARICO-EQ', 'NTPC-EQ', 'NESTLEIND-EQ', 'PIDILITIND-EQ', 'POWERGRID-EQ', 'RELIANCE-EQ', 'TCS-EQ', 'TECHM-EQ', 'ULTRACEMCO-EQ', 'WIPRO-EQ']
exchange ="NSE"
traded = {}
positions=[]
qty=1
while True :
	try:
		# pdb.set_trace()
	
		for name in watchlist :


			value =datetime.datetime.now()
			current_time = value.time()

			after_3 = datetime.time(15,13) < current_time 

			before_10 = datetime.time(9,15) < current_time < datetime.time(10,00) 

			if before_10:

				print(name)
				
				ltp= ab.get_ltp(name, exchange)
				df = ab.get_historical_data(name= name, interval="5min", timeperiod=3)
				df.set_index("date", inplace=True)
				df["ema"]= ta.ema(df['close'], length=5, offset=None, append=True)
				
				candle = df.iloc[-1]
				candle2 = df.iloc[-2]
				candle3 = df.iloc[-3]			
				
				close_and_EMA_Movement = ((candle2['close']-candle2["ema5"]) / candle2['close'])*100
				triggered_candle_formed = close_and_EMA_Movement > 0.5
				signal_candle_formed = candle2['low'] > candle2["ema5"] 
				if triggered_candle_formed and signal_candle_formed and name not in traded.keys():
					print("\n")
					print("*******************************************************stock scanned",name)	
					print("\n")
					low_broken=candle2['low'] > ltp
					if low_broken:
						now = datetime.datetime.now()
						time = now.strftime("%H:%M:%S")
						print(time)
						print("**********************************Taking sell trade for  = " ,name)
						print("\n\n",traded)
						token, exchange = ab.get_token_and_exchange(name)
						
						if candle3["high"]>candle2["high"] and  candle3["high"]>candle["high"]:
							sl=float(candle3["high"])

						elif candle["high"]>candle2["high"] and  candle["high"]>candle3["high"]:
							sl=float(candle["high"])

						else:
							sl=float(candle2["high"])

						
						sl_in_pts=round(sl-float(ltp))
						target_in_pts=sl_in_pts*2
						target=ltp-target_in_pts
						res1 = ab.place_order(token,name,qty,'SELL','MARKET',0) #sell order
						print("sl=",sl)
						print("ltp=",ltp)
						print("target=",target)
						print(res1)
						positions.append(name)
						print("current positions are =",positions)
						traded[name] = {}
						traded[name]['stoploss_price'] = sl
						traded[name]['target_price'] = target
						traded[name]['ltp'] = ltp
						traded[name]['entry_time'] = time
						traded[name]['sl_in_pts'] = sl_in_pts
						traded[name]['target_in_pts'] = target_in_pts
						traded[name]['status'] = None
						new  = pd.DataFrame.from_dict(traded)
						new = new.transpose()
						new.to_csv('C:\\rohan\\ema 5\\live trades\\'+str(datetime.datetime.now().date()) + ' trades_before10' + '.csv')
						
						
						
						

			if name in positions:
				print("checking positions in ", name)
				stoploss_price = traded[name]['stoploss_price']
				target_price = traded[ name]['target_price']
				ltp= ab.get_ltp(name, exchange)
				
				if ltp < target_price:
					# pdb.set_trace()
					print("target hit in ", name)
					token, exchange = ab.get_token_and_exchange(traded[name])
					res1 = ab.place_order(token,name,qty,'BUY','MARKET',0) #buy order
					positions.remove(name)
					print("current positions are ", positions)
					# traded[name]['status'] ="target"


				if ltp > stoploss_price:
					# pdb.set_trace()
					print("sl hit in ", name)
					token, exchange = ab.get_token_and_exchange(name)
					res1 = ab.place_order(token,name,qty,'BUY','MARKET',0) #buy order
					positions.remove(name)
					print("current positions are ", positions)
					# traded[name]['status'] ="sl"


			if after_3:
				for stocks in positions:
					token, exchange = ab.get_token_and_exchange(stocks)
					res1 = ab.place_order(token,stocks,qty,'BUY','MARKET',0) #buy order
					traded[name]['status'] ="MARKET over"
					positions.remove(stocks)
					print("current positions are ",positions)
				print("merkets are over")
				new  = pd.DataFrame.from_dict(traded)
				new = new.transpose()
				new.to_csv(str(datetime.datetime.now().date()) + ' trades' + '.csv')
				print(new)
				time.sleep(60)
	except Exception as e:
		print(e)
		continue
	


					
