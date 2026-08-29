"""'Prime numbers are required to proceed. Some characters need to be zeroed out.'

partA and partC use a-i only. The z-segments that decoded use a-i AND 'o' = 0.
So the missing zeros are the point, and the creator's hint says primes decide
which characters become them.

Decode after zeroing with the block's own convention: digits -> decimal integer
-> base 16 -> ASCII, the operation that produced lastwordsbeforearchichoice.
"""
import itertools
from wordscore import score, segment

LOWER = set(range(97, 123))
PRINTABLE = set(range(32, 127))


def primes_to(n):
    s = [True] * (n + 1)
    s[0] = s[1] = False
    for i in range(2, int(n ** .5) + 1):
        if s[i]:
            for j in range(i * i, n + 1, i):
                s[j] = False
    return {i for i, v in enumerate(s) if v}


def digits_of(s, mapping):
    return [mapping[c] for c in s]


def apply_rule(dig, rule, P):
    """rule -> new digit list, with some entries zeroed or dropped."""
    out = []
    for i, d in enumerate(dig):
        pos1, pos0 = i + 1, i
        hit = {
            "pos1-prime":      pos1 in P,
            "pos0-prime":      pos0 in P,
            "pos1-composite":  pos1 not in P,
            "val-prime":       d in (2, 3, 5, 7),
            "val-composite":   d not in (2, 3, 5, 7),
        }[rule[0]]
        if hit:
            if rule[1] == "zero":
                out.append(0)
            # "drop" -> omit entirely
        else:
            out.append(d)
    return out


def decode(dig):
    n = 0
    for d in dig:
        n = n * 10 + d
    if n == 0:
        return b""
    h = f"{n:x}"
    if len(h) % 2:
        h = "0" + h
    try:
        return bytes.fromhex(h)
    except ValueError:
        return b""


RULES = [(w, a) for w in ("pos1-prime", "pos0-prime", "pos1-composite",
                          "val-prime", "val-composite")
         for a in ("zero", "drop")]

if __name__ == "__main__":
    P = primes_to(1000)
    natural = {c: i + 1 for i, c in enumerate("abcdefghi")}
    for name in ("partA", "partC"):
        s = open(f"{name}.txt").read().strip()
        print(f"\n===== {name} ({len(s)} symbols) =====")
        results = []
        for rule in RULES:
            dig = apply_rule(digits_of(s, natural), rule, P)
            bs = decode(dig)
            if len(bs) < 4:
                continue
            low = sum(1 for b in bs if b in LOWER) / len(bs)
            pr = sum(1 for b in bs if b in PRINTABLE) / len(bs)
            results.append((low, pr, len(bs), rule, bs))
        results.sort(reverse=True)
        for low, pr, n, rule, bs in results[:6]:
            print(f"  {rule[0]:15s} {rule[1]:5s} -> {n:4d}B  lower {low:5.1%}  "
                  f"printable {pr:5.1%}")
            print(f"      {bs[:70]!r}")
