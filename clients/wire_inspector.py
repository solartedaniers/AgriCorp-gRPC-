import json
from dataclasses import dataclass
from typing import Iterable

from google.protobuf import json_format
from google.protobuf.message import Message


@dataclass(frozen=True)
class WireFootprint:
    protobuf_bytes: int
    json_bytes: int

    @property
    def saving_percent(self) -> float:
        if self.json_bytes == 0:
            return 0.0
        return (1 - self.protobuf_bytes / self.json_bytes) * 100

    @property
    def ratio(self) -> float:
        return self.json_bytes / self.protobuf_bytes if self.protobuf_bytes else 0.0

    def __add__(self, other: "WireFootprint") -> "WireFootprint":
        return WireFootprint(self.protobuf_bytes + other.protobuf_bytes, self.json_bytes + other.json_bytes)


class WireInspector:
    def measure(self, message: Message) -> WireFootprint:
        as_dict = json_format.MessageToDict(
            message,
            preserving_proto_field_name=False,
            always_print_fields_with_no_presence=True,
        )
        json_payload = json.dumps(as_dict, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        return WireFootprint(protobuf_bytes=message.ByteSize(), json_bytes=len(json_payload))

    def measure_many(self, messages: Iterable[Message]) -> WireFootprint:
        total = WireFootprint(0, 0)
        for message in messages:
            total = total + self.measure(message)
        return total

    def to_json(self, message: Message) -> str:
        return json_format.MessageToJson(message, always_print_fields_with_no_presence=True, ensure_ascii=False)
