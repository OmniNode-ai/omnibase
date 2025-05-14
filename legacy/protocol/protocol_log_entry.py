from typing import Protocol


class ProtocolLogEntry(Protocol): ...


class ProtocolPromptLogEntry(ProtocolLogEntry, Protocol): ...


class ProtocolVelocityLogEntry(ProtocolLogEntry, Protocol): ...
