#!/usr/bin/env python3

import os.path
import re
from typing import List, Optional, Callable, Pattern, TypeVar, Dict

import yaml

from log import log_debug, log_info, log_warning
from require import require_bool, require_str, require_list, require_int
from utils import AppException, ObjectType

CONFIG_FILENAME = "__CONFIG.yaml"
DEFAULT_UID = 0
DEFAULT_GID = 0
DEFAULT_MODE = {ObjectType.FILE: 0o664, ObjectType.DIR: 0o775}
DEFAULT_OVERWRITE = False

T = TypeVar('T')


class ResolvedConfig:

    def __init__(self, *, uid: int, gid: int, mode: int, overwrite: bool):
        self.uid = uid
        self.gid = gid
        self.mode = mode
        self.overwrite = overwrite

    def __repr__(self) -> str:
        return f"uid={self.uid},gid={self.gid},mode={oct(self.mode)},overwrite={self.overwrite}"


class ConfigRule:

    def __init__(self, *, path: Optional[str], path_pattern: Optional[Pattern], object_type: Optional[ObjectType], uid: Optional[int], gid: Optional[int], mode: Optional[int], overwrite: Optional[bool]):
        self.path = path
        self.path_pattern = path_pattern
        self.object_type = object_type
        self.uid = uid
        self.gid = gid
        self.mode = mode
        self.overwrite = overwrite

    def __repr__(self) -> str:
        buff: Dict[str, object] = dict()
        if self.path:
            buff['path'] = self.path
        if self.path_pattern:
            buff['path_pattern'] = self.path_pattern.pattern
        if self.object_type:
            buff['object_type'] = self.object_type
        if self.uid:
            buff['uid'] = self.uid
        if self.gid:
            buff['gid'] = self.gid
        if self.mode:
            buff['mode'] = oct(self.mode)
        if self.overwrite:
            buff['overwrite'] = self.overwrite
        return str(buff)


class Config:

    def __init__(self, *, directory: str):
        self._directory = directory
        self._rules: List[ConfigRule] = []
        self._loaded = False

    def resolve_config(self, *, path: str, object_type: ObjectType) -> ResolvedConfig:
        if not self._loaded:
            self._load_config()
            self._loaded = True

        uid = self._find_matching_rule_value(path=path, object_type=object_type, predicate=lambda rule: rule.uid)
        gid = self._find_matching_rule_value(path=path, object_type=object_type, predicate=lambda rule: rule.gid)
        mode = self._find_matching_rule_value(path=path, object_type=object_type, predicate=lambda rule: rule.mode)
        overwrite = self._find_matching_rule_value(path=path, object_type=object_type, predicate=lambda rule: rule.overwrite)

        return ResolvedConfig(
            uid=uid if uid is not None else DEFAULT_UID,
            gid=gid if gid is not None else DEFAULT_GID,
            mode=mode if mode is not None else DEFAULT_MODE[object_type],
            overwrite=overwrite if overwrite is not None else DEFAULT_OVERWRITE)

    def _find_matching_rule_value(self, path: str, object_type: ObjectType, predicate: Callable[[ConfigRule], T]) -> Optional[T]:
        """Returns the last rule matching (a matching rule is one that has a non-null value returned for predicate"""

        rules_copy: List[ConfigRule] = [* self._rules]
        rules_copy.reverse()

        for rule in rules_copy:
            if rule.path is not None and rule.path != path:
                log_debug(f"Skipping rule: '{rule}' for path: '{path}', path mismatch (expected: '{rule.path}')")
                continue
            if rule.path_pattern is not None and rule.path_pattern.match(path) is None:
                log_debug(f"Skipping rule: '{rule}' for path: '{path}', regex mismatch")
                continue
            if rule.object_type is not None and rule.object_type != object_type:
                log_debug(f"Skipping rule: '{rule}' for path: '{path}', type mismatch (expected: '{rule.object_type}')")
                continue
            result = predicate(rule)
            if result is not None:
                return result

        return None

    def _load_config(self) -> None:

        config_filename = f"{self._directory}/{CONFIG_FILENAME}"

        if not os.path.isfile(config_filename):
            log_warning(f"Config file not found: '{config_filename}'")
            return

        log_info(f"Reading config from: '{config_filename}'")

        with open(file=config_filename, mode="r") as stream:
            result: Dict[str, object] = yaml.safe_load(stream)
            for rule in require_list(result["rules"], msg="'rules' is of unexpected type"):

                # Either 'path' or 'pattern' can be specified but not both
                if "path" in rule and "pattern" in rule:
                    raise AppException("Cannot specify multiple predicates for the same rule")

                self._rules.append(ConfigRule(
                    path=require_str(rule["path"], msg="'path' is of unexpected type") if "path" in rule else None,
                    path_pattern=re.compile(require_str(rule["pattern"], msg="'pattern' is of unexpected type")) if "pattern" in rule else None,
                    object_type=self._parse_object_type(rule["type"] if "type" in rule else None),
                    uid=require_int(rule["uid"], msg="'uid' is of unexpected type") if "uid" in rule else None,
                    gid=require_int(rule["gid"], msg="'gid' is of unexpected type") if "gid" in rule else None,
                    mode=require_int(rule["mode"], msg="'mode' is of unexpected type") if "mode" in rule else None,
                    overwrite=require_bool(rule["overwrite"], msg="'overwrite' is of unexpected type") if "overwrite" in rule else None))

        log_info(f"Loaded {len(self._rules)} rules")

    def _parse_object_type(self, value: str) -> Optional[ObjectType]:
        if value is None:
            return None
        if value == "file":
            return ObjectType.FILE
        if value == "dir":
            return ObjectType.DIR
        raise AppException(f"Unparseable object type: '{value}' (expected file|dir)")
