"""partA as a 7 x 13 grid.

91 = 7 x 13, and the phase-3.2 plaintext threatens "SEVEN INTERTWINED
PASSWORDS". If partA is seven 13-digit passwords, then the thing to try is not
partA as one string -- which hashtheruns.py already exhausted -- but its rows:
individually, in every order, interleaved, and via their sums.
"""
import hashlib, itertools

LET2DIG = {c: str(i + 1) for i, c in enumerate("abcdefghi")}


def grid(s, ncols):
    return [s[i:i + ncols] for i in range(0, len(s), ncols)]


def digits(row):
    return ''.join(LET2DIG[c] for c in row)


def joins(nums):
    yield ''.join(map(str, nums))
    yield ','.join(map(str, nums))
    yield '-'.join(map(str, nums))
    yield str(sum(nums))


def derived(s, ncols, tag):
    """Everything a rectangular reading of s offers up."""
    rows = grid(s, ncols)
    if len(rows[-1]) != ncols:
        return
    drows = [digits(r) for r in rows]
    cols = [''.join(r[i] for r in rows) for i in range(ncols)]
    dcols = [digits(c) for c in cols]

    for i, d in enumerate(drows):
        yield f"{tag}row{i}", d
        yield f"{tag}row{i}-letters", rows[i]
        yield f"{tag}row{i}-upper", rows[i].upper()
    for i, d in enumerate(dcols):
        yield f"{tag}col{i}", d

    yield f"{tag}colread", ''.join(dcols)
    yield f"{tag}colread-letters", ''.join(cols)
    yield f"{tag}rowread", ''.join(drows)

    rs = [sum(int(c) for c in d) for d in drows]
    cs = [sum(int(c) for c in d) for d in dcols]
    for j, v in enumerate(joins(rs)):
        yield f"{tag}rowsums{j}", v
    for j, v in enumerate(joins(cs)):
        yield f"{tag}colsums{j}", v
    yield f"{tag}rowsums+colsums", ''.join(map(str, rs)) + ''.join(map(str, cs))
    yield f"{tag}colsums+rowsums", ''.join(map(str, cs)) + ''.join(map(str, rs))

    # the "seven intertwined passwords" reading: every order of the rows
    if len(rows) <= 8:
        for perm in itertools.permutations(range(len(rows))):
            yield f"{tag}perm", ''.join(drows[i] for i in perm)
            yield f"{tag}perm-letters", ''.join(rows[i] for i in perm)
        # each row hashed, then chained / xored -- "intertwined", not concatenated
        hs = [hashlib.sha256(d.encode()).digest() for d in drows]
        acc = bytes(32)
        for h in hs:
            acc = bytes(a ^ b for a, b in zip(acc, h))
        yield f"{tag}xor-of-rowhashes", acc.hex()
        chain = ""
        for d in drows:
            chain = hashlib.sha256((chain + d).encode()).hexdigest()
        yield f"{tag}chained-rowhashes", chain
        yield f"{tag}concat-rowhashes", ''.join(
            hashlib.sha256(d.encode()).hexdigest() for d in drows)


def all_candidates():
    A = open('partA.txt').read().strip()
    C = open('partC.txt').read().strip()
    yield from derived(A, 13, "A7x13.")
    yield from derived(A, 7, "A13x7.")
    for n in (19, 30, 15, 38, 10, 57, 6, 95, 5, 114, 3, 190, 2, 285):
        yield from derived(C, n, f"C{570//n}x{n}.")
