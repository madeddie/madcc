import pytest

from madcc.utils import crypto_assets
from madcc.utils.crypto_assets import CryptoAssets
from madcc.entrypoints import crypto_assets as crypto_assets_cli


# Testing data
config = {
    "crypto_file": "crypto_file",
    "currency": "usd",
    "currency_api": "https://free.currencyconverterapi.com/api/v6/convert"
}

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
    {'id': 1, 'name': 'Bitcoin', 'quotes': {'EUR': {'price': 6615.31631639}}, 'rank': 1, 'symbol': 'BTC', 'website_slug': 'bitcoin'},
    {'id': 2, 'name': 'Litecoin', 'quotes': {'EUR': {'price': 130.550739603}}, 'rank': 7, 'symbol': 'LTC', 'website_slug': 'litecoin'},
    {'id': 1027, 'name': 'Ethereum', 'quotes': {'EUR': {'price': 491.385586985}}, 'rank': 2, 'symbol': 'ETH', 'website_slug': 'ethereum'}
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

crypto_output = """symbol      amount      %    eur price    eur total
--------  --------  -----  -----------  -----------
bitcoin      12.05  52.35      6615.32     79714.56
ethereum     80.20  25.88       491.39     39409.12
litecoin    250.00  21.44       130.55     32637.68
eur         500.00   0.33         1.00       500.00
total                                     152261.37"""


def test_convert(mocker):
    ca = CryptoAssets(config, 'USD', '')
    mocker.patch('requests.get')
    ca.convert('eur', 10)

    crypto_assets.requests.get.assert_called_with(
        config['currency_api'],
        params={'q': 'EUR_USD', 'compact': 'y'}
    )


def test_convert_same():
    ca = CryptoAssets(config, 'eur', '')
    assert ca.convert('eur', 10) == ['eur', 10, 1, 10]


def test_parse_crypto_file(mocker):
    ca = CryptoAssets(config, 'eur', '')
    with mocker.mock_module.patch('builtins.open', mocker.mock_open(read_data=raw_crypto_file)) as m:
        result = ca.parse_crypto_file()

    m.assert_called_once_with('crypto_file')
    assert result == parsed_crypto_file


def test_parse_crypto_file_fail_open(mocker):
    ca = CryptoAssets(config, 'eur', '')
    with mocker.mock_module.patch('builtins.open', mocker.mock_open()) as m:
        m.side_effect = IOError
        result = ca.parse_crypto_file()

    m.assert_called_once_with('crypto_file')
    assert result is False


def test_retrieve_ticker_data(mocker):
    ca = CryptoAssets(config, 'eur', '')
    mocker.patch('coinmarketcap.Market.ticker')
    result = ca.retrieve_ticker_data(parsed_crypto_file)

    crypto_assets.Market.ticker.assert_called_with(1027, convert='eur')


def test_generate_crypto_table(mocker):
    ca = CryptoAssets(config, 'eur', '')
    mocker.patch.object(ca, 'retrieve_ticker_data', return_value=full_ticker_data)
    result = ca.generate_crypto_table(parsed_crypto_file)

    assert result == generated_crypto_table


def test_demo(mocker):
    mocker.patch.object(crypto_assets.CryptoAssets, 'generate_crypto_table', return_value=generated_crypto_table)

    assert crypto_assets.demo() == crypto_output


def test_generate_crypto_table_missing_data():
    ca = CryptoAssets(config, 'eur', '')
    assert ca.generate_crypto_table(None) is False


@pytest.fixture(scope='session')
def config_dir(tmpdir_factory):
    return tmpdir_factory.mktemp('madcc')


def test_crypto_assets_cli_no_config(mocker, config_dir):
    mocker.patch.object(crypto_assets_cli, 'resources')
    crypto_assets_cli.resources.user.read.return_value = None
    crypto_assets_cli.resources.user.path = str(config_dir)
    crypto_assets_cli.resources.user.open.return_value = config_dir.join('config.json')
    crypto_assets_cli.main()

    crypto_assets_cli.resources.user.open.assert_called_once_with('config.json', 'w')


def test_crypto_assets_cli_without_data(mocker, config_dir):
    mocker.patch.object(crypto_assets_cli, 'resources')
    crypto_assets_cli.resources.user.read.return_value = True
    crypto_assets_cli.resources.user.open.return_value = config_dir.join('config.json')
    crypto_assets_cli.main()

    crypto_assets_cli.resources.user.open.assert_called_once_with('config.json', 'r')
    assert crypto_assets_cli.main() is False


def test_crypto_assets_cli_with_data(mocker, config_dir):
    mocker.patch.object(crypto_assets_cli, 'resources')
    crypto_assets_cli.resources.user.read.return_value = None
    crypto_assets_cli.resources.user.path = str(config_dir)
    crypto_assets_cli.resources.user.open.return_value = config_dir.join('config.json')
    mocker.patch.object(crypto_assets_cli.CryptoAssets, 'generate_crypto_table')
    crypto_assets_cli.CryptoAssets.generate_crypto_table.return_value = generated_crypto_table
    config_dir.join('crypto.txt').write(raw_crypto_file)

    assert crypto_assets_cli.main() == crypto_output


def test_crypto_assets_cli_currency_eur(mocker, config_dir):
    mocker.patch.object(crypto_assets_cli, 'resources')
    crypto_assets_cli.resources.user.read.return_value = None
    crypto_assets_cli.resources.user.path = str(config_dir)
    crypto_assets_cli.resources.user.open.return_value = config_dir.join('config.json')
    mocker.patch.object(crypto_assets_cli.CryptoAssets, 'generate_crypto_table')
    crypto_assets_cli.CryptoAssets.generate_crypto_table.return_value = generated_crypto_table
    mocker.patch.object(crypto_assets_cli, 'Args')
    crypto_assets_cli.Args.return_value.last = 'eur'
    crypto_assets_cli.main()

    crypto_assets_cli.CryptoAssets.generate_crypto_table.assert_called_with(parsed_crypto_file)


def test_crypto_assets_cli_currency_usd(mocker, config_dir):
    mocker.patch.object(crypto_assets_cli, 'resources')
    crypto_assets_cli.resources.user.read.return_value = None
    crypto_assets_cli.resources.user.path = str(config_dir)
    crypto_assets_cli.resources.user.open.return_value = config_dir.join('config.json')
    mocker.patch.object(crypto_assets_cli.CryptoAssets, 'generate_crypto_table')
    crypto_assets_cli.CryptoAssets.generate_crypto_table.return_value = generated_crypto_table
    mocker.patch.object(crypto_assets_cli, 'Args')
    crypto_assets_cli.Args.return_value.last = 'usd'
    crypto_assets_cli.main()

    crypto_assets_cli.CryptoAssets.generate_crypto_table.assert_called_with(parsed_crypto_file)


def test_crypto_assets_cli_currency_btc(mocker, config_dir):
    mocker.patch.object(crypto_assets_cli, 'resources')
    crypto_assets_cli.resources.user.read.return_value = None
    crypto_assets_cli.resources.user.path = str(config_dir)
    crypto_assets_cli.resources.user.open.return_value = config_dir.join('config.json')
    mocker.patch.object(crypto_assets_cli.CryptoAssets, 'generate_crypto_table')
    crypto_assets_cli.CryptoAssets.generate_crypto_table.return_value = generated_crypto_table
    mocker.patch.object(crypto_assets_cli, 'Args')
    crypto_assets_cli.Args.return_value.last = 'btc'
    crypto_assets_cli.main()

    crypto_assets_cli.CryptoAssets.generate_crypto_table.assert_called_with(parsed_crypto_file)


def test_crypto_assets_cli_currency_unknown(mocker, config_dir):
    mocker.patch.object(crypto_assets_cli, 'resources')
    crypto_assets_cli.resources.user.read.return_value = None
    crypto_assets_cli.resources.user.path = str(config_dir)
    crypto_assets_cli.resources.user.open.return_value = config_dir.join('config.json')
    mocker.patch.object(crypto_assets_cli.CryptoAssets, 'generate_crypto_table')
    crypto_assets_cli.CryptoAssets.generate_crypto_table.return_value = generated_crypto_table
    mocker.patch.object(crypto_assets_cli, 'Args')
    crypto_assets_cli.Args.return_value.last = 'abc'
    crypto_assets_cli.main()

    crypto_assets_cli.CryptoAssets.generate_crypto_table.assert_called_with(parsed_crypto_file)
