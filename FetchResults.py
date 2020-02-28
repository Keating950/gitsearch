import argparse
import os
import re
import subprocess

import requests as r


def is_url(text: str) -> bool:
    return bool(
        re.match(
            r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.["
            r"a-zA-Z0-9("
            r")]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&/=]*)",
            text,
        )
    )


def format_query(args: argparse.Namespace):
    # GitHub API expects multi-word queries to be joined together with the + symbol
    qstring = f"{args.query[0]}"
    if len(args.query) > 1:
        for term in args.query[1:]:
            qstring += f"+{term}"
    # it also expects language to be part of the query string, so merging those
    # attributes here
    if args.lang is not None:
        qstring += f"+language:{args.lang}"
        delattr(args, "lang")
    args.query = qstring


def _send_request(args: argparse.Namespace) -> list:
    param_dict = {"q": args.query}
    if args.sort != None:
        param_dict["sort"] = args.sort
    if args.order != None:
        param_dict["order"] = args.order

    resp = r.get(url="https://api.github.com/search/repositories", params=param_dict)
    try:
        resp.raise_for_status()
    except r.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    return resp.json()["items"]


def search(args: argparse.Namespace) -> list:
    format_query(args)
    results = _send_request(args)
    return results


def clone_repo(path: str, url: str) -> None:
    og_cwd = os.getcwd()
    os.chdir(path)
    subprocess.check_call(
        ["git", "clone", url], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL
    )
    os.chdir(og_cwd)
