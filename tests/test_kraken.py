import pytest

from madcc.kraken import KrakenUtils
from madcc.entrypoints import kraken_limits


# some_api_key\nsome_api_secret both base64 encoded
raw_kraken_auth = """c29tZV9hcGlfa2V5Cg==
c29tZV9hcGlfc2VjcmV0Cg=="""

wrong_credentials_result = """deposit max: False EUR
withdraw max: False BTC"""


@pytest.fixture(scope='session')
def config_dir(tmpdir_factory):
    return tmpdir_factory.mktemp('madcc')


# TODO: this tests the krakenex api more than my code
# also mock the kraken api to test failures better and circumvent network
# access
def test_kraken_limits_wrong_credentials(mocker, config_dir):
    config_dir.join('kraken.auth').write(raw_kraken_auth)
    result = kraken_limits.main(str(config_dir.join('kraken.auth')))

    assert result == wrong_credentials_result
