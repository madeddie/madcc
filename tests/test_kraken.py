import pytest
import requests_mock

from madcc.kraken import KrakenUtils
from madcc.entrypoints import kraken_limits


# some_api_key\nsome_api_secret both base64 encoded
raw_kraken_auth = """c29tZV9hcGlfa2V5Cg==
c29tZV9hcGlfc2VjcmV0Cg=="""

kraken_limits_result = """deposit max: 100 EUR
withdraw max: 100 BTC"""


@pytest.fixture(scope='session')
def config_dir(tmpdir_factory):
    return tmpdir_factory.mktemp('madcc')


def test_kraken_utils_set_auth(config_dir):
    config_dir.join('kraken.auth').write(raw_kraken_auth)
    kraken = KrakenUtils(str(config_dir.join('kraken.auth')))

    assert kraken.api_key == raw_kraken_auth.splitlines()[0]
    assert kraken.api_secret == raw_kraken_auth.splitlines()[1]


# def test_kraken_utils_clint_auth(config_dir):
#     with pytest.raises(SystemExit):
#         # kraken = KrakenUtils()
#         kraken = KrakenUtils(str(config_dir.join('kraken.auth')))


def test_kraken_utils_api_live(config_dir):
    kraken = KrakenUtils(str(config_dir.join('kraken.auth')))
    with requests_mock.Mocker() as mock:
        mock.post('https://api.kraken.com/0/public/Time', json={'error': []})

        assert kraken.api_live() is True


def test_kraken_utils_api_dead(config_dir):
    kraken = KrakenUtils(str(config_dir.join('kraken.auth')))
    with requests_mock.Mocker() as mock:
        mock.post('https://api.kraken.com/0/public/Time', json={'error': ['something']})

        assert kraken.api_live() is False


def test_kraken_limits(config_dir):
    with requests_mock.Mocker() as mock:
        mock.post('https://api.kraken.com/0/public/Time', json={'error': []})
        mock.post('https://api.kraken.com/0/private/DepositMethods', json={
            'error': [],
            'result': [{'limit': 100}]
        })
        mock.post('https://api.kraken.com/0/private/WithdrawInfo', json={
            'error': [],
            'result': {'limit': 100}
        })
        result = kraken_limits.main(str(config_dir.join('kraken.auth')))

    assert result == kraken_limits_result
