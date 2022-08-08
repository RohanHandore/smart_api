from smartapi import SmartConnect
import warnings
import pdb
import requests
import pandas as pd
import datetime
import time
# import mibian


def angelbrok_login():
    try:
        global feedToken, client_code, obj, password
        
        obj = SmartConnect(api_key="9DV1aUFA")
        client_code = "IIRA44259"
        password = "Rohan8830@#"


        data = obj.generateSession(client_code,password)
        refreshToken = data['data']['refreshToken']

        # print (dict(data))
        feedToken=obj.getfeedToken()

        # userProfile= obj.getProfile(refreshToken)
        # print (dict(userProfile))
        print ("\nLogin succesfull!")
    except Exception as e:
        print("Error in login", e)

angelbrok_login()


def get_instruments():
	global instrument_df
	url = 'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json'
	request = requests.get(url=url, verify=False)
	data = request.json()
	instrument_df = pd.DataFrame(data)
	instrument_df.to_csv("instruments.csv")
	instrument_df.set_index("symbol", inplace=True)
	return instrument_df

instrument_df = get_instruments()
# print(instrument_df)

def get_token_and_exchange(name):
	symboltoken = instrument_df.loc[name]['token']
	exchange = instrument_df.loc[name]['exch_seg']
	return symboltoken, exchange

def get_ohlc(name, exchange):
	symboltoken = instrument_df.loc[name]['token']
	ohlc_data = obj.ltpData(exchange, name, symboltoken)
	ohlc_data = ohlc_data['data']
	return ohlc_data

def get_ltp(name, exchange):
	symboltoken = instrument_df.loc[name]['token']
	ltp_data = obj.ltpData(exchange, name, symboltoken)
	ltp = ltp_data['data']['ltp']
	return ltp

def get_historical_data(name, interval, timeperiod):

	token, exchange = get_token_and_exchange(name)

	
	try:
		intervals_dict = {'1min': 'ONE_MINUTE', '3min': 'THREE_MINUTE', '5min': 'FIVE_MINUTE', '10min': 'TEN_MINUTE', '15min': 'FIFTEEN_MINUTE', '30min': 'THIRTY_MINUTE', 'hour': 'ONE_HOUR', 'day': 'ONE_DAY'}
		todate = str(datetime.datetime.now())[:16]
		from_date = str(datetime.datetime.now().date() - datetime.timedelta(days=timeperiod))+" "+"09:15"
		symboltoken = instrument_df.loc[name]['token']
		historicParam = {"exchange": exchange, "symboltoken": symboltoken, "interval": intervals_dict[interval], "fromdate": from_date,  "todate": todate}
		response = obj.getCandleData(historicParam)
		dict1 = {}
		historic_df = pd.DataFrame()
		for data in response['data']:
			dict1['date'] = data[0]
			dict1['open'] = data[1]
			dict1['high'] = data[2]
			dict1['low'] = data[3]
			dict1['close'] = data[4]
			dict1['volume'] = data[5]
			historic_df = historic_df.append(dict1, ignore_index=True)
		return historic_df
	except Exception as e:
		print(e)

print("ready")
# def place_order(orderparams):

# 	orderId = obj.placeOrder(orderparams)
# 	print("		order is placed with orderid= ", orderId)
# 	return orderId
def place_order(token,symbol,qty,buy_sell,ordertype,price,variety= 'NORMAL',exch_seg='NSE',triggerprice=0):
    try:
        orderparams = {
            "variety": variety,
            "tradingsymbol": symbol,
            "symboltoken": token,
            "transactiontype": buy_sell,
            "exchange": exch_seg,
            "ordertype": ordertype,
            "producttype": "INTRADAY",
            "duration": "DAY",
            "price": price,
            "squareoff": "0",
            "stoploss": "0",
            "quantity": qty,
            "triggerprice":triggerprice
            }
        orderId=obj.placeOrder(orderparams)
        print("The order id is: {}".format(orderId))
        return orderId
    except Exception as e:
        print("Order placement failed:")


def cancelOrder(order_id,variety):
	satus=obj.cancelOrder(order_id,variety)
	return satus

