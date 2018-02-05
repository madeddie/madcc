#!/usr/bin/env python
import re
import sys

import requests
from clint.arguments import Args
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
        res = requests.get(
            base_url,
            params={'base': symbol.upper(), 'symbols': currency.upper()}
        )
        res.raise_for_status()
        rate = res.json()['rates'][currency.upper()]
        return([symbol, amount, rate, amount * rate])


def main():
    args = Args()

    if next(iter(args.grouped.get('--currency', [])), '').upper() in currencies:
        currency = args.grouped.get('--currency', {}).get(0)
    elif str(args.last or '').upper() in currencies:
        currency = args.last
    else:
        currency = 'eur'

    if currency == 'btc':
        decimals = 10
    else:
        decimals = 2

    m = re.compile(r'%s.*?%s' % ('# cryptocurrency', '#'), re.S)
    try:
        crypto_data = [line.strip('- \n').split() for line in m.search(open(crypto_file).read()).group(0).split('\n') if line.startswith('-')]
    except IOError as e:
        print('Unable to open crypto_data file: {}'.format(3))
        sys.exit()

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
