from nats.js.kv import KeyValue
from typing import Final, Callable, NoReturn, TypeVar, Generic, Type, Any, get_type_hints
from .com import encode, decode


T = TypeVar('T')

class Field(Generic[T]):
    def __init__(self, kv: KeyValue, entry: KeyValue.Entry):
        self.__kv: Final[KeyValue] = kv
        self.__key: str = entry.key
        self.__value: T = decode(entry.value)
        self.__revision: int = entry.revision

    @property
    def cached_value(self) -> T:
        return self.__value

    async def get_latest(self) -> T:
        await self.update()
        return self.__value

    async def update(self)-> None:
        self.__value = decode(await self.__kv.get(self.__key))

    async def overwrite(self, value: T) -> None:
        self.__revision, self.__value = await self.__kv.put(self.__key, encode(value)), value

    async def reduce(self, reducer: Callable[[T], T]) -> T:
        while True:
            value: T = reducer(self.__value)
            revision: int = await self.__kv.update(self.__key, encode(value), self.__revision)
            if revision == self.__revision + 1:
                self.__revision, self.__value = revision, value
                break
            self.update()
        return self.__value


BookkeptT = TypeVar('BookkeptT', bound='Bookkept')


class Bookkept:
    def __init__(self, kv: KeyValue, **entries: KeyValue.Entry):
        object.__setattr__(self, '_kv', kv)
        for key, entry in entries.items():
            object.__setattr__(self, key, Field(self._kv, entry))

    def __setattr__(self, attr: str, value: Any) -> NoReturn:
        raise RuntimeError()

    def __delattr__(self, attr: str) -> NoReturn:
        raise RuntimeError()

    @classmethod
    async def load(cls: Type[BookkeptT], kv: KeyValue) -> BookkeptT:
        return cls(kv, **{key: await kv.get(key) for key, type_ in get_type_hints(cls._cls).items()})


def kvdataclass(cls: Type[T]) -> Type[T]:
    return type(cls.__name__, (Bookkept,), { '_cls': cls })
