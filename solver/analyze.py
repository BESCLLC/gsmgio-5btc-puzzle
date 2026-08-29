"""Structural analysis of the undecoded 570-symbol SalPhaseIon segment."""
from collections import Counter

C = open('partC.txt').read().strip()
A = open('partA.txt').read().strip()

def stats(name, s):
    n = len(s)
    f = Counter(s)
    ic = sum(v * (v - 1) for v in f.values()) / (n * (n - 1))
    print(f"\n== {name}: n={n} alphabet={''.join(sorted(f))} IC={ic:.4f} "
          f"(flat 9-symbol = {1/9:.4f})")
    print("   freq:", sorted(f.items(), key=lambda kv: -kv[1]))
    for off in (0, 1):
        sub = s[off::2]
        fo = Counter(sub)
        print(f"   pos%2=={off}: " + " ".join(f"{k}{v}" for k, v in sorted(fo.items())))

stats("partA", A)
stats("partC", C)

# repeated n-grams: a giveaway for polygraphic / Polybius structure
for n in (3, 4, 5, 6):
    f = Counter(C[i:i+n] for i in range(len(C)-n+1))
    rep = [(k, v) for k, v in f.items() if v > 1]
    print(f"\nrepeated {n}-grams in partC: {len(rep)} -> {sorted(rep, key=lambda kv:-kv[1])[:8]}")
