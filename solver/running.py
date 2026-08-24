"""partA keying partC.

"Seven intertwined passwords" need not mean seven passwords for the blobs --
every derivation of that kind is now exhausted and negative. The other reading
is that the seven rows key the cipher, and partC is what they decrypt.

partA and partC are over the same 9-symbol alphabet, so combining them digitwise
mod 9 is the natural operation: a Vigenere/Beaufort over base 9, with partA
(91 symbols) or one of its 13-symbol rows as the key.

The test on the result is the puzzle's own decode convention -- digits, decimal,
base 16, ASCII -- which is what produced every solved run in this block.
"""
import itertools

LETTERS = "abcdefghi"
A = open('partA.txt').read().strip()
C = open('partC.txt').read().strip()
LOWER = set(range(ord('a'), ord('z') + 1))

ROWS = [A[i * 13:(i + 1) * 13] for i in range(7)]
COLS = [''.join(r[i] for r in ROWS) for i in range(13)]
KEYS = ([(f"row{i}", r) for i, r in enumerate(ROWS)]
        + [(f"col{i}", c) for i, c in enumerate(COLS)]
        + [("partA", A), ("partA-rev", A[::-1]),
           ("partA-colread", ''.join(COLS))])

OPS = {
    "c-k": lambda c, k: (c - k) % 9,
    "c+k": lambda c, k: (c + k) % 9,
    "k-c": lambda c, k: (k - c) % 9,          # Beaufort
}


def combine(ct, key, op):
    f = OPS[op]
    out = []
    for i, ch in enumerate(ct):
        c = LETTERS.index(ch)
        k = LETTERS.index(key[i % len(key)])
        out.append(LETTERS[f(c, k)])
    return ''.join(out)


def convention(s):
    """letters -> digits 1..9 -> decimal int -> base 16 -> bytes"""
    n = int(''.join(str(LETTERS.index(c) + 1) for c in s))
    h = f"{n:x}"
    if len(h) % 2:
        h = '0' + h
    try:
        return bytes.fromhex(h)
    except ValueError:
        return b''


if __name__ == "__main__":
    results = []
    for kname, key in KEYS:
        for op in OPS:
            for target, tname in ((C, "partC"), (C[::-1], "partC-rev")):
                s = combine(target, key, op)
                bs = convention(s)
                if not bs:
                    continue
                frac = sum(1 for b in bs if b in LOWER) / len(bs)
                results.append((frac, kname, op, tname, bs))

    results.sort(reverse=True)
    print(f"{len(results)} keyed streams tested (natural mapping a=1..i=9)")
    for frac, kname, op, tname, bs in results[:6]:
        print(f"  {frac:5.1%}  key={kname:14s} op={op:4s} target={tname}")
        print(f"         {bs[:90]!r}")
    print(f"\nbest lowercase fraction: {results[0][0]:.1%} "
          f"(a real decode is ~100%, cf. digitmap.py's 75% threshold)")
