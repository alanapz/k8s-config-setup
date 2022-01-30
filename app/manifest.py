#!/usr/bin/env python3

import os.path
from typing import List, Dict

import yaml

from log import log_info
from require import require_str, require_list, require_bool
from utils import AppException

MANIFEST_FILENAME = "__MANIFEST.yaml"


class ManifestItem:

    def __init__(self, *, name: str, path: str, sha256: str, base64: bool):
        self.name = name
        self.path = path
        self.sha256 = sha256
        self.base64 = base64

    def __repr__(self) -> str:
        return f"name={self.name},path={self.path},sha256={self.sha256},base64={self.base64}"


class Manifest:

    def __init__(self, *, directory: str):
        self._directory = directory
        self._items: List[ManifestItem] = []
        self._loaded = False

    @property
    def items(self) -> List[ManifestItem]:
        if not self._loaded:
            self._load_manifest()
            self._loaded = True
        return self._items

    def _load_manifest(self) -> None:

        manifest_filename = f"{self._directory}/{MANIFEST_FILENAME}"

        if not os.path.isfile(manifest_filename):
            raise AppException(f"Manifest file not found: '{manifest_filename}'")

        log_info(f"Reading manifest from: '{manifest_filename}'")

        with open(file=manifest_filename, mode="r") as stream:
            result: Dict[str, object] = yaml.safe_load(stream)
            for entry in require_list(result["mappings"],
                                      msg="'mappings' element not present in manifest file"):
                self._items.append(ManifestItem(
                    name=require_str(entry["name"], msg="'name' missing in mapping entry"),
                    path=require_str(entry["path"], msg="'path' missing in mapping entry"),
                    sha256=require_str(entry["sha256"], msg="'sha256' missing in mapping entry"),
                    base64=require_bool(entry["base64"],
                                        msg="'base64' is of unexpected type") if "base64" in entry else False))

        log_info(f"Loaded {len(self._items)} manifest entries")
