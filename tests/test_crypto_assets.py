from unittest.mock import patch

import pytest

from madcc.utils import crypto_assets
from madcc.entrypoints import crypto_assets as crypto_assets_cli


# Testing data
raw_crypto_file = """
# cryptocurrency

- bitcoin 12.05
    - some comment
    - maybe mentioning ledger contains 12.05
- ethereum 80.2
- litecoin 250
    - some comment
- eur 500
    - also accepts usd

# closing hash"""

parsed_crypto_file = [
    ['bitcoin', '12.05'],
    ['ethereum', '80.2'],
    ['litecoin', '250'],
    ['eur', '500']
]

full_ticker_data = [
    {'id': 'bitcoin', 'price_eur': '6615.31631639'},
    {'id': 'ethereum', 'price_eur': '491.385586985'},
    {'id': 'litecoin', 'price_eur': '130.550739603'}
]

generated_crypto_table = (
    ['symbol', 'amount', '%', 'eur price', 'eur total'],
    [
        ['bitcoin', 12.05, 52.35, 6615.31631639, 79714.5616124995],
        ['ethereum', 80.2, 25.88, 491.385586985, 39409.124076197],
        ['litecoin', 250.0, 21.44, 130.550739603, 32637.684900750002],
        ['eur', 500.0, 0.33, 1, 500.0],
        ['total', None, None, None, 152261.3705894465]
    ]
)

demo_output = """symbol      amount      %    eur price    eur total
--------  --------  -----  -----------  -----------
bitcoin      12.05  52.35      6615.32     79714.56
ethereum     80.20  25.88       491.39     39409.12
litecoin    250.00  21.44       130.55     32637.68
eur         500.00   0.33         1.00       500.00
total                                     152261.37"""


def test_convert(mocker):
    mocker.patch('requests.get')
    crypto_assets.convert('eur', 10, 'usd')
    crypto_assets.requests.get.assert_called_with(
        crypto_assets.currency_api,
        params={'base': 'EUR', 'symbols': 'USD'}
    )


def test_convert_same():
    assert crypto_assets.convert('eur', 10, 'eur') == ['eur', 10, 1, 10]


def test_parse_crypto_file(mocker):
    with patch('builtins.open', mocker.mock_open(read_data=raw_crypto_file)) as m:
        result = crypto_assets.parse_crypto_file('crypto_file')

    m.assert_called_once_with('crypto_file')
    assert result == parsed_crypto_file


def test_parse_crypto_file_fail_open(mocker):

    with patch('builtins.open', mocker.mock_open()) as m:
        m.side_effect = IOError
        result = crypto_assets.parse_crypto_file('crypto_file')

    m.assert_called_once_with('crypto_file')
    assert result is False


def test_retrieve_ticker_data(mocker):
    mocker.patch('coinmarketcap.Market.ticker')
    result = crypto_assets.retrieve_ticker_data('eur')

    crypto_assets.Market.ticker.assert_called_with(start=0, limit=2000, convert='eur')


def test_generate_crypto_table(mocker):
    mocker.patch.object(crypto_assets, 'retrieve_ticker_data', return_value=full_ticker_data)

    result = crypto_assets.generate_crypto_table('eur', parsed_crypto_file)
    assert result == generated_crypto_table


def test_generate_crypto_table_missing_data():
    assert crypto_assets.generate_crypto_table('eur', None) is False


def test_demo(mocker):
    mocker.patch.object(crypto_assets, 'generate_crypto_table', return_value=generated_crypto_table)
    assert crypto_assets.demo() == demo_output
