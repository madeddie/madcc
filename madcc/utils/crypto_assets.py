#!/usr/bin/env python
import re
import sys

import requests
from coinmarketcap import Market
from tabulate import tabulate

MISSING_CURRENCIES = ('BTC', 'USD')
CURRENCIES = ('AUD', 'BRL', 'CAD', 'CHF', 'CLP', 'CNY', 'CZK', 'DKK', 'EUR',
              'GBP', 'HKD', 'HUF', 'IDR', 'ILS', 'INR', 'JPY', 'KRW', 'MXN',
              'MYR', 'NOK', 'NZD', 'PHP', 'PKR', 'PLN', 'RUB', 'SEK', 'SGD',
              'THB', 'TRY', 'TWD', 'ZAR') + MISSING_CURRENCIES

currency_api = 'https://api.fixer.io/latest'


def convert(symbol, amount, currency):
    # Covert USD to EUR and vice versa
    # TODO: do something when api fails
    if symbol.upper() == currency.upper():
        return([symbol, amount, 1, amount])
    else:
        res = requests.get(
            currency_api,
            params={'base': symbol.upper(), 'symbols': currency.upper()}
        )
        res.raise_for_status()
        rate = res.json()['rates'][currency.upper()]
        return([symbol, amount, rate, amount * rate])


def parse_crypto_file(crypto_file):
    # Parse crypto note file for assets and amounts
    m = re.compile(r'%s.*?%s' % ('# cryptocurrency', '#'), re.S)
    try:
        with open(crypto_file) as f:
            crypto_data = list()
            res = m.search(f.read())
            for line in res.group(0).split('\n'):
                if line.startswith('-'):
                    crypto_data.append(line.strip('- \n').split())
        return crypto_data

    except IOError as e:
        print('Unable to open crypto_data file: {}'.format(crypto_file))
        return False


def retrieve_ticker_data(currency):
    # TODO: do something when api call fails
    coinmarketcap = Market()
    return coinmarketcap.ticker(start=0, limit=2000, convert=currency)


def generate_crypto_table(currency, crypto_data):
    # Generate list of lists with crypto_data to display
    if not crypto_data:
        return False
    full_ticker_data = retrieve_ticker_data(currency)
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

    return headers, table


def demo():
    currency = 'usd'
    decimals = 2

    # Just for demo, not actual data
    crypto_data = [['bitcoin', '10.5'], ['ethereum', '109.25']]

    headers, crypto_table = generate_crypto_table(currency, crypto_data)
    return tabulate(crypto_table, headers=headers, floatfmt='.{}f'.format(decimals))


if __name__ == "__main__":  # pragma: no cover
    print(demo())
