"""partA as a running key over partC -- correctly filtered this time.

Round 6's sweep was vacuous: it demanded the first two decoded bytes be
lowercase, which is structurally impossible at 570 digits. There is no cheap
sound prefilter for a whole-decode criterion, so this pays the full bignum and
scores the ENTIRE decode, exactly as digitmap.py did.

Every alphabet ordering, every key the 7x13 grid offers, three combining ops,
partC forwards and reversed.
"""
import itertools, sys, time

A = open("partA.txt").read().strip()
C = open("partC.txt").read().strip()
ROWS = [A[i*13:(i+1)*13] for i in range(7)]
COLS = [''.join(r[i] for r in ROWS) for i in range(13)]
KEYS = ([(f"row{i}", r) for i, r in enumerate(ROWS)]
        + [(f"col{i}", c) for i, c in enumerate(COLS)]
        + [("partA", A), ("partA-rev", A[::-1]), ("colread", ''.join(COLS))])
OPS = (("c-k", lambda c, k: (c - k) % 9),
       ("c+k", lambda c, k: (c + k) % 9),
       ("k-c", lambda c, k: (k - c) % 9))
LOWER = set(range(97, 123))
THRESH = 0.75

t0 = time.time(); n = 0; best = (0.0, None)
for perm in itertools.permutations("abcdefghi"):
    idx = {c: i for i, c in enumerate(perm)}
    for tname, ct in (("partC", C), ("partC-rev", C[::-1])):
        ci = [idx[c] for c in ct]
        for kname, key in KEYS:
            kl = len(key)
            ki = [idx[key[i % kl]] for i in range(len(ct))]
            for oname, f in OPS:
                n += 1
                num = 0
                for c, k in zip(ci, ki):
                    num = num * 10 + f(c, k) + 1
                h = f"{num:x}"
                if len(h) % 2: h = "0" + h
                bs = bytes.fromhex(h)
                low = sum(1 for b in bs if b in LOWER) / len(bs)
                if low > best[0]:
                    best = (low, (kname, oname, tname, ''.join(perm)))
                if low >= THRESH:
                    print(f"*** map={''.join(perm)} key={kname} op={oname} "
                          f"target={tname} lower={low:.0%}\n    {bs[:200]!r}", flush=True)
    if n % 200000 < 132:
        print(f"  {n:,} tested, {time.time()-t0:.0f}s, best {best[0]:.1%} {best[1]}",
              file=sys.stderr, flush=True)
print(f"[running-key v2] {n:,} combinations in {time.time()-t0:.0f}s, "
      f"best lowercase fraction {best[0]:.1%} at {best[1]}")
