"""partA keying partC, over every alphabet ordering.

running.py tested 138 keyed streams under the natural a=1..i=9. But the mod-9
arithmetic and the decode convention both depend on which letter is which digit,
and digitmap.py already established that the mapping need not be alphabetical.
This sweeps all 9! orderings against every key the 7x13 grid offers, using
fastdecode.py to skip the bignum on the ~99.5% that cannot be text.
"""
import itertools, sys, time
from fastdecode import leading_bytes, is_lower
from running import convention

A = open('partA.txt').read().strip()
C = open('partC.txt').read().strip()
ROWS = [A[i * 13:(i + 1) * 13] for i in range(7)]
COLS = [''.join(r[i] for r in ROWS) for i in range(13)]
KEYS = ([(f"row{i}", r) for i, r in enumerate(ROWS)]
        + [(f"col{i}", c) for i, c in enumerate(COLS)]
        + [("partA", A), ("partA-rev", A[::-1]), ("colread", ''.join(COLS))])
TARGETS = (("partC", C), ("partC-rev", C[::-1]))
OPS = (("c-k", lambda c, k: (c - k) % 9),
       ("c+k", lambda c, k: (c + k) % 9),
       ("k-c", lambda c, k: (k - c) % 9))
PREFIX = 30

t0 = time.time()
n = survived = hits = 0
for perm in itertools.permutations("abcdefghi"):
    idx = {c: i for i, c in enumerate(perm)}
    for tname, ct in TARGETS:
        ci = [idx[c] for c in ct[:PREFIX]]
        for kname, key in KEYS:
            ki = [idx[key[i % len(key)]] for i in range(PREFIX)]
            for oname, f in OPS:
                n += 1
                pre = ''.join(str(f(c, k) + 1) for c, k in zip(ci, ki))
                lb = leading_bytes(pre, len(ct))
                if lb is None or not (is_lower(lb[0]) and is_lower(lb[1])):
                    continue
                survived += 1
                full = ''.join(
                    perm[f(idx[ct[i]], idx[key[i % len(key)]])] for i in range(len(ct)))
                bs = convention(full)
                if not bs:
                    continue
                frac = sum(1 for b in bs if 97 <= b <= 122) / len(bs)
                if frac >= 0.75:
                    hits += 1
                    print(f"!!! map={''.join(perm)} key={kname} op={oname} "
                          f"target={tname} lower={frac:.0%}\n    {bs[:200]!r}", flush=True)
    if n % 5000000 < 132:
        print(f"  {n:,} tested, {survived:,} past filter, {hits} hits, "
              f"{time.time()-t0:.0f}s", file=sys.stderr, flush=True)
print(f"[running-key] {n:,} combinations, {survived:,} past the fast filter "
      f"({survived/max(n,1):.2%}), {hits} decodes above 75% lowercase, "
      f"{time.time()-t0:.0f}s")
