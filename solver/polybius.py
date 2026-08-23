"""Is partC a 9x9 Polybius / coordinate-pair encoding?

570 symbols over a-i splits into 285 pairs. If each pair is (row, col) in a 9x9
square then the plaintext is 285 characters. The simplest square -- cells filled
in order from some ASCII offset -- is only 380 tests, so try it exhaustively
before assuming a keyed one.
"""
from english import score

C = open('partC.txt').read().strip()
results = []
for align in (0, 1):
    pairs = [C[i:i + 2] for i in range(align, len(C) - 1, 2)]
    for order in ("rc", "cr"):
        vals = []
        for p in pairs:
            a, b = (ord(p[0]) - 97, ord(p[1]) - 97)
            vals.append(a * 9 + b if order == "rc" else b * 9 + a)
        for off in range(0, 200):
            txt = ''.join(chr(v + off) if 32 <= v + off < 127 else '?' for v in vals)
            if '?' in txt:
                continue
            results.append((score(txt), align, order, off, txt))

results.sort(reverse=True)
print(f"{len(results)} viable offset mappings tested")
for sc, align, order, off, txt in results[:5]:
    print(f"\nscore={sc:8.1f} align={align} order={order} offset={off}")
    print("  " + txt[:120])
