#!/usr/bin/env python3

from argparse import ArgumentParser
from hashlib import md5
from pathlib import Path
from shutil import copy2
import os


def parse_args():
    parser = ArgumentParser(description="A tool for removing duplicate files inside of all provided directories. "
                                        "Duplicates are being located by contents, not by name. "
                                        "Names are totally ignored.")
    parser.add_argument("path", nargs="+", help="Path (one or more) to the source directory.")
    parser.add_argument(
        "-d", "--destination", type=str, default=".",
        help="Path to the directory where results should be stored. Will be created if does not exist.")
    parser.add_argument(
        "--list", action="store_true", help="Just list found duplicates without applying any action.")
    parser.add_argument(
        "-p", "--file-pattern", type=str, default="*.*", help="File name pattern. Default '*.*'.")
    parser.add_argument(
        "-c", "--copy", action="store_true",
        help="Copy all files (without duplicates) to the destination directory. Same names will be overwritten.")
    return parser.parse_args()


def locate_files(paths: list[str], name_pattern: str) -> tuple[list[Path]]:
    hash_files_map: dict[bytes, list[Path]] = {}
    for path in paths:
        directory = Path(path)
        for file in directory.rglob(name_pattern):
            h = md5(file.read_bytes()).digest()
            hash_files_map[h] = hash_files_map.get(h, []) + [file]
    return tuple(hash_files_map.values())


def process_files(files_lists: tuple[list[Path]], destination: str, copy_files: bool):
    if copy_files:
        destination = Path(destination)
        destination.mkdir(parents=True, exist_ok=True)
        files_lists = [x[0] for x in files_lists]
        for f in files_lists:
            copy2(f, destination)
    else:
        for files_list in files_lists:
            for f in files_list[1:]:
                os.remove(f)


if __name__ == "__main__":
    args = parse_args()
    files = locate_files(args.path, args.file_pattern)
    if not args.list:
        process_files(files, args.destination, args.copy)
    print("Duplicates found:")
    for duplicates in [x for x in files if len(x) > 1]:
        print(", ".join(map(str, duplicates)))
