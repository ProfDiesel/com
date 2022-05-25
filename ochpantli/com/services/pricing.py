from dataclasses import dataclass
from enum import Enum, auto
from typing import Collection, Literal, NewType, Protocol, Sequence, Union

from ..types import SessionId

Indicator = Union[Literal['premium'], Literal['delta']]
ProductName = NewType('ProductName', str)


class ProductKind(Enum):
    OPTION = auto()

class Product(Protocol):
    @property
    def name(self) -> ProductName:
        pass

    @property
    def kind(self) -> ProductKind:
        pass

@dataclass
class Book:
    products: Collection[Product]

@dataclass
class PricingResult:
    book: Book
    data: Sequence[float]

    def get(product: ProductName, indicator: Indicator):
        ...

class PricingServer:
    def price(self, book: Book) -> float: ...

    def continuous_pricing(self, session: SessionId, book: Book): ...


class PricingClient:
    def new_price(self, result: PricingResult) -> None: ...
