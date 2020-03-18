#!/usr/bin/env python

import os
import sys
from os import path
import requests
import argparse


CRYP_URL = "http://localhost:8000/crypt/"


def _err_exit(err_msg):
    print(err_msg)
    sys.exit(1)


def parse_args():
    parser = argparse.ArgumentParser(description="handle fragmax encrypted files")
    parser.add_argument("command", choices=["fetch", "upload_dir"])
    parser.add_argument("src_file")
    parser.add_argument("dest_file")

    return parser.parse_args()


def _get_file(src_file):
    r = requests.post(CRYP_URL,
                      data=dict(operation="read",
                                filepath=src_file))
    if r.status_code != 200:
        _err_exit(f"error fetching {src_file}: {r.text}")

    return r.content


def _upload_file(src_file, dest_file):
    print(f"upload {src_file} -> {dest_file}")

    with open(src_file, "rb") as f:
        r = requests.post(CRYP_URL,
                          data=dict(operation="write",
                                    filepath=dest_file),
                          files=dict(file=f))

    if r.status_code != 200:
        _err_exit(f"error uploading {src_file}: {r.text}")


def _do_fetch(src_file, dest_file):
    file_data = _get_file(src_file)

    with open(dest_file, "bw") as f:
        f.write(file_data)


def _dir_tree(top):
    for dir, _, files in os.walk(top):
        for file in files:
            yield path.join(dir, file)


def _do_upload_dir(src_dir, dest_dir):
    for file in _dir_tree(src_dir):
        dest_path = path.join(dest_dir, file)
        _upload_file(file, dest_path)


def main():
    args = parse_args()

    if args.command == "fetch":
        _do_fetch(args.src_file, args.dest_file)
    elif args.command == "upload_dir":
        _do_upload_dir(args.src_file, args.dest_file)

main()
