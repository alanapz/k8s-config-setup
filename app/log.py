#!/usr/bin/env python3

LOG_DEBUG = False


def log_debug(msg: str) -> None:
    if LOG_DEBUG:
        print(msg)


def log_info(msg: str) -> None:
    print(msg)


def log_warning(msg: str) -> None:
    print(f"WARN: {msg}")
