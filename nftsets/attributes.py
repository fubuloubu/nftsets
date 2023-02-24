from typing import Dict, List, Tuple

from .typing import Attribute, AttributeValue, CollectionInfo, Name, TokenId


def attribute_rarity(
    collection: CollectionInfo, skip_traits: List[str] = None  # type: ignore[assignment]
) -> Dict[Name, Dict[AttributeValue, int]]:
    rarity: Dict[Name, Dict[AttributeValue, int]] = {}
    for token_id, metadata in collection.metadata.items():
        for attribute in metadata.attributes:
            if skip_traits and attribute.trait_type in skip_traits:
                continue

            if attribute.trait_type:
                if attribute.trait_type in rarity:
                    if attribute.value in rarity[attribute.trait_type]:
                        rarity[attribute.trait_type][attribute.value] += 1

                    else:
                        rarity[attribute.trait_type][attribute.value] = 1

                else:
                    rarity[attribute.trait_type] = {attribute.value: 1}

    return rarity


def get_rarest_attribute(
    collection: CollectionInfo, token_id: TokenId, **kwargs
) -> Tuple[Attribute, int]:
    rarity = attribute_rarity(collection, **kwargs)
    rarest_attribute = None
    top_rarity = collection.total_supply
    for trait_name in rarity:
        try:
            attribute = next(
                attr
                for attr in collection.metadata[token_id].attributes
                if attr.trait_type is trait_name
            )

        except StopIteration:
            continue

        attr_rarity = rarity[trait_name][attribute.value]
        if attr_rarity < top_rarity:
            top_rarity = attr_rarity
            rarest_attribute = attribute

    assert rarest_attribute, "Couldn't find the rarest attribute"
    return rarest_attribute, top_rarity
