"""The decode convention, applied in chunks.

A structural fact nobody seems to have noticed: under this block's own decode
convention (digits -> decimal integer -> base 16 -> ASCII), the first byte of
the result is *not free*. It is fixed by the digit count.

    570 digits -> first byte can only be 5..45     -- never a letter
     91 digits -> first byte can only be 8..78     -- never a letter
     63 digits -> reaches 1..255                   -- 'lastwordsbeforearchichoice'
     29 digits -> reaches 1..255                   -- 'thispassword'

The two segments that solved are short. partA and partC, read as one number
each, *cannot* begin with a letter no matter what the digit mapping is. So the
whole-string reading was never viable -- they have to be chunked, exactly like
the z-separated segments were, and partA/partC simply carry no 'z'.
"""
from english import score, segment

LETTERS = "abcdefghi"


def decode_chunk(chunk, m):
    n = int(''.join(m[c] for c in chunk))
    h = f"{n:x}"
    if len(h) % 2:
        h = '0' + h
    try:
        return bytes.fromhex(h)
    except ValueError:
        return b''


def decode_chunks(s, k, m):
    out = []
    for i in range(0, len(s) - k + 1, k):
        b = decode_chunk(s[i:i + k], m)
        if not b:
            return None
        out.append(b)
    return b''.join(out)


if __name__ == "__main__":
    natural = {c: str(i + 1) for i, c in enumerate(LETTERS)}
    for name in ("partA", "partC"):
        s = open(f"{name}.txt").read().strip()
        print(f"\n=== {name} ({len(s)} symbols), natural mapping, chunked ===")
        best = []
        for k in range(2, 61):
            bs = decode_chunks(s, k, natural)
            if not bs:
                continue
            txt = bs.decode('latin-1')
            printable = sum(1 for b in bs if 32 <= b < 127) / len(bs)
            best.append((score(txt), printable, k, txt))
        best.sort(reverse=True)
        for sc, pr, k, txt in best[:5]:
            print(f"  chunk={k:2d}  wordscore={sc:.3f}  printable={pr:.0%}")
            print(f"      {txt[:90]!r}")
