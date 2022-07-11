ProductId = NewType('ProductId', str)


@enum
class Field:
    BID0 = auto()
    ASK0 = auto()

@enum
class Status:
    OPEN = auto()
    CLOSED = auto()


#
# TREP

TrepServiceId = NewType('TrepServiceId', str)
TrepRic = NewType('TrepRic', str)

@dataclass
class FormClass:
    fields: Mapping[Field, str]

@dataclass
class TrepFeed:
    formclass: FormClass

@dataclass
class TrepInfo:
    rics: Mapping[ProductId, Mapping[TrepServiceId, TrepRic]]
    services: Mapping[TrepServiceId, TrepFeed]

class TrepConfig:
    def get_service(id: TrepServiceId) -> TrepFeed:
        pass

def get_trep_info(products: Collection[ProductId]) -> TrepInfo:
    pass


#
# LQ2

@enum
class LQ2Region:
    EU = auto()
    US = auto()

Address = NewType('Address', str)
LQ2FeedName = NewType('LQ2FeedName', str)
LQ2InstrumentId = NewType('LQ2InstrumentId', int)

@dataclass
class LQ2Feed:
    snapshots: Address
    updates: Address
    region: LQ2Region

@dataclass
class TrepInfo:
    instruments: Mapping[ProductId, Mapping[LQ2FeedName, LQ2InstrumentId]]
    services: Mapping[LQ2FeedName, LQ2Feed]
