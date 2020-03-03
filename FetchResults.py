import argparse
import json
from os import getcwd, chdir
from re import match
from subprocess import check_call, DEVNULL
from typing import List

import certifi
import urllib3


def is_url(text: str) -> bool:
    return bool(
        match(
            r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.["
            r"a-zA-Z0-9("
            r")]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&/=]*)",
            text,
        )
    )


def format_query(args: argparse.Namespace) -> str:
    arg_dict = dict(vars(args))
    url = "https://api.github.com/search/repositories"
    # GitHub API expects multi-word queries to be joined together with the + symbol
    qlist = arg_dict.pop("query")
    qstring = qlist.pop(0)
    for word in qlist:
        qstring += f"+{word}"
    # it also expects language to be part of the query string, so merging those
    # attributes here
    if arg_dict["lang"] is not None:
        # subscripting because a list is returned, even though its always one item long
        lang_str = arg_dict.pop("lang")[0].replace(" ", "+")
        qstring += f"+language:{lang_str}"
    url += f"?q={qstring}"
    # Finally, deal with any other arguments
    for k, v in arg_dict.items():
        if v is not None:
            url += f"&{k}={v}"
    return url


def _send_request(url: str) -> List[dict]:
    http = urllib3.PoolManager(
        headers={"User-Agent": "Keating950/Gitsearch"},
        cert_reqs='CERT_REQUIRED',
        ca_certs=certifi.where()
    )
    resp = http.request("GET", url)
    return json.loads(resp.data.decode("utf-8"))["items"]


def search(args: argparse.Namespace) -> List[dict]:
    url = format_query(args)
    results = _send_request(url)
    return results


def clone_repo(path: str, url: str) -> None:
    og_cwd = getcwd()
    chdir(path)
    check_call(
        ["git", "clone", url], stdout=DEVNULL, stderr=DEVNULL,
    )
    chdir(og_cwd)
