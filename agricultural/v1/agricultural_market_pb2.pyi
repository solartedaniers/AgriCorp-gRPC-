from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PriceTrend(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PRICE_TREND_UNSPECIFIED: _ClassVar[PriceTrend]
    PRICE_TREND_UP: _ClassVar[PriceTrend]
    PRICE_TREND_DOWN: _ClassVar[PriceTrend]
    PRICE_TREND_STABLE: _ClassVar[PriceTrend]
PRICE_TREND_UNSPECIFIED: PriceTrend
PRICE_TREND_UP: PriceTrend
PRICE_TREND_DOWN: PriceTrend
PRICE_TREND_STABLE: PriceTrend

class Product(_message.Message):
    __slots__ = ("product_id", "name", "unit", "origin_region")
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    UNIT_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_REGION_FIELD_NUMBER: _ClassVar[int]
    product_id: str
    name: str
    unit: str
    origin_region: str
    def __init__(self, product_id: _Optional[str] = ..., name: _Optional[str] = ..., unit: _Optional[str] = ..., origin_region: _Optional[str] = ...) -> None: ...

class ListProductsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListProductsResponse(_message.Message):
    __slots__ = ("products",)
    PRODUCTS_FIELD_NUMBER: _ClassVar[int]
    products: _containers.RepeatedCompositeFieldContainer[Product]
    def __init__(self, products: _Optional[_Iterable[_Union[Product, _Mapping]]] = ...) -> None: ...

class PriceRequest(_message.Message):
    __slots__ = ("product_id",)
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    product_id: str
    def __init__(self, product_id: _Optional[str] = ...) -> None: ...

class PriceResponse(_message.Message):
    __slots__ = ("product_id", "current_price", "currency", "timestamp", "previous_price", "change_percent", "trend", "product")
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    CURRENT_PRICE_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    PREVIOUS_PRICE_FIELD_NUMBER: _ClassVar[int]
    CHANGE_PERCENT_FIELD_NUMBER: _ClassVar[int]
    TREND_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_FIELD_NUMBER: _ClassVar[int]
    product_id: str
    current_price: float
    currency: str
    timestamp: int
    previous_price: float
    change_percent: float
    trend: PriceTrend
    product: Product
    def __init__(self, product_id: _Optional[str] = ..., current_price: _Optional[float] = ..., currency: _Optional[str] = ..., timestamp: _Optional[int] = ..., previous_price: _Optional[float] = ..., change_percent: _Optional[float] = ..., trend: _Optional[_Union[PriceTrend, str]] = ..., product: _Optional[_Union[Product, _Mapping]] = ...) -> None: ...

class TelemetryData(_message.Message):
    __slots__ = ("station_id", "temperature", "humidity", "weight_kg", "timestamp", "product_id")
    STATION_ID_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    HUMIDITY_FIELD_NUMBER: _ClassVar[int]
    WEIGHT_KG_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    station_id: str
    temperature: float
    humidity: float
    weight_kg: float
    timestamp: int
    product_id: str
    def __init__(self, station_id: _Optional[str] = ..., temperature: _Optional[float] = ..., humidity: _Optional[float] = ..., weight_kg: _Optional[float] = ..., timestamp: _Optional[int] = ..., product_id: _Optional[str] = ...) -> None: ...

class TelemetrySummary(_message.Message):
    __slots__ = ("processed_records", "success", "message", "avg_temperature", "min_temperature", "max_temperature", "avg_humidity", "total_weight_kg", "alert_count", "station_count", "server_processing_ms", "received_bytes")
    PROCESSED_RECORDS_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    AVG_TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    MIN_TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    MAX_TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    AVG_HUMIDITY_FIELD_NUMBER: _ClassVar[int]
    TOTAL_WEIGHT_KG_FIELD_NUMBER: _ClassVar[int]
    ALERT_COUNT_FIELD_NUMBER: _ClassVar[int]
    STATION_COUNT_FIELD_NUMBER: _ClassVar[int]
    SERVER_PROCESSING_MS_FIELD_NUMBER: _ClassVar[int]
    RECEIVED_BYTES_FIELD_NUMBER: _ClassVar[int]
    processed_records: int
    success: bool
    message: str
    avg_temperature: float
    min_temperature: float
    max_temperature: float
    avg_humidity: float
    total_weight_kg: float
    alert_count: int
    station_count: int
    server_processing_ms: float
    received_bytes: int
    def __init__(self, processed_records: _Optional[int] = ..., success: bool = ..., message: _Optional[str] = ..., avg_temperature: _Optional[float] = ..., min_temperature: _Optional[float] = ..., max_temperature: _Optional[float] = ..., avg_humidity: _Optional[float] = ..., total_weight_kg: _Optional[float] = ..., alert_count: _Optional[int] = ..., station_count: _Optional[int] = ..., server_processing_ms: _Optional[float] = ..., received_bytes: _Optional[int] = ...) -> None: ...
