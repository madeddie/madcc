#!/usr/bin/env python
from ..utils import crypto_assets

import configparser
import sys

from clint import resources
from clint.arguments import Args
from tabulate import tabulate


def main():
    resources.init('madtech', 'madcc')
    if not resources.user.read('config.ini'):
        config = configparser.ConfigParser()
        config['crypto_assets'] = {}
        config['crypto_assets']['crypto_file'] = resources.user.path + '/crypto.txt'
        config['crypto_assets']['currency'] = 'eur'
        with resources.user.open('config.ini', 'w') as configfile:
            config.write(configfile)
    else:
        config = configparser.ConfigParser()
        with resources.user.open('config.ini', 'r') as configfile:
            config.read_file(configfile)

    args = Args()

    if next(iter(args.grouped.get('--currency', [])), '').upper() in crypto_assets.CURRENCIES:
        currency = args.grouped.get('--currency', {}).get(0)
    elif str(args.last or '').upper() in crypto_assets.CURRENCIES:
        currency = args.last
    else:
        currency = config['crypto_assets']['currency'].lower()

    if currency == 'btc':
        decimals = 10
    else:
        decimals = 2

    crypto_data = crypto_assets.parse_crypto_file(config['crypto_assets']['crypto_file'])
    if not crypto_data:
        sys.exit(1)

    headers, crypto_table = crypto_assets.generate_crypto_table(currency, crypto_data)
    print(tabulate(crypto_table, headers=headers, floatfmt='.{}f'.format(decimals)))


if __name__ == "__main__":
    main()
