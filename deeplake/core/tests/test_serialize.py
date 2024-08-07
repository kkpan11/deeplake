import pytest

from deeplake.constants import ENCODING_DTYPE
from deeplake.core.serialize import (
    serialize_chunk,
    deserialize_chunk,
    serialize_chunkids,
    deserialize_chunkids,
)
import numpy as np
import deeplake
import time


def test_chunk_serialize():
    version = deeplake.__version__
    shape_info = np.cast[deeplake.constants.ENCODING_DTYPE](
        np.random.randint(100, size=(17, 63))
    )
    byte_positions = np.cast[deeplake.constants.ENCODING_DTYPE](
        np.random.randint(100, size=(31, 3))
    )
    data = [b"x" * 8 * 1024 * 1024] * 2  # 16 MB chunk
    encoded = bytes(serialize_chunk(version, shape_info, byte_positions, data))

    # Deserialize
    start = time.time()
    for _ in range(10000):
        decoded = deserialize_chunk(encoded)
    end = time.time()

    assert end - start < 0.5

    version2, shape_info2, byte_positions2, data2 = decoded
    assert version2 == version
    np.testing.assert_array_equal(shape_info, shape_info2)
    np.testing.assert_array_equal(byte_positions, byte_positions2)
    assert b"".join(data) == bytes(data2)


def test_chunkids_serialize():
    version = deeplake.__version__
    arr = np.cast[ENCODING_DTYPE](np.random.randint(100, size=(100, 2)))
    encoded = serialize_chunkids(version, arr)
    decoded = deserialize_chunkids(encoded)
    version2, ids, dtype = decoded
    assert version2 == version
    np.testing.assert_array_equal(arr, ids)


@pytest.mark.slow
@pytest.mark.flaky
def test_get_large_header(hub_cloud_dev_token):
    # headers for videos in this dataset are larger than the 100 bytes originally fetched
    # ideally this test would just be calling `serialize.get_header_from_url` directly, but that requires all the URL buliding up logic that lives in the chunk engine.
    # So calling a larger codepath that includes `get_header_from_url`
    ds = deeplake.load("hub://activeloop/hmdb51-train", token=hub_cloud_dev_token)
    assert ds.videos[0].shape == (75, 240, 560, 3)
