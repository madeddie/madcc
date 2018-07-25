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


class CryptoAssets:
    def __init__(self, config, currency, decimals):
        self.config = config
        self.currency = currency
        self.decimals = decimals

    def convert(self, symbol, amount):
        # Covert fiat currencies from symbol to configured currency
        # TODO: do something when api fails
        if symbol.upper() == self.currency.upper():
            return([symbol, amount, 1, amount])
        else:
            convert_pair = '{}_{}'.format(symbol.upper(), self.currency.upper())
            res = requests.get(
                self.config['currency_api'],
                params={
                    'q': convert_pair,
                    'compact': 'y'
                }
            )
            res.raise_for_status()
            rate = res.json()[convert_pair]['val']
            return([symbol, amount, rate, amount * rate])

    def parse_crypto_file(self):
        # Parse crypto note file for assets and amounts
        m = re.compile(r'%s.*?%s' % ('# cryptocurrency', '#'), re.S)
        try:
            with open(self.config['crypto_file']) as f:
                crypto_data = list()
                res = m.search(f.read())
                for line in res.group(0).split('\n'):
                    if line.startswith('-'):
                        crypto_data.append(line.strip('- \n').split())
            return crypto_data

        except IOError as e:
            print('Unable to open crypto_data file: {}'.format(self.config['crypto_file']))
            return False

    def retrieve_ticker_data(self, crypto_data):
        # Retrieve list of specified ticker data from coinmarketcap
        # TODO: do something when api call fails
        coinmarketcap = Market()
        listings = coinmarketcap.listings()
        ticker_data = list()
        for idnum in [x['id'] for x in listings['data'] if x['website_slug'] in [z[0] for z in crypto_data]]:
            ticker_data.append(coinmarketcap.ticker(
                idnum,
                convert=self.currency)['data']
            )

        return ticker_data

    def generate_crypto_table(self, crypto_data):
        # Generate list of lists with crypto_data to display
        if not crypto_data:
            return False
        ticker_data = self.retrieve_ticker_data(crypto_data)
        portfolio_total = 0
        headers = [
            'symbol', 'amount', '%',
            '{} price'.format(self.currency), '{} total'.format(self.currency)
        ]
        table = list()
        for line in crypto_data:
            symbol = line[0]
            amount = float(line[1])
            if symbol.upper() in ('EUR', 'USD'):
                outcome = self.convert(symbol, amount)
                table.append(outcome)
                portfolio_total += outcome[3]
                continue
            price = [x['quotes'][self.currency.upper()]['price'] for x in ticker_data if x['website_slug'] == symbol][0]
            total = amount * float(price)
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
    config = {
        'currency_api': 'https://free.currencyconverterapi.com/api/v6/convert'
    }

    # Just for demo, not actual data
    crypto_data = [['bitcoin', '10.5'], ['ethereum', '109.25']]

    ca = CryptoAssets(config, currency, decimals)
    headers, crypto_table = ca.generate_crypto_table(crypto_data)
    return tabulate(crypto_table, headers=headers, floatfmt='.{}f'.format(decimals))


if __name__ == "__main__":  # pragma: no cover
    print(demo())
