from ..kraken.kraken import KrakenUtils


def main(authfile=None):
    k = KrakenUtils(authfile=authfile)
    deposit_limit = k.deposit_limit()
    withdraw_limit = k.withdraw_limit()

    return 'deposit max: {} EUR\nwithdraw max: {} BTC'.format(deposit_limit,
                                                              withdraw_limit)


if __name__ == "__main__":  # pragma: no cover
    print(main())
