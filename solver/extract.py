"""Pull the SalPhaseIon symbol stream out of the README and segment it.

Writes partA.txt / partC.txt (the two runs nobody has decoded) for the other
scripts to work on.
"""
import re
from collections import Counter


def stream():
    txt = open('../README.md').read()
    start = txt.index('## Salphaseion')
    block = txt[start:start + txt[start:].index('The two "abba" sections')]
    line = [l for l in block.splitlines() if l.startswith('> ')][0]
    toks = line[2:].replace('**', '').split()
    assert all(len(t) == 1 for t in toks), [t for t in toks if len(t) != 1]
    return ''.join(toks)


def segments():
    """-> (partA, matrixsumlist_bits, partC, [z-separated tails], trailer)"""
    s = stream()
    head, *tails = s.split('z')
    a, b = next(re.finditer(r'[ab]{40,}', head)).span()
    return head[:a], head[a:b], head[b:], tails[:-1], tails[-1]


def bits_to_text(run):
    b = run.replace('a', '0').replace('b', '1')
    return ''.join(chr(int(b[i:i + 8], 2)) for i in range(0, len(b), 8))


if __name__ == '__main__':
    s = stream()
    print(f"full stream: {len(s)} symbols, alphabet {''.join(sorted(set(s)))}")
    partA, abba, partC, tails, trailer = segments()

    print(f"\npartA   : {len(partA)} symbols over {''.join(sorted(set(partA)))}  [UNDECODED]")
    print(partA)
    print(f"\nabba run: {len(abba)} bits -> {bits_to_text(abba)!r}")
    print(f"\npartC   : {len(partC)} symbols over {''.join(sorted(set(partC)))}  [UNDECODED]")
    print(partC)
    for i, t in enumerate(tails):
        print(f"\nz-tail {i}: {len(t)} symbols -> see numeric.py")
        print(t)
    print(f"\ntrailer : {trailer}")

    open('partA.txt', 'w').write(partA)
    open('partC.txt', 'w').write(partC)
    print("\nwrote partA.txt, partC.txt")
