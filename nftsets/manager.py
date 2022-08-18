from typing import Iterator, List, Optional

import requests  # type: ignore

from . import config
from .typing import ChainId, CollectionInfo, NftSet, Symbol


class Manager:
    def __init__(self):
        # NOTE: Folder should always exist, even if empty
        self.cache_folder = config.DEFAULT_CACHE_PATH
        self.cache_folder.mkdir(exist_ok=True)

        # Load all the ones cached on disk
        self.installed = {}
        for path in self.cache_folder.glob("*.json"):
            nftset = NftSet.parse_file(path)
            self.installed[nftset.name] = nftset

        self.default = config.DEFAULT_NFTSET
        if not self.default:
            # Default might be cached on disk (does not override config)
            default_cachefile = self.cache_folder.joinpath(".default")

            if default_cachefile.exists():
                self.default = default_cachefile.read_text()

            elif len(self.installed) > 0:
                # Not cached on disk, use first installed list
                self.default = next(iter(self.installed))

    def install(self, uri: str) -> str:
        """
        Install the nftset at the given URI, return the name of the installed list
        (for reference purposes)
        """
        # Load and store the nftset
        response = requests.get(uri)
        response.raise_for_status()
        nftset = NftSet.parse_obj(response.json())
        self.installed[nftset.name] = nftset

        # Cache it on disk for later instances
        self.cache_folder.mkdir(exist_ok=True)
        token_list_file = self.cache_folder.joinpath(f"{nftset.name}.json")
        token_list_file.write_text(nftset.json())

        return nftset.name

    def remove(self, nftset_name: str) -> None:
        nftset = self.installed[nftset_name]

        if nftset.name == self.default:
            self.default = ""

        token_list_file = self.cache_folder.joinpath(f"{nftset.name}.json")
        token_list_file.unlink()

        del self.installed[nftset.name]

    def set_default(self, name: str) -> None:
        if name not in self.installed:
            raise ValueError(f"Unknown token list: {name}")

        self.default = name

        # Cache it on disk too
        self.cache_folder.mkdir(exist_ok=True)
        self.cache_folder.joinpath(".default").write_text(name)

    def available(self) -> List[str]:
        return sorted(self.installed)

    def get(self, token_listname: Optional[str] = None) -> NftSet:
        if not token_listname:
            if not self.default:
                raise ValueError("Default token list has not been set.")

            token_listname = self.default

        if token_listname not in self.installed:
            raise ValueError(f"Unknown token list: {token_listname}")

        return self.installed[token_listname]

    def get_collections(
        self,
        nftset_name: Optional[str] = None,  # Use default
        chain_id: ChainId = 1,  # Ethereum Mainnnet
    ) -> Iterator[CollectionInfo]:
        nftset = self.get(nftset_name)
        return filter(lambda t: t.chain_id == chain_id, nftset.collections)

    def get_collection_info(
        self,
        symbol: Symbol,
        nftset_name: Optional[str] = None,  # Use default
        chain_id: ChainId = 1,  # Ethereum Mainnnet
        case_insensitive: bool = False,
    ) -> CollectionInfo:
        nftset = self.get(nftset_name)
        collection_iter = self.get_collections(nftset_name, chain_id)
        collection_iter = (
            filter(lambda t: t.symbol == symbol, collection_iter)
            if case_insensitive
            else filter(lambda t: t.symbol.lower() == symbol.lower(), collection_iter)
        )

        matching_tokens = list(collection_iter)
        if len(matching_tokens) == 0:
            raise ValueError(
                f"Collection with symbol '{symbol}' does not exist" f" within '{nftset}' Set."
            )

        elif len(matching_tokens) > 1:
            raise ValueError(
                f"Multiple collectionss with symbol '{symbol}'" f" found in '{nftset}' Set."
            )

        else:
            return matching_tokens[0]
