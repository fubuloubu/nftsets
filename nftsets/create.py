import random
from pathlib import Path
from typing import Callable, Dict, List, Sequence, Tuple, Union

from .typing import Attribute, AttributeValue, DisplayType, Metadata, Name, TokenId


def create_random_attributes(
    choices: Dict[Name, Union[Sequence[str], Tuple[int, int], Tuple[float, float]]]
) -> List[Attribute]:
    """
    Create a list of attributes with randomized values,
    according to the given choices for each attribute.
    """
    attributes: List[Attribute] = list()

    for trait_name, selection in choices.items():
        value: AttributeValue
        if isinstance(selection, tuple):
            min_value, max_value = selection
            if isinstance(min_value, int) and isinstance(max_value, int):
                value = random.randrange(min_value, max_value)

            elif isinstance(min_value, float) and isinstance(max_value, float):
                value = random.uniform(min_value, max_value)

        else:
            value = random.choice(selection)

        attribute = Attribute(trait_type=trait_name, value=value)

        if isinstance(value, (int, float)):
            attribute.max_value = max_value
            attribute.display_type = DisplayType.NUMBER

        attributes.append(attribute)

    return attributes


def compile_metadata_from_sources(
    source_files: List[Path],
    get_metadata_fn: Callable[[Path], Dict],
) -> Dict[TokenId, Metadata]:
    """
    Create a mapping of metadata objects from a specified list of source files in `tokenId` order,
    using the specified `get_attributes_fn` to extract properties and attributes from the source.
    """
    return {
        token_id: Metadata.parse_obj(metadata)
        for token_id, metadata in enumerate(map(get_metadata_fn, source_files))
    }
