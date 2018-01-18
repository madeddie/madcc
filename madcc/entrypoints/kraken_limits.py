from ..kraken.kraken import KrakenUtils


def main():
    k = KrakenUtils()
    deposit_limit = k.deposit_limit()
    withdraw_limit = k.withdraw_limit()

    print('deposit max: {} EUR'.format(deposit_limit))
    print('withdraw max: {} BTC'.format(withdraw_limit))
