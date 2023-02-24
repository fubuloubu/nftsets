from nftsets import CollectionInfo


def test_parse_collection(raw_collection_file):
    CollectionInfo.parse_file(raw_collection_file)
