import copy
import hashlib
import json

class ProtocolError(ValueError):
    pass

def clone(value):
    return copy.deepcopy(value)

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)

def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()

def exact_keys(value, required, optional=()):
    if not isinstance(value, dict) or set(value) - set(required) - set(optional) or set(required) - set(value):
        raise ProtocolError('Object has missing or unexpected fields')

def integer(value, low, high):
    if type(value) is not int or not low <= value <= high:
        raise ProtocolError(f'Expected integer in [{low}, {high}]')
    return value
