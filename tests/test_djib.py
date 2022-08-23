from djib import __version__
from djib.rpc import KmsClient, DjibRpc


def test_version():
    assert __version__ == '0.1.0'


def test_kms(private_key: str):
    kms = KmsClient(private_key, is_devnet=True)
    a = 'Test Text'
    a_enc = kms.encrypt(a)
    a_dec = kms.decrypt(a_enc)
    assert a_dec == a


def test_rpc(private_key: str):
    rpc = DjibRpc(private_key, is_devnet=True)
    print(rpc.get_profile().data)


WALLET_PRIVATE_KEY = ""

test_rpc(WALLET_PRIVATE_KEY)
