import pytest

from madcc.utils import crypto_assets


def test_convert(mocker):
    mocked_get = mocker.patch('requests.get')
    crypto_assets.convert('eur', 10, 'usd')
    mocked_get.assert_called_with(
        crypto_assets.currency_api,
        params={'base': 'EUR', 'symbols': 'USD'}
    )
