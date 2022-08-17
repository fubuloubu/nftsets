# NFT Sets

Verified Sets of NFT Collections

## Dependencies

* [python3](https://www.python.org/downloads) version 3.7 or greater, python3-dev

## Installation

### via `pip`

You can install the latest release via [`pip`](https://pypi.org/project/pip/):

```bash
pip install nftsets
```

### via `setuptools`

You can clone the repository and use [`setuptools`](https://github.com/pypa/setuptools) for the most up-to-date version:

```bash
git clone https://github.com/ApeWorX/nftsets.git
cd nftsets
python3 setup.py install
```

## Quick Usage

NOTE: **Work in Progress!**

```py
>>> from nftsets import Manager
>>> nfts = Manager()

>>> nfts.available_sets()
[]

>>> nfts.install_set("nfts.opensea.eth")
>>> nfts.available_sets()
["opensea"]

>>> print(*(set.name for set in nfts))
PUNKS
BAYC
...
```

## Development

This project is in development and should be considered a beta.
Things might not be in their final state and breaking changes may occur.
Comments, questions, criticisms and pull requests are welcomed.

## License

This project is licensed under the [Apache 2.0](LICENSE).
