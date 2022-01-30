#!/usr/bin/env python3

import argparse
import os
import time

import log
from log import log_debug
from processor import Processor
from utils import AppException


def setup_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Processes config/manifest files to copy/extract files.')
    parser.add_argument('sources', metavar='SRC:DEST', nargs='+', help='source/destination directory to processs')
    parser.add_argument('--verbose', dest='verbose', action='store_true', help='verbose logging')
    parser.add_argument('--wait-for-file', metavar="FILENAME", dest='wait_for_file', action='store', help='pause until the specified file exists')
    return parser


def main() -> None:

    if os.getuid() != 0:
        raise AppException("This program must be run as root")

    params = setup_arg_parser().parse_args()
    if params.verbose:
        log.LOG_DEBUG = True
    if params.sources is None or not params.sources:
        raise AppException("Nothing to do - no sources specified")

    log_debug(f"Params: {params}")

    if params.wait_for_file:
        while not os.path.isfile(params.wait_for_file):
            log_debug(f"Waiting for wait file to exist: '{params.wait_for_file}'")
            time.sleep(5)

    for source in params.sources:
        log_debug(f"Processing source: '{source}'")
        (src_directory, dest_directory) = source.split(":")
        Processor(src_directory=src_directory, dest_directory=dest_directory).process()


if __name__ == '__main__':
    main()
