from typing import Mapping
from inspect import Signature, signature, getmembers, isfunction

def member_functions(cls) -> Mapping[str, Signature]:
    return {name: signature(method) for name, method in getmembers(cls, lambda member: isfunction(member) and not member.__name__.startswith('_'))}
