#!/usr/bin/env python

import json
import os
import sys

import krakenex
import requests

from ..conf import settings


class KrakenUtils(object):
    def __init__(self):
        # TODO: get config somewhere else, don't load it in the module?
        settings.init()
        self._set_auth(str(settings.user_dir.joinpath('kraken.auth')))
        self.api = krakenex.API(key=self.api_key, secret=self.api_secret)
        if not self.api_live():
            # TODO: use logging instead of print
            print('Kraken API failure')
            sys.exit(1)

    def _set_auth(self, auth_file=None):
        """Read the api auth data from file"""
        self.api_key, self.api_secret = open(auth_file).read().splitlines()

    def api_live(self):
        res = self.api.query_public('Time')
        if res['error']:
            return False
        else:
            return True

    def deposit_limit(self, retry=5):
        for i in range(0, retry):
            try:
                res = self.api.query_private('DepositMethods', {'asset': 'ZEUR'})
            except json.decoder.JSONDecodeError as err:
                continue
            else:
                if res['error']:
                    # print(','.join(res['error']))
                    continue
                limit = res['result'][0]['limit']
                return limit

        return False

    def withdraw_limit(self, retry=5):
        for i in range(0, retry):
            try:
                res = self.api.query_private('WithdrawInfo', {'asset': 'XXBT', 'key': 'gdax', 'amount': 1})
            except json.decoder.JSONDecodeError as err:
                continue
            else:
                if res['error']:
                    # print(','.join(res['error']))
                    continue
                limit = res['result']['limit']
                return limit

        return False
