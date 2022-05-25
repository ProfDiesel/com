from argparse import ArgumentParser
from dataclasses import dataclass, fields, is_dataclass
from importlib import import_module
from importlib.machinery import ModuleSpec
from importlib.util import module_from_spec, spec_from_file_location
from inspect import Signature, getmembers, isclass
from pathlib import Path
from types import ModuleType
from typing import (Any, Final, Iterable, Mapping, MutableSet, NewType,
                    Optional, Sequence, Tuple, get_args, get_origin)

from jinja2 import Environment, FileSystemLoader
from typing_inspect import is_new_type

from .utils import member_functions

Annotation = NewType('Annotation', Any)

@dataclass(frozen=True)
class Service:
    name: str
    methods: Mapping[str, Signature]
    signals: Mapping[str, Signature]


def services(module: ModuleType) -> Iterable[Service]:
    for name, cls in getmembers(module, lambda x: isclass(x) and hasattr(x, '_client_cls')):
        yield Service(name = name.removesuffix('Server'), methods = member_functions(cls), signals = member_functions(cls._client_cls) if cls._client_cls else {})

def walk(services: Iterable[Service]) -> Iterable[Annotation]:
    known = set()

    def recurse(annotation: Annotation) -> Iterable[Annotation]:
        if annotation in known:
            return
        known.add(annotation)
        if is_dataclass(annotation):
            for field in fields(annotation):
                yield from recurse(field.type)
        elif is_new_type(annotation):
            yield from recurse(annotation.__supertype__)
        elif (origin := get_origin(annotation)) == list:
            (arg,) = get_args(annotation)
            yield from recurse(arg)
        else:
            return
        yield annotation

    for service in services:
        for method in service.methods.values():
            for parameter in list(method.parameters.values())[1:]:
                yield from recurse(parameter.annotation)
            yield from recurse(method.return_annotation)
        for signal in service.methods.values():
            for parameter in list(signal.parameters.values())[1:]:
                yield from recurse(parameter.annotation)

def _load_module(module: str) -> ModuleType:
    try:
        return import_module(module)
    except (TypeError, ImportError):
        spec: Final[ModuleSpec] = spec_from_file_location(Path(module).stem, module)
        result: Final[ModuleType] = module_from_spec(spec)
        spec.loader.exec_module(result)
        return result


def _render(module: ModuleType, template: str) -> str:
    env: Final[Environment] = Environment(loader=FileSystemLoader('.'))
    env.filters.update({'camelise': lambda x: x.title().replace('_', ''),
                        'parameters': lambda x: list(x.parameters.values())[1:],
                        'fields': lambda x: fields(x),
                        'type_arg': lambda x: x.__supertype__ if is_new_type(x) else get_args(x)[0]})
    env.tests.update({'string_type': lambda x: isinstance(x, type) and issubclass(x, str),
                      'sub_type': is_new_type,
                      'array_type': lambda x: get_origin(x) == list,
                      'record_type': is_dataclass})
    return env.get_template(template).render(services=list(services(module)), **{'walk': lambda: walk(services(module))})


def main(argv: Optional[Sequence[str]] = None):
    parser: Final[ArgumentParser] = ArgumentParser()
    parser.add_argument('module')
    parser.add_argument('template')
    args = parser.parse_args(argv)
    print(_render(_load_module(args.module), args.template))

if __name__ == '__main__':
    main()
