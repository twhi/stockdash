import requests
import json
import time
import os
from datetime import date, datetime, timedelta


class Finnhub:

    def __init__(self, ticker):
        self.ticker = ticker
        self.token = os.environ['FINNHUB_API_KEY']


    @property
    def last_year(self):

        today = datetime.today() 
        n_days_ago = today - timedelta(days=365)

        today_unix = int(time.mktime(today.timetuple()))
        n_days_ago_unix = int(time.mktime(n_days_ago.timetuple()))

        url = f'https://finnhub.io/api/v1/stock/candle?symbol={self.ticker}&resolution=D&from={n_days_ago_unix}&to={today_unix}&token={self.token}'

        try:
            data = json.loads(requests.get(url).text)
        except json.JSONDecodeError:
            print(f'JSON ERROR SKIPPING {t}')

        if data['s'] == 'no_data':
            return None

        return data['c']

    @property
    def current_value(self):

        url = f'https://finnhub.io/api/v1/quote?symbol={self.ticker}&token={self.token}'

        try:
            return json.loads(requests.get(url).text)['c']
        except json.JSONDecodeError:
            print(f'JSON ERROR SKIPPING {t}')
        return None

    @property
    def stock_name(self):

        url = f'https://finnhub.io/api/v1/search?q={self.ticker}&token={self.token}'

        try:
            data = json.loads(requests.get(url).text)
        except json.JSONDecodeError:
            print(f'JSON ERROR')
            return None
        
        for result in data['result']:
            if result['symbol'] == self.ticker:
                return result['description'].title()

        return None
