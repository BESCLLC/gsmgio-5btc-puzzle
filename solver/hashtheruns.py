"""'Our first hint is your last command' -> HASHTHETEXT.

pagehash.py tested that on the page as a whole. But the two undecoded runs are
themselves 'the text', and if their digit mapping is non-alphabetical then the
string to hash is the mapped decimal form, not the letters. That is 9! mappings
x the natural pieces -- a space nothing has covered, and cheap enough to just do.
"""
import hashlib, itertools, sys
import validate
from sweep import plausible
from pagehash import BLOBS

A = open('partA.txt').read().strip()
C = open('partC.txt').read().strip()
LETTERS = "abcdefghi"
PIECES = [("partA", A), ("partC", C), ("partA+partC", A + C), ("partC+partA", C + A)]

n = hits = 0
for digits in ("123456789", "012345678"):
    for perm in itertools.permutations(digits):
        m = dict(zip(LETTERS, perm))
        for pname, s in PIECES:
            d = ''.join(m[c] for c in s)
            h1 = hashlib.sha256(d.encode()).hexdigest()
            for fname, pw in (("sha256", h1),
                              ("sha256^2", hashlib.sha256(h1.encode()).hexdigest())):
                for md in ("md5", "sha256"):
                    for bname, blob in BLOBS.items():
                        n += 1
                        pt = blob.check(pw, md)
                        if pt is not None and plausible(pt):
                            hits += 1
                            print(f"!!! HIT blob={bname} piece={pname} map={''.join(perm)} "
                                  f"form={fname} kdf={md}\n    {pt[:200]!r}", flush=True)
                            for key, addr in validate.check(pt):
                                print(f"    *** PRIZE ADDRESS {addr} <- {key}", flush=True)
        if n % 2000000 < 32:
            print(f"  ... {n:,} decryptions, {hits} hits", file=sys.stderr, flush=True)
print(f"[hash-the-runs] {n:,} decryptions, {hits} plausible plaintexts")
