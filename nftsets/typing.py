from datetime import datetime as Timestamp
from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import AnyUrl
from pydantic import BaseModel as _BaseModel

ChainId = int
Address = str

Name = str
Symbol = str

TokenId = int


class BaseModel(_BaseModel):
    def dict(self, *args, **kwargs):
        if "exclude_unset" not in kwargs:
            kwargs["exclude_unset"] = True

        return super().dict(*args, **kwargs)

    class Config:
        froze = True


class DisplayType(Enum):
    # NOTE: If `None`, will display as a simple string
    STRING = None
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
    display_type: DisplayType = DisplayType.STRING
    value: Union[str, int, float]
    # NOTE: If `None`, will use the maximum value for this attribute over the collection
    max_value: Optional[Union[int, float]] = None


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
    total_supply: Optional[int] = None

    # NOTE: Must be either a URI w/ `{uri}/{tokenId}` that points to `Metadata` objects
    #       or a pre-indexed mapping of `{tokenId: URI}` that points to `Metadata` objects
    #       or a pre-indexed mapping of `{tokenId: Metadata}`
    #       or if `None`, may be able to be fetched via `ERC721(address).tokenURI(tokenId) -> URI`
    # NOTE: If pre-indexed mapping, it may not be complete and may require further indexing
    # NOTE: Any URIs must point to content which is publicly available
    metadata: Optional[Union[AnyUrl, Dict[TokenId, Union[AnyUrl, Metadata]]]] = None


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
