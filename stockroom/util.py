import re

_ISO = re.compile(r"^(\d{4})-(\d{1,2})-(\d{1,2})$")
_US = re.compile(r"^(\d{1,2})/(\d{1,2})/(\d{2,4})$")
_COMPACT = re.compile(r"^(\d{4})(\d{2})(\d{2})$")


def parse_when(s):
    if s is None:
        return None
    s = str(s).strip()
    if not s:
        return None
    m = _ISO.match(s)
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return "%04d-%02d-%02d" % (y, mo, d)
    m = _US.match(s)
    if m:
        mo, d, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if y < 100:
            y = 2000 + y
        return "%04d-%02d-%02d" % (y, mo, d)
    m = _COMPACT.match(s)
    if m:
        return "%s-%s-%s" % (m.group(1), m.group(2), m.group(3))
    if "T" in s:
        return parse_when(s.split("T", 1)[0])
    bits = s.replace(".", "-").replace(" ", "-").split("-")
    if len(bits) == 3 and all(bits):
        try:
            y, mo, d = int(bits[0]), int(bits[1]), int(bits[2])
            if y < 100:
                y = 2000 + y
            return "%04d-%02d-%02d" % (y, mo, d)
        except Exception:
            return s
    return s
