"""Cheap English-likeness score. A real cipher break screams; this only has to
be loud enough to hear it over noise."""
import math
from collections import Counter

FREQ = dict(zip("etaoinshrdlcumwfgypbvkjxqz",
                [12.7,9.1,8.2,7.5,7.0,6.7,6.3,6.1,6.0,4.3,4.0,2.8,2.8,2.4,
                 2.4,2.2,2.0,2.0,1.9,1.5,1.0,0.8,0.15,0.15,0.10,0.07]))
COMMON = ("the and ing ion tio ent for her ter hat tha ere ate his con res "
          "ver all ons nce men ith ted ers pro thi wit are ess not ive out "
          "eve red cti ted sta ted est ate all int our you key priv bitcoin "
          "address wallet matrix choice answer password").split()


def score(s):
    s = ''.join(c for c in s.lower() if c.isalpha() or c == ' ')
    if len(s) < 20:
        return -1e9
    letters = [c for c in s if c.isalpha()]
    if not letters:
        return -1e9
    n = len(letters)
    f = Counter(letters)
    # chi-square against English letter frequencies, lower is better
    chi = sum((f.get(c, 0) - FREQ[c] * n / 100) ** 2 / max(FREQ[c] * n / 100, 1e-9)
              for c in FREQ)
    hits = sum(s.count(w) * len(w) for w in COMMON)
    return hits * 40 - chi
