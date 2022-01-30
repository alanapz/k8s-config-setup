#!/usr/bin/env python3

import os.path
import shutil
import stat

from config import Config, ResolvedConfig
from log import log_info
from manifest import Manifest, ManifestItem
from utils import ObjectType, AppException, base64_decode, sha256_sum


class Processor:

    def __init__(self, *, src_directory: str, dest_directory: str):
        self.src_directory = src_directory
        self.dest_directory = dest_directory
        self.manifest = Manifest(directory=self.src_directory)
        self.config = Config(directory=self.src_directory)

    def process(self) -> None:

        if not os.path.isdir(self.src_directory):
            raise AppException(f"Source directory not found: '{self.src_directory}'")
        if not os.path.isdir(self.dest_directory):
            raise AppException(f"Destination directory not found: '{self.dest_directory}'")

        for item in self.manifest.items:
            self._process_item(item=item)

    def _process_item(self, item: ManifestItem) -> None:
        source_path = f"{self.src_directory}/{item.name}"
        dest_path = f"{self.dest_directory}/{item.path}"

        if not os.path.isfile(source_path):
            raise AppException(f"Source file found: '{source_path}'")

        resolved_config = self.config.resolve_config(path=item.path, object_type=ObjectType.FILE)

        if os.path.isfile(dest_path) and not resolved_config.overwrite:
            raise AppException(f"Destination file exists: '{dest_path}' (and overwrite disabled)")

        self._mkdir_if_necessary(dirname=os.path.dirname(item.path))

        if not item.base64:
            log_info(f"Copying '{source_path}' -> '{dest_path}'")
            shutil.copy(source_path, dest_path)
        else:
            log_info(f"Extracting and Base64 decoding '{source_path}' -> '{dest_path}'")
            base64_decode(source_path=source_path, dest_path=dest_path)

        self._update_stat_if_necessary(path=dest_path, resolved_config=resolved_config)

        # We only check checksum for base64-encoded files due to Kubernetes stripping YAML characters that I haven't been able
        if item.base64:
            sha256 = sha256_sum(path=dest_path)
            if sha256 != item.sha256:
                raise AppException(f"Checksum mismatch for file: '{dest_path}' (expected: '{item.sha256}', actual: '{sha256}')")

    def _mkdir_if_necessary(self, dirname: str) -> None:
        if dirname == "":
            return
        path = f"{self.dest_directory}/{dirname}"
        if not os.path.isdir(path):
            self._mkdir_if_necessary(os.path.dirname(dirname))
        resolved_config = self.config.resolve_config(path=path, object_type=ObjectType.DIR)
        if not os.path.isdir(path):
            log_info(f"mkdir '{path}', mode: {oct(resolved_config.mode)}")
            os.mkdir(path=path, mode=resolved_config.mode)
        self._update_stat_if_necessary(path=path, resolved_config=resolved_config)

    def _update_stat_if_necessary(self, path: str, resolved_config: ResolvedConfig) -> None:
        result = os.stat(path=path)
        if result.st_uid != resolved_config.uid or result.st_gid != resolved_config.gid:
            log_info(f"chown '{path}', uid: {resolved_config.uid}, gid: {resolved_config.gid}")
            os.chown(path=path, uid=resolved_config.uid, gid=resolved_config.gid)
        if stat.S_IMODE(result.st_mode) != resolved_config.mode:
            log_info(f"chmod '{path}', mode: {oct(resolved_config.mode)}")
            os.chmod(path=path, mode=resolved_config.mode)
