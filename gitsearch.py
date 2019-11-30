import argparse
import requests as r


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", metavar="query string", type=str, nargs=1,
                        help="A quoted query string")
    parser.add_argument("--sort", metavar="sort by", type=str, nargs=1,
                        help="sort by stars, forks, help-wanted-issues, or updated."
                             "Default is best match.")
    parser.add_argument("--order", metavar="order", type=str, nargs=1, default="desc",
                        help="asc or desc. Default is descending")
    parser.add_argument("--lang", metavar="lang", type=str, nargs=1,
                        help="Restrict results by language.")
    namespace_obj = parser.parse_args()
    namespace_obj.query = str(namespace_obj.query[0]).split()
    return namespace_obj


def format_query(args):
    qstring = ""
    if type(args.query) == list:
        qstring += f"{args.query[0]}"
        for term in args.query[1:]:
            qstring += f"+{term}"
    else:
        qstring = args.query
    if args.lang is not None:
        qstring += f"+language:{args.lang}"
        delattr(args, "lang")
    args.query = qstring


def send_request(args):
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


def pretty_print(results):
    BOLD = '\033[1m'
    END = '\033[0m'
    for repo in results:
        line1 = f"{repo['name']}    {repo['owner']['login']}    {repo['language']}    " \
                f"☆{repo['stargazers_count']}"
        if len(repo['description']) > 80:
            line2 = repo['description'][0:77] + "..."
        else:
            line2 = repo['description']
        line3 = repo['url']

        print(BOLD + line1 + END)
        print(line2)
        print(line3)
        print("\n")


if __name__ == "__main__":
    args = parse_args()
    format_query(args)
    results = send_request(args)
    pretty_print(results)
