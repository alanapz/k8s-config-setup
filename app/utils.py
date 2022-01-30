#!/usr/bin/env python3

import hashlib
from enum import Enum
from base64io import Base64IO


class AppException(Exception):

    def __init__(self, msg: str):
        super().__init__(msg)


class ObjectType(Enum):
    FILE = 1
    DIR = 2


def sha256_sum(*, path: str) -> str:
    sha256_hash = hashlib.sha256()
    with open(path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()


def base64_decode(*, source_path: str, dest_path: str) -> None:
    with open(source_path, "rb") as encoded_source, open(dest_path, "wb") as target:
        with Base64IO(encoded_source) as source:
            for line in source:
                target.write(line)
