import argparse
import requests as r


def format_query(args: argparse.Namespace):
    qstring = f"{args.query[0]}"
    if len(args.query) > 1:
        for term in args.query[1:]:
            qstring += f"+{term}"
    if args.lang is not None:
        qstring += f"+language:{args.lang}"
        delattr(args, "lang")
    args.query = qstring


def send_request(args: argparse.Namespace) -> list:
    param_dict = {"q": args.query}
    if args.sort != None:
        param_dict["sort"] = args.sort
    if args.order != None:
        param_dict["order"] = args.order

    resp = r.get(url="https://api.github.com/search/repositories",
                 params=param_dict)
    try:
        resp.raise_for_status()
    except r.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    return resp.json()["items"]


def fetch_results(args: argparse.Namespace) -> list:
    format_query(args)
    results = send_request(args)
    return results
