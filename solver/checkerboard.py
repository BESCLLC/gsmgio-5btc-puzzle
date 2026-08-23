"""Straddling checkerboard / VIC.

Phase 3.2.2 of this puzzle was already a VIC cipher: a digit stream decoded
against a keyed 28-symbol alphabet (FUBCDORA.LETHINGKYMVPS.JQZXW) with rows 1
and 4 as the two-digit rows. partC is a digit stream over 1-9 with a
conspicuously absent 0 -- which is exactly what a checkerboard looks like when
one single-digit letter never occurs in the plaintext. So try the puzzle's own
alphabet first, then every row pair, then the other keyed alphabets it has used.
"""
import itertools
from english import score

VIC_ALPHABET = "FUBCDORA.LETHINGKYMVPS.JQZXW"      # from phase 3.2.2


def board(alphabet, d1, d2):
    """-> dict of digit-string -> symbol"""
    singles = [d for d in "0123456789" if d not in (str(d1), str(d2))]
    t = {}
    a = list(alphabet)
    for d in singles:
        t[d] = a.pop(0)
    for row in (d1, d2):
        for d in "0123456789":
            if a:
                t[f"{row}{d}"] = a.pop(0)
    return t


def decode(digits, table, d1, d2):
    out, i = [], 0
    while i < len(digits):
        c = digits[i]
        if c in (str(d1), str(d2)):
            if i + 1 >= len(digits):
                break
            out.append(table.get(digits[i:i + 2], '?'))
            i += 2
        else:
            out.append(table.get(c, '?'))
            i += 1
    return ''.join(out)


def hunt(name, symbols, alphabets, digit_maps):
    print(f"\n=== {name} ===")
    results = []
    for aname, alpha in alphabets:
        for mname, dmap in digit_maps:
            digits = ''.join(dmap[c] for c in symbols)
            for d1, d2 in itertools.permutations(range(10), 2):
                t = board(alpha, d1, d2)
                txt = decode(digits, t, d1, d2)
                if '?' in txt:
                    continue
                results.append((score(txt), aname, mname, d1, d2, txt))
    results.sort(reverse=True)
    print(f"{len(results)} clean decodes")
    for sc, aname, mname, d1, d2, txt in results[:6]:
        print(f"  score={sc:8.1f} alphabet={aname} map={mname} rows=({d1},{d2})")
        print(f"    {txt[:110]}")
    return results


if __name__ == "__main__":
    C = open('partC.txt').read().strip()
    A = open('partA.txt').read().strip()
    maps = [("a=1..i=9", {c: str(i + 1) for i, c in enumerate("abcdefghi")}),
            ("a=0..i=8", {c: str(i) for i, c in enumerate("abcdefghi")}),
            ("a=9..i=1", {c: str(9 - i) for i, c in enumerate("abcdefghi")})]
    alphabets = [("VIC phase3.2.2", VIC_ALPHABET),
                 ("plain", "ABCDEFGHIJKLMNOPQRSTUVWXYZ.."),
                 ("etaoin", "ETAOINSRHDLUCMFYWGPBVKXJQZ..")]
    hunt("partC", C, alphabets, maps)
    hunt("partA", A, alphabets, maps)
