import re

import click

from .manager import Manager
from .typing import Symbol


class NftSetChoice(click.Choice):
    def __init__(self, case_sensitive=True):
        self.case_sensitive = case_sensitive

    @property
    def choices(self):
        return list(Manager().available_nftsets())


@click.group()
@click.version_option(message="%(version)s")
def cli():
    """
    Utility for working with installed NFT Sets
    """


@cli.command(name="list", short_help="Display the names and versions of all installed Sets")
def _list():
    manager = Manager()

    available = manager.available_nftsets()
    if available:
        click.echo("Installed Sets:")
        for nftset in map(manager.get_nftset, available):
            click.echo(f"- {nftset.name} ({nftset.timestamp})")

    else:
        click.echo("WARNING: No Sets exist!")


@cli.command(short_help="Install a new Set")
@click.argument("uri")
def install(uri):
    manager = Manager()

    manager.install_nftset(uri)


@cli.command(short_help="Remove an existing Set")
@click.argument("name", type=NftSetChoice())
def remove(name):
    manager = Manager()

    manager.remove_nftset(name)


@cli.command(short_help="Choose default Set")
@click.argument("name", type=NftSetChoice())
def set_default(name):
    manager = Manager()

    manager.set_default_nftset(name)

    click.echo(f"Default Set is now: '{manager.default_nftset}'")


@cli.command(short_help="Display all installed Collections")
@click.option("--search", default="")
@click.option("--set-name", type=NftSetChoice(), default=None)
@click.option("--chain-id", default=1, type=int)
def list_collections(search, set_name, chain_id):
    manager = Manager()

    if not manager.default_nftset:
        raise click.ClickException("No Sets available!")

    pattern = re.compile(search or ".*")

    for collection_info in filter(
        lambda t: pattern.match(t.symbol),
        manager.get_collections(set_name, chain_id),
    ):
        click.echo("{address} ({symbol})".format(**collection_info.dict()))


@cli.command(short_help="Display the info for a particular collection")
@click.argument("symbol", type=Symbol)
@click.option("--set-name", type=NftSetChoice(), default=None)
@click.option("--case-insensitive", default=False, is_flag=True)
@click.option("--chain-id", default=1, type=int)
def collection_info(symbol, set_name, chain_id, case_insensitive):
    manager = Manager()

    if not manager.default_nftset:
        raise click.ClickException("No Sets available!")

    collection_info = manager.get_collection_info(symbol, set_name, chain_id, case_insensitive)
    collection_info = collection_info.dict()

    click.echo(
        """
        Name: {name}
      Symbol: {symbol}
    Chain ID: {chainId}
     Address: {address}
    """.format(
            **collection_info
        )
    )
