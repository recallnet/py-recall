"""Type definitions for the Recall SDK."""

from typing import TypedDict, Union

from eth_typing import ChecksumAddress


class CreatedBucketResponse(TypedDict):
    """Type definition for BucketCreated event data."""

    kind: int
    bucket: ChecksumAddress


class MachineInitializedEvent(TypedDict):
    """Type definition for MachineInitialized event data."""

    kind: int
    machineAddress: ChecksumAddress


class EventLog(TypedDict):
    """Type definition for processed event logs."""

    args: Union[MachineInitializedEvent]  # Can extend with other event types as needed
    event: str
    logIndex: int
    transactionIndex: int
    transactionHash: str
    address: str
    blockHash: str
    blockNumber: int
