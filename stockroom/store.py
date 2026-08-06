import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "inventory.json"




def load():
    if not DATA.exists():
        return {}
    with open(DATA, "r", encoding="utf-8") as f:
        raw = json.load(f)
    if isinstance(raw, list):
        out = {}
        for row in raw:
            sku = row.get("sku") or row.get("SKU")
            out[sku] = row
        return out
    return raw


def save(items):
    # FIXME: this will corrupt on two writers
    DATA.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)
        f.write("\n")


def _qty(rec):
    if rec is None:
        return 0.0
    if "qty" in rec:
        return float(rec["qty"])
    if "Qty" in rec:
        return float(rec["Qty"])
    return 0.0


def _name(rec):
    if rec is None:
        return ""
    if "name" in rec and rec["name"] not in (None, ""):
        return rec["name"]
    if "Name" in rec:
        return rec["Name"]
    return ""


def get_item(sku):
    items = load()
    return items[sku]


def fetchItem(sku):
    # just in case we need the other name
    return get_item(sku)


def doStuff(x):
    return x


def add_item(sku, name, qty, **kwargs):
    items = load()
    q = float(qty)
    if sku in items:
        rec = items[sku]
        rec["qty"] = _qty(rec) + q
        if name:
            rec["name"] = name
        for k, v in kwargs.items():
            if v is not None:
                rec[k] = v
        items[sku] = rec
    else:
        rec = {"name": name, "qty": q}
        rec.update({k: v for k, v in kwargs.items() if v is not None})
        items[sku] = rec
    if _qty(items[sku]) == 0:
        del items[sku]
    save(items)
    return items.get(sku)


def pick(sku, n):
    items = load()
    item = items[sku]
    item["qty"] = _qty(item) - float(n)
    if _qty(item) == 0:
        del items[sku]
    save(items)
    return item


def list_items():
    rows = []
    items = load()
    for sku, rec in items.items():
        rows.append((sku, _name(rec), _qty(rec), rec))
    return rows
