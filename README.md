<div align="center">
    <img src="https://4289938616-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2F6MrZ6BqPMP2mmJKSKsG8%2Ficon%2F5q4QZZ6hqugOY1FCi0Mw%2Flogo.svg?alt=media&token=114140fd-3e6b-4ba9-8925-07c50a835eb5" width="25%" height="25%">
</div>

---

# Djib Python SDK

It's the base Python library for interacting with Djib network.
You can use it interact
with the Djib network. 

## Quickstart

### Installation

```sh
pip install djib
```

### General RPC Usage

```py
from djib.rpc import DjibRpc

WALLET_PRIVATE_KEY = '<Base58 encoded string>'

try:
    rpc = DjibRpc(WALLET_PRIVATE_KEY, is_devnet=True)

    # status of drive
    response = rpc.status()

    if response.error:
        print(f"Error: {response.error['message']}, Code: {response.error['code']}, Data: {response.error['data']}")
    else:
        print(response.data)
except Exception as e:
    print(f"Error: {str(e)}")
```

### KMS Usage

```py
from djib.rpc import KmsClient

WALLET_PRIVATE_KEY = '<Base58 encoded string>'

try:
    kms = KmsClient(WALLET_PRIVATE_KEY, is_devnet=True)
    a = 'Hello, World!'
    a_enc = kms.encrypt(a)
    a_dec = kms.decrypt(a_enc)
    assert a_dec == a
except Exception as e:
    print(f"Error: {str(e)}")
```


## Development

### Setup

1. Install [poetry](https://python-poetry.org/docs/#installation)
2. Install dev dependencies:

```sh
poetry install
```

3. Activate the poetry shell.

```sh
poetry shell
```
