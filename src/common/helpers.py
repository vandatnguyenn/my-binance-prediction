import dateparser
import pytz
from datetime import datetime
import csv

def date_to_milliseconds(date_str):
    """Convert UTC date to milliseconds
    If using offset strings add "UTC" to date string e.g. "now UTC", "11 hours ago UTC"
    See dateparse docs for formats http://dateparser.readthedocs.io/en/latest/
    :param date_str: date in readable format, i.e. "January 01, 2018", "11 hours ago UTC", "now UTC"
    :type date_str: str
    """
    epoch = datetime.utcfromtimestamp(0).replace(tzinfo=pytz.utc)
    d = dateparser.parse(date_str)
    if d.tzinfo is None or d.tzinfo.utcoffset(d) is None:
        d = d.replace(tzinfo=pytz.utc)

    return int((d - epoch).total_seconds() * 1000.0)

def writeCsv(_data):
    with open('BTC-USD.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Date','Open','High','Low','Close','Adj Close','Volume'])
        
        saveData = []

        for data in _data:
            candlestick = [
                data.Date,
                data.Open,
                data.High,
                data.Low,
                data.Close,
                data.AdjClose,
                data.Volume
            ]
            saveData.append(candlestick)
        
        writer.writerow(saveData)