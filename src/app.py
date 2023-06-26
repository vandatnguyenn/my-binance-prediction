from flask import Flask, render_template, request, flash, redirect, jsonify
import csv, datetime
from binance.client import Client
from binance.enums import *
from helpers import date_to_milliseconds

app = Flask(__name__)
app.secret_key = b'somelongrandomstring'

client = Client("","")

print("client")
print(client)

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
        startTime= date_to_milliseconds("48 hours ago UTC"),
        endTime= date_to_milliseconds("now UTC")
    )

    processed_candlesticks = []

    for data in candlesticks:
        candlestick = { 
            "time": data[0] / 1000, 
            "open": data[1],
            "high": data[2], 
            "low": data[3], 
            "close": data[4]
        }

        processed_candlesticks.append(candlestick)

    return jsonify(processed_candlesticks)