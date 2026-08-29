"""Numeric decodes in the style the SalPhaseIon block already uses.

The two solved z-segments were: letters a..i,o -> digits 1..9,0, read the result
as a decimal integer, re-express it in base 16, then read the hex as ASCII.
Here we try that and its neighbours on the still-unsolved runs.
"""
import string

def to_int(s, digits):
    v = 0
    b = len(digits)
    for ch in s:
        v = v * b + digits.index(ch)
    return v

def as_bytes(v):
    h = f"{v:x}"
    if len(h) % 2:
        h = "0" + h
    return bytes.fromhex(h)

def score(bs):
    if not bs:
        return 0.0
    good = sum(1 for b in bs if 32 <= b < 127)
    return good / len(bs)

MAPS = {
    "a=1..i=9,o=0":  "oabcdefghi",          # value = index, so a->1 ... i->9, o->0
    "a=0..i=8":      "abcdefghi",
    "a=1..i=9(b9)":  "iabcdefgh",           # bijective-ish: i wraps to 0
    "a=0..i=8,o=9":  "abcdefghio",
}

def report(name, s):
    print(f"\n===== {name} (len {len(s)}) =====")
    for label, digits in MAPS.items():
        if not set(s) <= set(digits):
            continue
        for rev in (False, True):
            t = s[::-1] if rev else s
            v = to_int(t, digits)
            for how, bs in (("int->bytes", as_bytes(v)),
                            ("decimal-digits->hex->bytes",
                             as_bytes(int(str(v), 16)) if set(str(v)) <= set("0123456789abcdef") else b"")):
                sc = score(bs)
                if sc > 0.85:
                    print(f"  [{label}]{' rev' if rev else ''} {how}: score={sc:.2f}")
                    print(f"    {bs!r}")
    print("  (nothing above 0.85 printable unless shown)")

if __name__ == "__main__":
    for f in ("partA.txt", "partC.txt"):
        report(f, open(f).read().strip())
