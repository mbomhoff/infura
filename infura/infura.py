# coding:utf-8
import os
import tempfile
import requests_cache


class Client():

    def __init__(self,
                 project_id,
                 project_secret=None,
                 network='mainnet',
                 cache_backend='sqlite',
                 cache_expire_after=5,
                 ):

        # verify network
        if network not in ['mainnet', 'ropsten', 'kovan', 'rinkeby', 'polygon-mainnet']:
            raise Exception('network could only be mainnet/ropsten/kovan/rinkeby')

        # id/secret
        self._project_id = project_id
        self._project_secret = project_secret
        self._network = network

        # Endpoint URL
        self._endpoint = 'https://{network}.infura.io/v3/{project_id}'.format(
            network=self._network,
            project_id=self._project_id,
        )

        # headers
        self._headers = {
            'Content-Type': 'application/json',
        }

        # params
        self._params = []

        # payload
        self._payload = {
            'jsonrpc': '2.0',
            'id': 1,
        }

        # session & cache
        self._session = None
        self._cache_name = os.path.join(tempfile.gettempdir(), 'etherscan_cache')
        self._cache_backend = cache_backend
        self._cache_expire_after = cache_expire_after

    @property
    def session(self):
        if not self._session:
            self._session = requests_cache.CachedSession(
                cache_name=self._cache_name,
                backend=self._cache_backend,
                expire_after=self._cache_expire_after,
            )
            self._session.headers.update(
                {
                    'User-agent': 'infura - python wrapper '
                                  'around infura.io (github.com/neoctobers/infura)'
                }
            )
        return self._session

    def __req(self):
        self._payload['params'] = self._params

        r = self.session.post(
            url=self._endpoint,
            headers=self._headers,
            json=self._payload,
        ).json()

        # todo: handle with error
        # sample: {'jsonrpc': '2.0', 'id': 1, 'error': {'code': -32602, 'message': 'invalid argument 0: json: cannot unmarshal hex string of odd length into Go value of type common.Address'}}
        return r

    def eth_get_gas_price(self):
        self._payload['method'] = 'eth_gasPrice'

        r = self.__req()

        return int(r['result'], 16)

    def eth_get_balance(self, address: str, block='latest'):
        self._payload['method'] = 'eth_getBalance'
        self._params = [address, block]

        r = self.__req()

        return int(r['result'], 16)

    def eth_get_block_number(self):
        self._payload['method'] = 'eth_blockNumber'

        r = self.__req()

        return int(r['result'], 16)

    def eth_get_block_by_number(self, block_number, show_transaction_details: bool = False):
        self._payload['method'] = 'eth_getBlockByNumber'
        self._params = [hex(block_number), show_transaction_details]

        r = self.__req()

        return r['result']

    def eth_get_transaction_receipt(self, tx_hash):
        self._payload['method'] = 'eth_getTransactionReceipt'
        self._params = [tx_hash]

        r = self.__req()

        return r['result']

    def eth_get_code(self, addr, block):
        self._payload['method'] = 'eth_getCode'
        self._params = [addr, block]

        r = self.__req()

        return r['result']

    def eth_call(self, fromAddr, toAddr, gas, gasPrice, value, data):
        self._payload['method'] = 'eth_call'
        self._params = [fromAddr, toAddr, hex(gas), hex(gasPrice), hex(value), data]

        r = self.__req()

        return r['result']

    def eth_call_erc20(self, to, data):
        self._payload['method'] = 'eth_call'
        self._params = [to, data]

        r = self.__req()

        return r['result']
