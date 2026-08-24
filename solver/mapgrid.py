"""The 7x13 grid derivations under every digit assignment.

run_grid.py tested the grid readings with the obvious a=1..i=9. But digitmap.py
already showed the mapping need not be alphabetical, and the grid derivations
that depend on digit *values* -- the sums, the column read -- change completely
under a different assignment. hashtheruns.py covered partA as one string; it did
not cover its rows, columns or sums. This does.
"""
import hashlib, itertools, sys
import validate
from sweep import plausible
from pagehash import BLOBS

A = open('partA.txt').read().strip()
LETTERS = "abcdefghi"
ROWS = [A[i * 13:(i + 1) * 13] for i in range(7)]
COLS = [''.join(r[i] for r in ROWS) for i in range(13)]


def forms(m):
    drows = [''.join(m[c] for c in r) for r in ROWS]
    dcols = [''.join(m[c] for c in c_) for c_ in COLS]
    rs = [sum(int(x) for x in d) for d in drows]
    cs = [sum(int(x) for x in d) for d in dcols]
    yield "colread", ''.join(dcols)
    yield "rowsums", ''.join(map(str, rs))
    yield "colsums", ''.join(map(str, cs))
    yield "rowsums+colsums", ''.join(map(str, rs)) + ''.join(map(str, cs))
    acc = bytes(32)
    for d in drows:
        acc = bytes(a ^ b for a, b in
                    zip(acc, hashlib.sha256(d.encode()).digest()))
    yield "xor-of-rowhashes", acc.hex()


n = hits = 0
for digitset in ("123456789", "012345678"):
    for perm in itertools.permutations(digitset):
        m = dict(zip(LETTERS, perm))
        for fname, base in forms(m):
            h1 = hashlib.sha256(base.encode()).hexdigest()
            for pname, pw in (("sha256", h1),
                              ("sha256^2", hashlib.sha256(h1.encode()).hexdigest())):
                for md in ("md5", "sha256"):
                    for bname, blob in BLOBS.items():
                        n += 1
                        pt = blob.check(pw, md)
                        if pt is not None and plausible(pt):
                            hits += 1
                            print(f"!!! HIT blob={bname} form={fname} "
                                  f"map={''.join(perm)} pw={pname} kdf={md}\n"
                                  f"    base={base[:80]}\n    {pt[:200]!r}", flush=True)
                            for key, addr in validate.check(pt):
                                print(f"    *** PRIZE ADDRESS {addr} <- {key}", flush=True)
print(f"[mapgrid] {n:,} decryptions, {hits} plausible plaintexts")
