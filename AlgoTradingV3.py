import time
import datetime
from math import ceil
from keys import api_key
from keys import api_secret
from binance.client import Client

from multiprocessing import Pool

file_name = "file.txt"
new_candle = "new_candle"
input_point = False

dump_info = ''
import requests
import numpy as np
import talib

api_key_testnet = ""
secret_key_testnet = ""

client = Client(api_key, api_secret)

trades = client.get_my_trades(symbol='BNBUSDT')

print(trades)
ups = False
with open("new_candle", "w") as text:
    text.write(str(0))
SYMBOL = "BNBUSDT"
TIME_PERIOD = "1h"
LIMIT = "200"

short = False

now_hour = 0
last_hour = 0
now_minute = 0
now_date = ""

now_kandle = 0
last_kandle = 0
last_kandle_diff = 0

Flag_new_Candle = False
Flag_new_hour = False
get_now_candle = 0

cnt = 0

get_percent_round = 0

long_or_short = 0
balance = client.get_account()
free = [b['free'] for b in balance['balances'] if b['asset'] == 'USDT']
locked = [b['locked'] for b in balance['balances'] if b['asset'] == 'USDT']

all_balance = float(free[0]) + float(locked[0])
print(all_balance)

my_balance = all_balance

time.sleep(1)
print("Start-UP")
time.sleep(0.1)
print("     |    ")
time.sleep(0.1)
print("     |    ")
time.sleep(0.1)
print("     |    ")
time.sleep(0.1)
print("     |    ")
time.sleep(0.1)
print("     |    ")
time.sleep(0.1)
print("     |    ")


def get_data():
    try:
        global input_point
        global cnt
        global Flag_new_Candle
        url = "https://api.binance.com/api/v3/klines?symbol={}&interval={}&limit={}".format(SYMBOL, TIME_PERIOD, LIMIT)
        res = requests.get(url)
        global last_kandle
        global now_kandle
        global last_kandle_diff
        cnt += 1
        # print(url,res) вывод юрл
        return_data = []
        print("\033[33m")
        for each in res.json():
            return_data.append(float(each[4]))
        now_kandle = (np.array(return_data))[-1]
        last_kandle = (np.array(return_data))[-2]
        if last_kandle != last_kandle_diff:
            if cnt > 2:
                Flag_new_Candle = True
                print(Flag_new_Candle, Flag_new_hour)
                input_point = True
                print("\033[31mNEW_Candle")
                with open("new_candle", "w") as text:
                    text.write(str(1))



        else:
            Flag_new_Candle = False

        last_kandle_diff = last_kandle
        print(now_kandle, "\033[33mnow kandle")
        print(last_kandle, "\033[33mlast kandle")
        return np.array(return_data)

    except:
        print("\033[31mOffline")
        time.sleep(0.5)
        print("\033[31mOffline")
        time.sleep(0.5)
        print("\033[31mOffline")
        time.sleep(0.5)


print(get_data())


def all_calculations():
    with Pool(processes=1) as pool:
        get_data()
        global send
        global long_or_short
        global now_date
        global now_minute
        global cnt
        global get_percent_round
        global Flag_new_hour
        now = datetime.datetime.now()
        now_date = now.strftime("%d-%m-%Y %H:%M")
        global now_kandle
        global now_hour
        global last_hour
        # print(Flag_new_Candle, Flag_new_hour)

        now_hour = now.hour
        now_minute = now.minute
        if last_hour != now_hour:
            if cnt > 2:
                Flag_new_hour = True

                print("NEW_HOUR")

        global last_kandle
        closing_data = get_data()
        # print(last_hour, now_hour)
        ema_50 = talib.EMA(closing_data, 50)
        ema200 = talib.EMA(closing_data, 200)
        sma50 = talib.MA(closing_data, 50)
        sma100 = talib.MA(closing_data, 100)
        sma100 = sma100[-1]
        sma100 = round(sma100, 2)
        ema_50 = ema_50[-1]
        ema_50_raw = ema_50
        ema_50 = round(ema_50_raw, 2)
        # print(ema_50_raw)
        print("\033[38m" + str(ema_50) + " |  " + "\033[38m" + str(last_kandle))
        # print(now.hour, "hour")
        last_hour = now.hour
        get_percent = ((ema_50 / last_kandle) - 1) * 100
        get_percent_now = ((ema_50 / now_kandle) - 1) * 100
        get_percent_round = round(get_percent, 3)
        get_percent_round_now = round(get_percent_now, 3)
        long_or_short = ema_50 - last_kandle
        # print("diff_between_ema_and_realtime_char", round(ema_50 - now_kandle, 2), "diff_between_ema_and_last_char in %", (round(get_percent_now, 3)))
        # print(Flag_new_Candle, Flag_new_hour)
        return "Online", ema_50, sma100, now_kandle, last_kandle


print(all_calculations())


def entry_long():
    time.sleep(15)
    global in_position
    status, ema50, sma100, now_kandle, last_kandle = all_calculations()
    if in_position == False and last_kandle > ema50 and last_kandle > sma100:
        open_long(in_position)


def open_long(in_position):
    try:
        with open("in_position.txt", "r") as f:
            d = f.readline()
            d = int(d)
            if d == 1:
                in_position = True
            if d == 0:
                in_position = False
        global my_balance
        global buy_price
        time.sleep(30)
        status, ema50, sma100, now_kandle, last_kandle = all_calculations()
        if in_position == False:
            if last_kandle > ema50 and last_kandle > sma100:
                order = client.create_order(symbol=SYMBOL, side="buy", quantity=1, type="MARKET")
                now = datetime.datetime.now()
                with open(file_name, "a") as text_file:
                    text_file.write("BUY |" + str(now) + " | " + str(now_kandle))
                buy_price = now_kandle
                with open("in_position.txt", "w") as text_file:
                    text_file.write(str(1))

                in_position = True
        if in_position == True:

            your_profit_pnl = now_kandle - buy_price
            your_profit = ((now_kandle / buy_price) - 1) * 100
            if your_profit >= 0:

                print("\033[32m " + str(round(your_profit_pnl, 2)) + " $ " + " " + str(round(your_profit, 2)) + " % ")
            else:
                print("\033[31m " + str(round(your_profit_pnl, 2)) + " $ " + " " + str(round(your_profit, 2)) + " % ")






                open_long(in_position)

            if last_kandle < ema50:
                print("StopLoss!")
                with open("in_position.txt", "w") as text_file:
                    text_file.write(str(0))
                time.sleep(2)
                balance = client.get_account()
                free = [b['free'] for b in balance['balances'] if b['asset'] == 'USDT']
                locked = [b['locked'] for b in balance['balances'] if b['asset'] == 'USDT']

                all_balance = float(free[0]) + float(locked[0])
                print(all_balance)
                my_balance = 0
                my_balance = all_balance

                time.sleep(5)
                order = client.create_order(symbol=SYMBOL, side="sell", quantity=1, type="MARKET")
                time.sleep(5)
                balance = client.get_account()
                free = [b['free'] for b in balance['balances'] if b['asset'] == 'USDT']
                locked = [b['locked'] for b in balance['balances'] if b['asset'] == 'USDT']

                all_balance = float(free[0]) + float(locked[0])
                print(all_balance)

                print("continue")
                open_long(in_position)

                now = datetime.datetime.now()
                text_file.write("SELL |" + str(now) + " | " + str(now_kandle) + " | StopLoss!" + str(
                    all_balance - my_balance))
                print("checkClosedPosition ---> OK!")
                print("Lose ---> " + str(all_balance - my_balance))


                with open("in_position.txt", "w") as text_file:
                    text_file.write(str(0))
                time.sleep(7200)
                open_long(in_position=False)
        else:

            with open("in_position.txt", "r") as text_file:
                text_file.write(str(0))
            open_long(in_position=False)

    except:
        print("\033[31mOffline or < ema50")
        time.sleep(2)
        with open("in_position.txt", "r") as f:
            d = f.readline()
            d = int(d)
            if d == 1:
                open_long(in_position=True)
            if d == 0:
                open_long(in_position=False)



print(all_calculations())

print("1 loop")
in_position = False
while True:
    open_long(in_position)
