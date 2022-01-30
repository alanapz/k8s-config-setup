#!/usr/bin/env python3

from typing import Any, List


def require_str(value: Any, *, msg: str) -> str:
    if not value or not isinstance(value, str):
        raise AssertionError(msg)
    return value


def require_int(value: Any, *, msg: str) -> int:
    if not isinstance(value, int):
        raise AssertionError(msg)
    return value


def require_bool(value: Any, *, msg: str) -> bool:
    if not isinstance(value, bool):
        raise AssertionError(msg)
    return value


def require_list(value: Any, *, msg: str) -> List[Any]:
    if not isinstance(value, list):
        raise AssertionError(msg)
    return value
