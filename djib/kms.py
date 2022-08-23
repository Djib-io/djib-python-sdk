import base58
import requests
from jsonrpcclient.requests import request
from jsonrpcclient.responses import Ok
from jsonrpcclient.responses import parse
from nacl.encoding import Base64Encoder, HexEncoder
from nacl.public import PrivateKey, Box, PublicKey
from solana.keypair import Keypair

from djib.constants import *
from djib.dtypes import *


class KmsClient:
    _wallet_private_key: str
    _wallet_public_key: str
    _kms_api: str
    _sk_alice: Any
    _pk_alice: str
    _pk_bob: Any
    _engine: Box

    def __init__(self, wallet_private_key: str, is_devnet: bool = False):
        """ constructor
            :param wallet_public_key: str
            :param wallet_private_key: str
            :param is_devnet: bool
        """
        self._wallet_private_key = wallet_private_key
        tmp = base58.b58decode(self._wallet_private_key)[:32]
        self._wallet_public_key = str(Keypair.from_seed(tmp).public_key)
        self._kms_api = KMS_MAIN_ENDPOINT if not is_devnet else KMS_DEV_ENDPOINT
        self._sk_alice = PrivateKey.from_seed(tmp)
        self._pk_alice = self._sk_alice.public_key.encode(Base64Encoder).decode('utf-8')
        handshake_result = self._handshake()
        self._pk_bob = PublicKey(handshake_result.data['pkbob'], Base64Encoder)
        signed_signature = self._sign_message(handshake_result.data['message_to_sign'])
        self._auth(signed_signature)
        self._engine = Box(self._sk_alice, self._pk_bob)

    def _sign_message(self, message: str) -> str:
        """ signing a message using private key
            :param message: str
            :return: str
        """
        seed_from_private_key = base58.b58decode(self._wallet_private_key)[:32]
        kp = Keypair.from_seed(seed_from_private_key)
        return str(kp.sign(bytes(message, 'utf8')))

    def _call_kms(self, params: list, method: str):
        """ calling KMS API
            :param params: list
            :param method: str
            :return:
        """
        try:
            res = requests.post(self._kms_api, json=request(method, params))
            if res.status_code >= 500:
                raise Exception(f"{self._kms_api} is DOWN!")
            if res.status_code >= 400:
                raise Exception("Bad request!")
            if res.status_code == 200:
                rpc_response = parse(res.json())
                n = RPCResponse()
                if isinstance(rpc_response, Ok):
                    n.data = rpc_response.result
                    return n
                n.error = {
                    "message": rpc_response.message,
                    "data": rpc_response.data,
                    "code": rpc_response.code,
                }
            raise Exception("Unknown Error!")
        except Exception as e:
            raise e

    def _handshake(self) -> RPCResponse:
        """ handshake with KMS for creating keypairs
            :return: RPCResponse
        """
        return self._call_kms([self._wallet_public_key], "handshake")

    def _auth(self, signed_signature: str) -> RPCResponse:
        """ authenticate for validation of wallet
            :param signed_signature: str
            :return: RPCResponse
        """
        return self._call_kms([self._wallet_public_key, signed_signature, self._pk_alice], "auth")

    def encrypt(self, data: str) -> str:
        """ encrypt data
            :param data: str
            :return: str
        """
        return self._engine.encrypt(data.encode('utf-8'), None, HexEncoder).decode('utf-8')

    def decrypt(self, data: str) -> str:
        """ decrypt data
            :param data:
            :return:
        """
        return self._engine.decrypt(data.encode('utf-8'), None, HexEncoder).decode('utf-8')

    @property
    def wallet_public_key(self):
        return self._wallet_public_key
