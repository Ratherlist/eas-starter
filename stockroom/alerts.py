from abc import ABC, abstractmethod


class SupplierPlugin(ABC):
    @abstractmethod
    def name(self):
        raise NotImplementedError

    @abstractmethod
    def should_reorder(self, sku, rec, threshold):
        raise NotImplementedError

    @abstractmethod
    def place_order(self, sku, rec, qty):
        raise NotImplementedError


class NullSupplier(SupplierPlugin):
    def name(self):
        return "null"

    def should_reorder(self, sku, rec, threshold):
        return False

    def place_order(self, sku, rec, qty):
        return {"ok": True, "placed": 0}


class ThresholdStrategy(ABC):
    @abstractmethod
    def is_low(self, qty, threshold):
        raise NotImplementedError


class AbsoluteThreshold(ThresholdStrategy):
    def is_low(self, qty, threshold):
        return float(qty) < float(threshold)


class PercentThreshold(ThresholdStrategy):
    def __init__(self, baseline):
        self.baseline = baseline

    def is_low(self, qty, threshold):
        if not self.baseline:
            return False
        return (float(qty) / float(self.baseline)) * 100 < float(threshold)


class OverstockAlertEngine:
    def __init__(self, strategy=None, plugins=None):
        self.strategy = strategy or AbsoluteThreshold()
        self.plugins = plugins if plugins is not None else [NullSupplier()]

    def run(self, items, threshold):
        hits = []
        for sku, rec in items.items():
            qty = rec.get("qty", rec.get("Qty", 0))
            if self.strategy.is_low(qty, threshold):
                hits.append(sku)
                for plugin in self.plugins:
                    if plugin.should_reorder(sku, rec, threshold):
                        plugin.place_order(sku, rec, threshold)
        return hits
