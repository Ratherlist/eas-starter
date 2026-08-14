from stockroom.store import load


def test_list_has_filament():
    items = load()
    assert "FIL-PLA-WHT" in items
