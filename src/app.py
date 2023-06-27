from flask import Flask, render_template, request, flash, redirect, jsonify
import csv, datetime
from binance.client import Client
from binance.enums import *
from common.helpers import date_to_milliseconds, writeCsv, milliseconds_to_date


app = Flask(__name__)
app.secret_key = b'somelongrandomstring'

client = Client("","")

@app.route('/')
def index():
    title = 'CoinView'
    return render_template('index.html', title=title)


@app.route('/history')
def history():
    candlesticks = client.get_klines(
        symbol="BTCUSDT",
        interval="5m",
        limit=100000,
        startTime= date_to_milliseconds("24 hours ago UTC+7"),
        endTime= date_to_milliseconds("now UTC+7")
    )

    # print(candlesticks)

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

    writeCsv("BTC-USD.csv", _dataCsv)
    return jsonify(processed_candlesticks)


@app.route('/predictions')
def predictions():
    # candlesticks = client.get_klines(
    #     symbol="BTCUSDT",
    #     interval="5m",
    #     limit=100000,
    #     startTime= date_to_milliseconds("24 hours ago UTC+7"),
    #     endTime= date_to_milliseconds("now UTC+7")
    # )
    
    # processed_candlesticks = []

    # for data in candlesticks:
    #     candlestick = { 
    #         "time": data[0], 
    #         "open": data[1],
    #         "high": data[2], 
    #         "low": data[3], 
    #         "close": data[4]
    #     }

    #     processed_candlesticks.append(candlestick)

    ##

    # return "aaaaa"
    temp = [
        { "value": 30360,    "time": 1687796888048 },
        { "value": 30490,    "time": 1687796888049 },
        { "value": 30570,    "time": 1687796888050 },
        { "value": 30320,    "time": 1687796888051 },
        { "value": 30763,    "time": 1687796888052 },
        { "value": 30643,    "time": 1687796888053 },
        { "value": 30341,    "time": 1687796888054 },
        { "value": 30343,    "time": 1687796888055 },
        { "value": 30356,    "time": 1687796888056 },
        { "value": 30626,    "time": 1687796888057 }
    ]
    return jsonify(temp)