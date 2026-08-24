"""BNCC-8B-style fractionation for a 9-symbol alphabet.

Part 8B of the 2020 National Cipher Challenge takes 5 Baudot characters, writes
them as a 5x5 bit matrix, rotates it 90 degrees and reads the rows back. The
radix analogue here is exact: 9 = 3^2, so one symbol is two trits, two symbols
make a 2x2 trit matrix, and the dihedral symmetries of that matrix are the
transform family.

The A[i]/C[i] pairing this was proposed with does not exist -- partA is 91
symbols and partC is 570 -- so pairs are taken within each run, and the cross
readings are included as variants.

Judged downstream, not by English: each output stream is tried as a password
against the four real blobs under the puzzle's KDF convention.
"""
ALPHA = "abcdefghi"


def to_trits(c, hi_first=True):
    v = ALPHA.index(c)
    a, b = divmod(v, 3)
    return (a, b) if hi_first else (b, a)


def from_trits(t, hi_first=True):
    a, b = t if hi_first else (t[1], t[0])
    return ALPHA[a * 3 + b]


# the eight dihedral symmetries of [[p,q],[r,s]]
D4 = {
    "identity":  lambda p, q, r, s: (p, q, r, s),
    "rot90cw":   lambda p, q, r, s: (r, p, s, q),
    "rot180":    lambda p, q, r, s: (s, r, q, p),
    "rot90ccw":  lambda p, q, r, s: (q, s, p, r),
    "transpose": lambda p, q, r, s: (p, r, q, s),
    "antitrans": lambda p, q, r, s: (s, q, r, p),
    "flipcols":  lambda p, q, r, s: (q, p, s, r),
    "fliprows":  lambda p, q, r, s: (r, s, p, q),
}


def transform(pairs, op, hi_first=True):
    """pairs: iterable of (symbol, symbol) -> output symbol string"""
    f = D4[op]
    out = []
    for x, y in pairs:
        p, q = to_trits(x, hi_first)
        r, s = to_trits(y, hi_first)
        a, b, c, d = f(p, q, r, s)
        out.append(from_trits((a, b), hi_first))
        out.append(from_trits((c, d), hi_first))
    return "".join(out)


def consecutive(s):
    return [(s[i], s[i + 1]) for i in range(0, len(s) - 1, 2)]


def aligned(x, y):
    n = min(len(x), len(y))
    return [(x[i], y[i]) for i in range(n)]
