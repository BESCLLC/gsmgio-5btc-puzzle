"""English-likeness score.

Delegates to wordscore: letter-frequency scoring was actively misleading here --
a decode that is nothing but high-frequency letters passes chi-square while
containing no words at all, which is exactly the false positive the first pass
at the checkerboard search produced. Word segmentation does not have that
failure mode.

Calibration: known puzzle plaintexts 0.33-0.43, an ETAOIN wall 0.16, random
letters 0.08. Treat anything below ~0.28 as noise.
"""
from wordscore import score, segment  # noqa: F401

THRESHOLD = 0.28
