from flask import Flask, render_template, request, flash, redirect, jsonify
# import csv, datetime
from datetime import datetime
from binance.client import Client
from binance.enums import *
import os
from common.helpers import date_to_milliseconds, writeCsv, milliseconds_to_date
from predictions.lstm_pred import lstm_prediction_process
from predictions.rnn_pred import rnn_prediction_process


app = Flask(__name__)
app.secret_key = b'somelongrandomstring'

client = Client("","")

@app.route('/')
def index():
    title = 'Coin View'
    return render_template('index.html', title=title)


@app.route('/history')
def history():
    candlesticks = client.get_klines(
        symbol="BTCUSDT",
        interval="5m",
        limit=1000,
        startTime= date_to_milliseconds("5000 mins ago UTC"),
        endTime= date_to_milliseconds("now UTC")
    )

    processed_candlesticks = []
    _dataCsv = [['Date','Open','High','Low','Close','Volume']]

    for data in candlesticks:
        candlestick = { 
            "time": data[0], 
            "open": data[1],
            "high": data[2], 
            "low": data[3], 
            "close": data[4]
        }

        processed_candlesticks.append(candlestick)
        _dataCsv.append([milliseconds_to_date(data[0]), data[1], data[2], data[3], data[4], data[5]])

    # thêm dữ liệu để dự đoán
    # for i in range(1, 110):
    #     _dataCsv.append([milliseconds_to_date(candlesticks[len(candlesticks) - 1][0] + i*300000), 0, 0, 0, 0, 0])

    # Lưu ngày hiện tại để reset model
    if not os.path.exists("lastDate.txt"):
        _now = milliseconds_to_date(candlesticks[len(candlesticks) - 1][0]).strftime("%Y-%m-%d")
        w_file = open("lastDate.txt", "w")
        w_file.write(_now)
        w_file.write(" 23:59:59")
        w_file.close()

    writeCsv("BTC-USD.csv", _dataCsv)
    return jsonify(processed_candlesticks)


@app.route('/predictions')
def predictions():

    # Kiểm tra reset model
    f = open("lastDate.txt", "r")
    _lastDate = datetime.strptime(f.read(), "%Y-%m-%d %H:%M:%S")
    f.close()

    _isReset = datetime.now() > _lastDate

    _data = rnn_prediction_process(_isReset)
    # _data = lstm_prediction_process(_isReset) 
    return jsonify(_data)