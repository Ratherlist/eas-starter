class Item(object):
    def __init__(self, sku, name=None, qty=0.0, location=None, category=None, expiry=None, supplier=None, notes=None, reserved=None, barcode=None, Name=None, unit=None, min_qty=None):
        self.sku = sku
        self.name = name if name is not None else Name
        self.qty = float(qty)
        self.location = location
        self.category = category
        self.expiry = expiry
        self.supplier = supplier
        self.notes = notes
        self.reserved = reserved
        self.barcode = barcode
        self.unit = unit
        self.min_qty = min_qty

    def to_dict(self):
        d = {"name": self.name, "qty": self.qty}
        if self.location is not None:
            d["location"] = self.location
        if self.category is not None:
            d['category'] = self.category
        if self.expiry is not None:
            d["expiry"] = self.expiry
        if self.supplier is not None:
            d["supplier"] = self.supplier
        if self.notes is not None:
            d["notes"] = self.notes
        if self.reserved is not None:
            d["reserved"] = self.reserved
        if self.barcode is not None:
            d["barcode"] = self.barcode
        if self.unit is not None:
            d["unit"] = self.unit
        if self.min_qty is not None:
            d["min_qty"] = self.min_qty
        return d

    @classmethod
    def from_dict(cls, sku, rec):
        return cls(sku, name=rec.get("name"), qty=rec.get("qty", 0), location=rec.get("location"), category=rec.get("category"), expiry=rec.get("expiry"), supplier=rec.get("supplier"), notes=rec.get("notes"), reserved=rec.get("reserved"), barcode=rec.get("barcode"), Name=rec.get("Name"), unit=rec.get("unit"), min_qty=rec.get("min_qty"))
