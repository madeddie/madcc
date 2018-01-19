#!/usr/bin/env python
import json
import re
import sys
import time
from datetime import datetime

import requests
from coinmarketcap import Market
from tabulate import tabulate

ticker_baseurl = 'https://api.coinmarketcap.com/v1/ticker/'
crypto_file = '/Users/madeddie/Documents/notes/crypto.txt'
missing_currencies = ('BTC', 'USD')
currencies = ('AUD', 'BRL', 'CAD', 'CHF', 'CLP', 'CNY', 'CZK', 'DKK', 'EUR',
              'GBP', 'HKD', 'HUF', 'IDR', 'ILS', 'INR', 'JPY', 'KRW', 'MXN',
              'MYR', 'NOK', 'NZD', 'PHP', 'PKR', 'PLN', 'RUB', 'SEK', 'SGD',
              'THB', 'TRY', 'TWD', 'ZAR') + missing_currencies


def convert(symbol, amount, currency):
    # Convert USD and EUR to their counterparts
    if symbol.upper() == currency.upper():
        return([symbol, amount, 1, amount])
    else:
        base_url = 'https://api.fixer.io/latest'
        # TODO: check if we can reach the API and the result is valid
        res = requests.get(
            base_url,
            params={'base': symbol.upper(), 'symbols': currency.upper()}
        )
        rate = res.json()['rates'][currency.upper()]
        return([symbol, amount, rate, amount * rate])


def main():
    if len(sys.argv) > 1 and sys.argv[1].upper() in currencies:
        currency = sys.argv.pop(1)
    else:
        currency = 'eur'

    if currency == 'btc':
        decimals = 10
    else:
        decimals = 2

    # TODO check if file exists and any results return
    # crypto_data = [line.strip('- \n').split() for line in open(crypto_file, 'r') if line.startswith('-')]
    m = re.compile(r'%s.*?%s' % ('# cryptocurrency', '#'), re.S)
    crypto_data = [line.strip('- \n').split() for line in m.search(open(crypto_file).read()).group(0).split('\n') if line.startswith('-')]

    coinmarketcap = Market()
    full_ticker_data = coinmarketcap.ticker(start=0, limit=2000, convert=currency)

    portfolio_total = 0
    headers = [
        'symbol', 'amount', '%',
        '{} price'.format(currency), '{} total'.format(currency)
    ]
    table = list()
    for line in crypto_data:
        symbol = line[0]
        amount = float(line[1])
        if symbol.upper() in ('EUR', 'USD'):
            outcome = convert(symbol, amount, currency)
            table.append(outcome)
            portfolio_total += outcome[3]
            continue
        ticker_data = next((x for x in full_ticker_data if x['id'] == symbol))
        price = float(ticker_data['price_{}'.format(currency)])
        total = amount * price
        portfolio_total += total
        table.append([symbol, amount, price, total])

    for idx, val in enumerate(table):
        table[idx].insert(-2, round(val[3] / (portfolio_total / 100), 2))

    table.sort(key=lambda x: x[4], reverse=True)
    table.append([
        'total', None, None,
        None, portfolio_total
    ])
    print(tabulate(table, headers=headers, floatfmt='.{}f'.format(decimals)))
