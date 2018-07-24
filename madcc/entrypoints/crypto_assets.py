#!/usr/bin/env python
from ..utils import crypto_assets

import json
import sys

from clint import resources
from clint.arguments import Args
from tabulate import tabulate


def main():
    resources.init('madtech', 'madcc')
    if not resources.user.read('config.json'):
        config = dict()
        config['crypto_assets'] = dict()
        config['crypto_assets']['crypto_file'] = resources.user.path + '/crypto.txt'
        config['crypto_assets']['currency'] = 'eur'
        config['crypto_assets']['currency_api'] = 'http://data.fixer.io/latest?access_key=S0m3k3y'

        configfile = resources.user.open('config.json', 'w')
        configfile.write(json.dumps(config, sort_keys=True, indent=4))
    else:
        configfile = resources.user.open('config.json', 'r')
        config = json.loads(configfile.read())

    args = Args()

    if next(iter(args.grouped.get('--currency', [])), '').upper() in crypto_assets.CURRENCIES:
        currency = next(iter(args.grouped.get('--currency', [])), '')
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
        return False

    headers, crypto_table = crypto_assets.generate_crypto_table(
        currency,
        crypto_data,
        config['crypto_assets']['currency_api']
    )
    return tabulate(crypto_table, headers=headers, floatfmt='.{}f'.format(decimals))


if __name__ == "__main__":  # pragma: no cover
    print(main())
