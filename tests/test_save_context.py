from pytest import mark

from ryukit import utils as ryuitls
from ryukit.app.save.__context__ import bucket, channel_save_bucket
from ryukit.libs import db, paths

__all__ = ["test_channel_save_bucket", "test_bucket"]


@mark.parametrize("id_, upstream", [(1, True), (2, True), (5, False)])
def test_channel_save_bucket(seed: object, id_: int, upstream: bool):
    channel_save_bucket(id_, upstream=upstream)
    assert ryuitls.size(
        paths.SAVE_INSTANCE_DIR.format(id=id_), sizing="dir"
    ) == ryuitls.size(
        paths.RYUJINX_DATA_DIR, sizing="dir"
    ), "Data folder sizes did not match."


@mark.parametrize("id_, valid", [(1, True), (2, True), (3, True), (99, False)])
def test_bucket(seed: object, id_: int, valid: bool):
    try:
        with bucket(id_) as (client, save):
            assert (
                client.get(db.RyujinxSave, id_) == save
            ), "Incorrect bucket returned."
    except Exception:
        assert not valid, "Failed to fetch a valid bucket."
        return
    assert valid, "Successfully fetched invalid bucket."
