"""Chunked decode, every digit mapping, every chunk size.

Cheap because the first chunk decides it: if the leading chunk does not decode
to lowercase letters, no mapping/size pair is worth finishing. One small bignum
per candidate instead of one per chunk.
"""
import itertools, sys, time
from chunked import decode_chunk, decode_chunks, LETTERS
from english import score, segment

LOWER = set(range(97, 123))
SIZES = range(2, 61)


def hunt(name, s, minbytes=3):
    print(f"\n=== {name}: {len(s)} symbols ===", flush=True)
    t0 = n = 0
    t0 = time.time()
    found = []
    for digitset in ("123456789", "012345678"):
        for perm in itertools.permutations(digitset):
            m = dict(zip(LETTERS, perm))
            for k in SIZES:
                n += 1
                first = decode_chunk(s[:k], m)
                if len(first) < minbytes or not all(b in LOWER for b in first):
                    continue
                full = decode_chunks(s, k, m)
                if not full:
                    continue
                frac = sum(1 for b in full if b in LOWER) / len(full)
                if frac < 0.9:
                    continue
                txt = full.decode('latin-1')
                found.append((score(txt), frac, k, ''.join(perm), txt))
    found.sort(reverse=True)
    print(f"  {n:,} (mapping, chunk-size) pairs in {time.time()-t0:.0f}s; "
          f"{len(found)} decoded >=90% lowercase throughout", flush=True)
    for sc, frac, k, perm, txt in found[:10]:
        print(f"  wordscore={sc:.3f} lower={frac:.0%} chunk={k} map={perm}")
        print(f"      {txt[:100]!r}")
        print(f"      {segment(txt)[:100]}")
    return found


if __name__ == "__main__":
    A = open('partA.txt').read().strip()
    C = open('partC.txt').read().strip()
    hunt("partA", A)
    hunt("partC", C)
