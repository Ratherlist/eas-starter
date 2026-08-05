import argparse
import sys

from stockroom import store


def cmd_add(args):
    store.add_item(args.sku, args.name, args.qty, location=args.location)
    print("added", args.sku)


def cmd_list(args):
    rows = store.list_items()
    if not rows:
        print("(empty)")
        return
    for sku, name, qty, rec in rows:
        loc = rec.get("location") or rec.get("Location") or ""
        extra = "  " + loc if loc else ""
        print(sku + "  " + name + "  " + str(qty) + extra)


def cmd_pick(args):
    store.pick(args.sku, args.qty)
    print("picked", args.qty, "from", args.sku)


def build_parser():
    p = argparse.ArgumentParser(prog="stockroom")
    sub = p.add_subparsers(dest="cmd")
    sub.required = True

    a = sub.add_parser("add")
    a.add_argument("--sku", required=True)
    a.add_argument("--name", required=True)
    a.add_argument("--qty", type=float, required=True)
    a.add_argument("--location", default=None)
    a.set_defaults(func=cmd_add)

    l = sub.add_parser("list")
    l.set_defaults(func=cmd_list)

    k = sub.add_parser("pick")
    k.add_argument("--sku", required=True)
    k.add_argument("--qty", type=float, required=True)
    k.set_defaults(func=cmd_pick)

    return p


def main(argv=None):
    p = build_parser()
    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main(sys.argv[1:])
