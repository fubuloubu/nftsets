from datetime import datetime as Timestamp
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Union

import requests  # type: ignore[import]
from pydantic import AnyUrl
from pydantic import BaseModel as _BaseModel
from pydantic import root_validator

ChainId = int
Address = str

Name = str
Symbol = str

TokenId = int

AttributeValue = Union[str, int, float]


class BaseModel(_BaseModel):
    def dict(self, *args, **kwargs):
        if "exclude_unset" not in kwargs:
            kwargs["exclude_unset"] = True

        return super().dict(*args, **kwargs)

    class Config:
        froze = True


class DisplayType(Enum):
    NUMBER = "number"
    BOOST_NUMBER = "boost_number"
    BOOST_PERCENTATGE = "boost_percentage"
    DATE = "date"


class Attribute(BaseModel):
    """
    Using OpenSea's Metadata Standards

    https://docs.opensea.io/docs/metadata-standards
    """

    # NOTE: If `None`, will display as a "Generic Attribute"
    trait_type: Optional[Name] = None
    # NOTE: If `None`, will display as a simple string
    display_type: Optional[DisplayType] = None
    value: AttributeValue
    # NOTE: If `None`, will use the maximum value for this attribute over the collection
    max_value: Optional[Union[int, float]] = None

    @root_validator
    def value_matches_display_type(cls, values):
        if "display_type" in values and values["display_type"]:
            if "percentage" in str(values["display_type"]):
                assert isinstance(
                    values["value"], float
                ), "Display type 'boost_percentage' must be float"

            else:
                assert isinstance(
                    values["value"], int
                ), f"Display type '{values['display_type']}' must be an int"

        return values

    @root_validator
    def value_within_max_value(cls, values):
        if "max_value" in values and values["max_value"] is not None:
            assert (
                values["value"] <= values["max_value"]
            ), f'Value {values["value"]} must be less than or equal to {values["max_value"]}'

        return values


class Metadata(BaseModel):
    name: Optional[Name] = None
    description: Optional[str] = None
    image: Optional[AnyUrl] = None
    attributes: List[Attribute] = []

    # TODO: Support other non-standard Metadata (OpenSea, Enjin, etc.)


class CollectionInfo(BaseModel):
    chain_id: ChainId
    address: Address
    name: Name
    symbol: Symbol
    collectionURI: Optional[AnyUrl] = None

    # NOTE: If `None`, collection has not been fully minted, or is unlimited in size
    #       If unlimited in size, suggestion is that `metadata` is set to `None` also
    total_supply: int

    # NOTE: Must be either a URI w/ `{uri}/{tokenId}` that points to `Metadata` objects
    #       or a pre-indexed mapping of `{tokenId: URI}` that points to `Metadata` objects
    #       or a pre-indexed mapping of `{tokenId: Metadata}`
    #       or if `None`, may be able to be fetched via `ERC721(address).tokenURI(tokenId) -> URI`
    # NOTE: If pre-indexed mapping, it may not be complete and may require further indexing
    # NOTE: Any URIs must point to content which is publicly available
    metadata: Dict[TokenId, Metadata] = {}

    @root_validator(pre=True)
    def expand_metadata(cls, data):
        raw_metadata = data["metadata"]
        if isinstance(raw_metadata, str) and "total_supply" in data and data["total_supply"]:
            raw_metadata = {
                token_id: f"{raw_metadata}/{token_id}" for token_id in range(data["total_supply"])
            }

        if isinstance(raw_metadata, dict):
            metadata = {}
            for token_id in raw_metadata:
                if isinstance(raw_metadata[token_id], str):
                    response = requests.get(raw_metadata[token_id])
                    metadata[token_id] = Metadata.parse_obj(response.json())

                else:
                    metadata[token_id] = Metadata.parse_obj(raw_metadata[token_id])

            data["metadata"] = metadata

            if "total_supply" not in data:
                data["total_supply"] = len(metadata)

        else:
            raise ValueError(f"Cannot expand metadata '{raw_metadata}'")

        return data

    def unpack_metadata_to_folder(self, folder: Path):
        if not folder.is_dir():
            folder.mkdir()

        max_digits = len(str(self.total_supply - 1))
        for token_id, metadata in self.metadata.items():
            token_id_str = str(token_id).zfill(max_digits)
            (folder / f"{token_id_str}.json").write_text(metadata.json())


class NftSet(BaseModel):
    name: Name  # NOTE: Name of the provider of the Set
    timestamp: Timestamp  # NOTE: Should use ISO timestamp to determine versioning history
    collections: List[CollectionInfo] = []
    keywords: List[str] = []
    logoURI: Optional[AnyUrl] = None  # NOTE: Logo of the Set provider

    class Config:
        # NOTE: Not frozen as we may need to dynamically modify this
        froze = False

    def dict(self, *args, **kwargs) -> dict:
        data = super().dict(*args, **kwargs)
        # NOTE: This was the easiest way to make sure this property returns isoformat
        data["timestamp"] = self.timestamp.isoformat()
        return data
