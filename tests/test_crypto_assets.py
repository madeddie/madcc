import pytest

from madcc.utils import crypto_assets
from madcc.entrypoints import crypto_assets as crypto_assets_cli


# Testing data
currency_api = 'http://data.fixer.io/latest?access_key=S0m3k3y'

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

crypto_output = """symbol      amount      %    eur price    eur total
--------  --------  -----  -----------  -----------
bitcoin      12.05  52.35      6615.32     79714.56
ethereum     80.20  25.88       491.39     39409.12
litecoin    250.00  21.44       130.55     32637.68
eur         500.00   0.33         1.00       500.00
total                                     152261.37"""


def test_convert(mocker):
    mocker.patch('requests.get')
    crypto_assets.convert('eur', 10, 'usd', currency_api)

    crypto_assets.requests.get.assert_called_with(
        currency_api,
        params={'base': 'EUR', 'symbols': 'USD'}
    )


def test_convert_same():
    assert crypto_assets.convert('eur', 10, 'eur', currency_api) == ['eur', 10, 1, 10]


def test_parse_crypto_file(mocker):
    with mocker.mock_module.patch('builtins.open', mocker.mock_open(read_data=raw_crypto_file)) as m:
        result = crypto_assets.parse_crypto_file('crypto_file')

    m.assert_called_once_with('crypto_file')
    assert result == parsed_crypto_file


def test_parse_crypto_file_fail_open(mocker):
    with mocker.mock_module.patch('builtins.open', mocker.mock_open()) as m:
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
    result = crypto_assets.generate_crypto_table('eur', parsed_crypto_file, currency_api)

    assert result == generated_crypto_table


def test_generate_crypto_table_missing_data():
    assert crypto_assets.generate_crypto_table('eur', None, currency_api) is False


def test_demo(mocker):
    mocker.patch.object(crypto_assets, 'generate_crypto_table', return_value=generated_crypto_table)

    assert crypto_assets.demo() == crypto_output


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
    mocker.patch.object(crypto_assets_cli, 'crypto_assets')
    crypto_assets_cli.crypto_assets.generate_crypto_table.return_value = generated_crypto_table
    config_dir.join('crypto.txt').write(raw_crypto_file)

    assert crypto_assets_cli.main() == crypto_output


def test_crypto_assets_cli_currency_eur(mocker, config_dir):
    mocker.patch.object(crypto_assets_cli, 'resources')
    crypto_assets_cli.resources.user.read.return_value = None
    crypto_assets_cli.resources.user.path = str(config_dir)
    crypto_assets_cli.resources.user.open.return_value = config_dir.join('config.json')
    mocker.patch('madcc.utils.crypto_assets.generate_crypto_table', autospect=True, return_value=generated_crypto_table)
    mocker.patch.object(crypto_assets_cli, 'Args')
    crypto_assets_cli.Args.return_value.last = 'eur'
    crypto_assets_cli.main()

    crypto_assets_cli.crypto_assets.generate_crypto_table.assert_called_with('eur', parsed_crypto_file, currency_api)


def test_crypto_assets_cli_currency_usd(mocker, config_dir):
    mocker.patch.object(crypto_assets_cli, 'resources')
    crypto_assets_cli.resources.user.read.return_value = None
    crypto_assets_cli.resources.user.path = str(config_dir)
    crypto_assets_cli.resources.user.open.return_value = config_dir.join('config.json')
    mocker.patch('madcc.utils.crypto_assets.generate_crypto_table', autospect=True, return_value=generated_crypto_table)
    mocker.patch.object(crypto_assets_cli, 'Args')
    crypto_assets_cli.Args.return_value.last = 'usd'
    crypto_assets_cli.main()

    crypto_assets_cli.crypto_assets.generate_crypto_table.assert_called_with('usd', parsed_crypto_file, currency_api)


def test_crypto_assets_cli_currency_btc(mocker, config_dir):
    mocker.patch.object(crypto_assets_cli, 'resources')
    crypto_assets_cli.resources.user.read.return_value = None
    crypto_assets_cli.resources.user.path = str(config_dir)
    crypto_assets_cli.resources.user.open.return_value = config_dir.join('config.json')
    mocker.patch('madcc.utils.crypto_assets.generate_crypto_table', autospect=True, return_value=generated_crypto_table)
    mocker.patch.object(crypto_assets_cli, 'Args')
    crypto_assets_cli.Args.return_value.last = 'btc'
    crypto_assets_cli.main()

    crypto_assets_cli.crypto_assets.generate_crypto_table.assert_called_with('btc', parsed_crypto_file, currency_api)


def test_crypto_assets_cli_currency_unknown(mocker, config_dir):
    mocker.patch.object(crypto_assets_cli, 'resources')
    crypto_assets_cli.resources.user.read.return_value = None
    crypto_assets_cli.resources.user.path = str(config_dir)
    crypto_assets_cli.resources.user.open.return_value = config_dir.join('config.json')
    mocker.patch('madcc.utils.crypto_assets.generate_crypto_table', autospect=True, return_value=generated_crypto_table)
    mocker.patch.object(crypto_assets_cli, 'Args')
    crypto_assets_cli.Args.return_value.last = 'abc'
    crypto_assets_cli.main()

    crypto_assets_cli.crypto_assets.generate_crypto_table.assert_called_with('eur', parsed_crypto_file, currency_api)
