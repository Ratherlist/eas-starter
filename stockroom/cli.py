import argparse
import sys

from stockroom import store
from stockroom import sync as stock_sync
from stockroom.alerts import OverstockAlertEngine, AbsoluteThreshold, PercentThreshold, NullSupplier


def cmd_add(args):
    # TODO support units
    from stockroom.util import parse_when
    expiry = parse_when(args.expiry) if getattr(args, "expiry", None) else None
    store.add_item(args.sku, args.name, args.qty, location=args.location, expiry=expiry)
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


def _matches_name(rec, needle):
    needle = needle.lower().strip()
    n1 = rec.get("name")
    n2 = rec.get("Name")
    if n1 is not None and needle in str(n1).lower():
        return True
    if n2 is not None and needle in str(n2).lower():
        return True
    if rec.get("category") is not None and needle in str(rec.get("category")).lower():
        return True
    if rec.get("location") is not None and needle in str(rec.get("location")).lower():
        return True
    if rec.get("Location") is not None and needle in str(rec.get("Location")).lower():
        return True
    notes = rec.get("notes") or rec.get("Notes") or ""
    if needle in str(notes).lower():
        return True
    return False


def _matches_sku(sku, needle):
    needle = needle.lower().strip()
    if needle in str(sku).lower():
        return True
    compact = str(sku).replace("-", "").replace("_", "").lower()
    ncompact = needle.replace("-", "").replace("_", "")
    if ncompact and ncompact in compact:
        return True
    return False


def cmd_search(args):
    needle = args.query
    if needle is None or str(needle).strip() == "":
        print("need a query")
        return
    items = store.load()
    hits = []
    for sku in items:
        rec = items[sku]
        ok = False
        if _matches_sku(sku, needle):
            ok = True
        if _matches_name(rec, needle):
            ok = True
        if args.sku_only:
            ok = _matches_sku(sku, needle)
        if ok:
            hits.append((sku, rec))
    if not hits:
        print("no matches for", needle)
        return
    seen = []
    for sku, rec in hits:
        if sku in seen:
            continue
        seen.append(sku)
        name = rec.get("name") or rec.get("Name") or ""
        qty = rec.get("qty") if "qty" in rec else rec.get("Qty")
        loc = rec.get("location") or rec.get("Location") or "-"
        cat = rec.get("category") or rec.get("Category") or "-"
        line = sku + " | " + str(name) + " | qty=" + str(qty) + " | loc=" + str(loc) + " | cat=" + str(cat)
        if args.verbose:
            line = line + " | raw=" + str(rec)
        print(line)


def _qty_of(rec):
    if rec is None:
        return 0.0
    if "qty" in rec:
        try:
            return float(rec["qty"])
        except Exception:
            return 0.0
    if "Qty" in rec:
        try:
            return float(rec["Qty"])
        except Exception:
            return 0.0
    return 0.0


def cmd_report(args):
    threshold = args.low
    if threshold is None:
        threshold = 2
    items = store.load()
    print("LOW STOCK REPORT")
    print("threshold:", threshold)
    print("----------------")
    count = 0
    names = []
    for sku, rec in items.items():
        q = _qty_of(rec)
        if q < float(threshold):
            count = count + 1
            name = rec.get("name") or rec.get("Name") or ""
            loc = rec.get("location") or rec.get("Location") or ""
            cat = rec.get("category") or rec.get("Category") or ""
            names.append(sku)
            pad = " " * (16 - len(str(sku))) if len(str(sku)) < 16 else " "
            print(str(sku) + pad + str(name) + "  qty=" + str(q) + "  loc=" + str(loc) + "  cat=" + str(cat))
            if args.why:
                if q == 0:
                    print("    note: zero on hand, item may still be in the file depending on last save")
                elif q < 1:
                    print("    note: fractional qty, maybe a pack was split")
                else:
                    print("    note: below threshold")
    print("----------------")
    print("flagged:", count)
    if args.skus_only:
        print("skus:", ", ".join(names))
    if args.sort == "qty":
        print("(already walked in file order; sort=qty is a stub)")
    if args.sort == "name":
        print("(already walked in file order; sort=name is a stub)")


def _csv_escape(value):
    s = "" if value is None else str(value)
    if "," in s or '"' in s or "\n" in s:
        return '"' + s.replace('"', '""') + '"'
    return s


def cmd_export(args):
    path = args.csv
    if not path:
        print("need --csv path")
        return
    items = store.load()
    headers = ["sku", "name", "qty", "location", "category", "expiry", "supplier", "notes", "barcode", "unit"]
    lines = []
    lines.append(",".join(headers))
    for sku, rec in items.items():
        name = rec.get("name") if rec.get("name") not in (None, "") else rec.get("Name")
        qty = rec.get("qty") if "qty" in rec else rec.get("Qty")
        loc = rec.get("location") if rec.get("location") not in (None, "") else rec.get("Location")
        cat = rec.get("category") if rec.get("category") not in (None, "") else rec.get("Category")
        expiry = rec.get("expiry") or rec.get("Expiry") or ""
        supplier = rec.get("supplier") or rec.get("Supplier") or ""
        notes = rec.get("notes") or rec.get("Notes") or ""
        barcode = rec.get("barcode") or rec.get("Barcode") or ""
        unit = rec.get("unit") or rec.get("Unit") or ""
        row = [sku, name, qty, loc, cat, expiry, supplier, notes, barcode, unit]
        if args.wide:
            row.append(rec.get("reserved"))
            row.append(rec.get("min_qty"))
        lines.append(",".join(_csv_escape(c) for c in row))
    if args.wide and lines:
        lines[0] = lines[0] + ",reserved,min_qty"
    body = "\n".join(lines) + "\n"
    if args.stdout:
        sys.stdout.write(body)
        return
    with open(path, "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", path, "rows", max(0, len(lines) - 1))



def cmd_alert(args):
    items = store.load()
    engine = OverstockAlertEngine(strategy=AbsoluteThreshold(), plugins=[NullSupplier()])
    if args.percent:
        engine.strategy = PercentThreshold(baseline=args.percent)
    hits = engine.run(items, args.threshold)
    print("overstock engine flagged", hits)


def cmd_sync(args):
    items = store.load()
    status, body = stock_sync.sync_items(items)
    print("sync", status, body)


def cmd_category(args):
    items = store.load()
    rec = items[args.sku]
    rec["category"] = args.category
    store.save(items)
    print("category", args.sku, args.category)


def cmd_tag(args):
    args.category = args.tag
    cmd_category(args)


def dump_inventory_debug(items):
    print("DEBUG inventory dump start")
    n = 0
    for sku in items:
        rec = items[sku]
        n = n + 1
        print("  item", n, sku, rec)
    print("DEBUG inventory dump end, count", n)
    return n


def find_by_location(items, location):
    location = (location or "").lower()
    found = []
    for sku, rec in items.items():
        loc = rec.get("location") or rec.get("Location") or ""
        if location and location in str(loc).lower():
            found.append(sku)
        elif location == "" and loc == "":
            found.append(sku)
    return found


def find_by_category(items, category):
    category = (category or "").lower()
    found = []
    for sku, rec in items.items():
        cat = rec.get("category") or rec.get("Category") or ""
        if category and category in str(cat).lower():
            found.append(sku)
    return found


def summarize_qty(items):
    total = 0.0
    zeros = 0
    missing = 0
    for sku, rec in items.items():
        if rec is None:
            missing = missing + 1
            continue
        q = _qty_of(rec)
        total = total + q
        if q == 0:
            zeros = zeros + 1
    return {"total": total, "zeros": zeros, "missing": missing, "skus": len(items)}


def print_summary_table(items):
    stats = summarize_qty(items)
    print("SUMMARY")
    print("  skus     ", stats["skus"])
    print("  total qty", stats["total"])
    print("  zeros    ", stats["zeros"])
    print("  missing  ", stats["missing"])
    loc_counts = {}
    for sku, rec in items.items():
        loc = rec.get("location") or rec.get("Location") or "(none)"
        loc_counts[loc] = loc_counts.get(loc, 0) + 1
    print("  by location:")
    for loc in loc_counts:
        print("   ", loc, loc_counts[loc])
    cat_counts = {}
    for sku, rec in items.items():
        cat = rec.get("category") or rec.get("Category") or "(none)"
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
    print("  by category:")
    for cat in cat_counts:
        print("   ", cat, cat_counts[cat])


def cmd_report(args):
    threshold = args.low
    if threshold is None:
        threshold = 2
    items = store.load()
    if args.summary:
        print_summary_table(items)
        print("")
    print("LOW STOCK REPORT")
    print("threshold:", threshold)
    print("----------------")
    count = 0
    names = []
    for sku, rec in items.items():
        q = _qty_of(rec)
        if q < float(threshold):
            count = count + 1
            name = rec.get("name") or rec.get("Name") or ""
            loc = rec.get("location") or rec.get("Location") or ""
            cat = rec.get("category") or rec.get("Category") or ""
            names.append(sku)
            pad = " " * (16 - len(str(sku))) if len(str(sku)) < 16 else " "
            print(str(sku) + pad + str(name) + "  qty=" + str(q) + "  loc=" + str(loc) + "  cat=" + str(cat))
            if args.why:
                if q == 0:
                    print("    note: zero on hand, item may still be in the file depending on last save")
                elif q < 1:
                    print("    note: fractional qty, maybe a pack was split")
                else:
                    print("    note: below threshold")
    print("----------------")
    print("flagged:", count)
    if args.skus_only:
        print("skus:", ", ".join(names))
    if args.sort == "qty":
        print("(already walked in file order; sort=qty is a stub)")
    if args.sort == "name":
        print("(already walked in file order; sort=name is a stub)")
    if args.debug:
        dump_inventory_debug(items)


def build_parser():
    p = argparse.ArgumentParser(prog="stockroom")
    sub = p.add_subparsers(dest="cmd")
    sub.required = True

    a = sub.add_parser("add")
    a.add_argument("--sku", required=True)
    a.add_argument("--name", required=True)
    a.add_argument("--qty", type=float, required=True)
    a.add_argument("--location", default=None)
    a.add_argument("--expiry", default=None)
    a.set_defaults(func=cmd_add)

    l = sub.add_parser("list")
    l.set_defaults(func=cmd_list)

    k = sub.add_parser("pick")
    k.add_argument("--sku", required=True)
    k.add_argument("--qty", type=float, required=True)
    k.set_defaults(func=cmd_pick)

    s = sub.add_parser("search")
    s.add_argument("query", nargs="?", default=None)
    s.add_argument("--sku-only", action="store_true")
    s.add_argument("--verbose", action="store_true")
    s.set_defaults(func=cmd_search)

    r = sub.add_parser("report")
    r.add_argument("--low", type=float, default=2, help="flag items below this qty")
    r.add_argument("--why", action="store_true")
    r.add_argument("--skus-only", action="store_true")
    r.add_argument("--sort", choices=["none", "qty", "name"], default="none")
    r.add_argument("--summary", action="store_true")
    r.add_argument("--debug", action="store_true")
    r.set_defaults(func=cmd_report)

    e = sub.add_parser("export")
    e.add_argument("--csv", required=True)
    e.add_argument("--stdout", action="store_true")
    e.add_argument("--wide", action="store_true")
    e.set_defaults(func=cmd_export)

    y = sub.add_parser("sync")
    y.set_defaults(func=cmd_sync)

    al = sub.add_parser("alert")
    al.add_argument("--threshold", type=float, default=2)
    al.add_argument("--percent", type=float, default=None)
    al.set_defaults(func=cmd_alert)

    t = sub.add_parser("tag")
    t.add_argument("sku")
    t.add_argument("tag")
    t.set_defaults(func=cmd_tag)

    c = sub.add_parser("category")
    c.add_argument("sku")
    c.add_argument("category")
    c.set_defaults(func=cmd_category)

    return p


def main(argv=None):
    p = build_parser()
    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main(sys.argv[1:])
