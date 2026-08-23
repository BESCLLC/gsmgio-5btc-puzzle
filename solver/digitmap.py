"""The z-segments decoded as: letters -> digits -> decimal integer -> base 16 ->
ASCII, with the obvious mapping a=1..i=9, o=0. partA and partC refuse that
mapping -- but nothing says the mapping has to be alphabetical.

There are only 9! = 362,880 ways to assign digits to a-i, so try all of them
under both digit sets and see if any produces text. The known answers
("lastwordsbeforearchichoice", "thispassword") were pure lowercase letters, so
that is the filter: it is tight enough that a false positive is very unlikely.
"""
import itertools, sys

LOWER = set(range(ord('a'), ord('z') + 1))


def decode(s, mapping):
    """mapping: dict letter -> digit character."""
    n = int(''.join(mapping[c] for c in s))
    h = f"{n:x}"
    if len(h) % 2:
        h = '0' + h
    try:
        return bytes.fromhex(h)
    except ValueError:
        return b''


def hunt(name, s, digit_sets=("123456789", "012345678"), thresh=0.75):
    letters = sorted(set(s))
    print(f"\n=== {name}: {len(s)} symbols over {''.join(letters)} ===")
    best = []
    tried = 0
    for digits in digit_sets:
        for perm in itertools.permutations(digits, len(letters)):
            tried += 1
            mapping = dict(zip(letters, perm))
            bs = decode(s, mapping)
            if not bs:
                continue
            frac = sum(1 for b in bs if b in LOWER) / len(bs)
            if frac >= thresh:
                best.append((frac, digits, ''.join(perm), bs))
    best.sort(reverse=True)
    print(f"tried {tried:,} digit assignments; {len(best)} above {thresh:.0%} lowercase")
    for frac, digits, perm, bs in best[:8]:
        print(f"  {frac:.0%}  {''.join(letters)} -> {perm}  ({digits})")
        print(f"      {bs[:120]!r}")
    return best


if __name__ == "__main__":
    hunt("partA", open('partA.txt').read().strip())
    hunt("partC", open('partC.txt').read().strip())
