import re

from recall_sdk import LOCALNET_CHAIN_ID, Client
from recall_sdk.exceptions import UnexpectedError

client = Client(
    private_key="0x7c852118294e51e653712a81e05800f419141751be58f605c371e15141b007a6",
    chain_id=LOCALNET_CHAIN_ID,
)
signer_address = client.get_signer_address()


def test_create_bucket():
    data = client.create_bucket()
    if data is None:
        raise UnexpectedError(UnexpectedError.BUCKET_CREATION_FAILED)
    assert data["kind"] == 0
    assert re.match(r"^0x[a-fA-F0-9]{40}$", data["bucket"])


def test_list_buckets():
    buckets = client.list_buckets()
    assert len(buckets) > 0


# TODO: object tests are hardcoded values, matching objects created via the CLI
def test_get_object_state():
    bucket = "0xff0000000000000000000000000000000000008f"
    key = "hello/world"
    state = client.get_object_state(bucket, key)
    assert len(state) == 5  # Includes: blob hash, recovery hash, size, expiry, metadata


def test_get_object():
    bucket = "0xff0000000000000000000000000000000000008f"
    key = "hello/world"
    data = client.get_object(bucket, key)
    assert data == b"hello\n"
